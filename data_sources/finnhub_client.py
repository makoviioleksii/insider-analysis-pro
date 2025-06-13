from typing import Dict, Any, List, Optional
import pandas as pd
from finnhub import Client
from data_sources.base_client import BaseDataClient
from utils.logging_config import logger
from utils.cache_manager import cache_manager
from config.settings import settings

class FinnhubClient(BaseDataClient):
    """Finnhub API client - MANUAL USE ONLY due to API limitations"""
    
    def __init__(self):
        super().__init__("Finnhub", "https://finnhub.io/api/v1/")
        if not settings.FINNHUB_API_KEY:
            logger.warning("Finnhub API key not provided")
            self.client = None
        else:
            self.client = Client(api_key=settings.FINNHUB_API_KEY)
    
    def fetch_stock_data_manual(self, ticker: str) -> Dict[str, Any]:
        """MANUAL fetch of comprehensive stock data from Finnhub"""
        if not self.client:
            logger.warning("Finnhub client not initialized")
            return {}
        
        if not self.validate_ticker(ticker):
            logger.warning(f"Invalid ticker format: {ticker}")
            return {}
        
        # Check cache first
        cached_data = cache_manager.load_cache(ticker, "finnhub", ttl_seconds=settings.FINNHUB_CACHE_TTL)
        if cached_data:
            logger.info(f"Using cached Finnhub data for {ticker}")
            return cached_data
        
        stock_data = {}
        
        try:
            logger.info(f"MANUAL Finnhub API call for {ticker}")
            
            # Basic company profile
            profile = self.client.company_profile2(symbol=ticker)
            stock_data['profile'] = profile
            
            # Financial metrics
            metrics = self.client.company_basic_financials(ticker, 'all')
            stock_data['metrics'] = metrics.get('metric', {})
            
            # Price target
            price_target = self.client.price_target(ticker)
            stock_data['price_target'] = price_target.get('targetMean')
            
            # News sentiment
            news_sentiment = self.client.news_sentiment(ticker)
            stock_data['news_sentiment'] = news_sentiment.get('sentiment', {})
            
            # Historical data (1 year)
            import time
            end_time = int(time.time())
            start_time = end_time - 365 * 24 * 3600
            
            candles = self.client.stock_candles(ticker, 'D', start_time, end_time)
            if candles.get('s') == 'ok' and candles.get('c'):
                stock_data['candles'] = pd.DataFrame({
                    'open': candles['o'],
                    'high': candles['h'],
                    'low': candles['l'],
                    'close': candles['c'],
                    'volume': candles['v'],
                    'timestamp': candles['t']
                })
                stock_data['candles']['date'] = pd.to_datetime(stock_data['candles']['timestamp'], unit='s')
            
            # Technical indicators
            try:
                rsi = self.client.technical_indicator(ticker, 'D', start_time, end_time, 'rsi')
                if rsi.get('s') == 'ok':
                    stock_data['rsi'] = rsi.get('rsi', [])
            except Exception as e:
                logger.warning(f"Failed to fetch RSI for {ticker}: {e}")
            
            # Cache the data
            cache_manager.save_cache(ticker, stock_data, "finnhub")
            logger.info(f"Successfully fetched Finnhub data for {ticker} (MANUAL)")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Failed to fetch Finnhub data for {ticker}: {e}")
            return {}
    
    async def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Disabled automatic fetch - use manual only"""
        logger.warning(f"Automatic Finnhub fetch disabled for {ticker}. Use manual fetch only.")
        return {}
    
    async def fetch_multiple_stocks(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Disabled automatic batch fetch - use manual only"""
        logger.warning("Automatic Finnhub batch fetch disabled. Use manual fetch only.")
        return {ticker: {} for ticker in tickers}
    
    async def fetch_insider_transactions(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch insider transactions for a ticker (manual only)"""
        if not self.client:
            return []
        
        try:
            from datetime import datetime, timedelta
            
            # Get insider transactions for the last 3 months
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            
            transactions = self.client.stock_insider_transactions(ticker, start_date, end_date)
            
            logger.info(f"Fetched {len(transactions.get('data', []))} insider transactions for {ticker}")
            return transactions.get('data', [])
            
        except Exception as e:
            logger.error(f"Failed to fetch insider transactions for {ticker}: {e}")
            return []