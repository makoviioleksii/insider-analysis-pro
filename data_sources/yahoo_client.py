import yfinance as yf
import pandas as pd
from typing import Dict, Any, List, Optional
from data_sources.base_client import BaseDataClient
from utils.logging_config import logger
from utils.cache_manager import cache_manager

class YahooFinanceClient(BaseDataClient):
    """Yahoo Finance data client"""
    
    def __init__(self):
        super().__init__("YahooFinance")
    
    async def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch stock data from Yahoo Finance"""
        if not self.validate_ticker(ticker):
            logger.warning(f"Invalid ticker format: {ticker}")
            return {}
        
        # Check cache first
        cached_data = cache_manager.load_cache(ticker, "yahoo", ttl_seconds=3600)
        if cached_data:
            return cached_data
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info.get('regularMarketPrice') and not info.get('symbol'):
                logger.warning(f"No valid data for {ticker} from Yahoo Finance")
                return {}
            
            # Get historical data for technical analysis
            hist = stock.history(period="1y")
            
            data = {
                'info': info,
                'history': hist.to_dict() if not hist.empty else {},
                'ticker': ticker
            }
            
            # Cache the data
            cache_manager.save_cache(ticker, data, "yahoo")
            logger.info(f"Successfully fetched Yahoo Finance data for {ticker}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch Yahoo Finance data for {ticker}: {e}")
            return {}
    
    async def fetch_multiple_stocks(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch data for multiple stocks"""
        results = {}
        
        # Validate tickers
        valid_tickers = [t for t in tickers if self.validate_ticker(t)]
        
        if not valid_tickers:
            logger.warning("No valid tickers provided")
            return results
        
        try:
            # Use yfinance's ability to fetch multiple tickers at once
            tickers_str = " ".join(valid_tickers)
            data = yf.download(tickers_str, period="1y", group_by='ticker', progress=False)
            
            for ticker in valid_tickers:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    ticker_data = {
                        'info': info,
                        'history': data[ticker].to_dict() if ticker in data.columns.levels[0] else {},
                        'ticker': ticker
                    }
                    
                    results[ticker] = ticker_data
                    cache_manager.save_cache(ticker, ticker_data, "yahoo")
                    
                except Exception as e:
                    logger.warning(f"Failed to process {ticker}: {e}")
                    results[ticker] = {}
            
            logger.info(f"Fetched Yahoo Finance data for {len(results)} tickers")
            
        except Exception as e:
            logger.error(f"Failed to fetch multiple Yahoo Finance data: {e}")
            # Fallback to individual requests
            for ticker in valid_tickers:
                results[ticker] = await self.fetch_stock_data(ticker)
        
        return results
    
    def is_etf(self, ticker: str) -> bool:
        """Check if ticker is an ETF"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info.get('quoteType') == 'ETF'
        except Exception as e:
            logger.warning(f"Failed to check ETF status for {ticker}: {e}")
            return False