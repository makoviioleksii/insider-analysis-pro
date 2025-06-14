from typing import Dict, Any, List, Optional
import aiohttp
from data_sources.base_client import BaseDataClient
from utils.logging_config import logger
from utils.cache_manager import cache_manager
from config.settings import settings

class AlphaVantageClient(BaseDataClient):
    """Alpha Vantage API client"""
    
    def __init__(self):
        super().__init__("AlphaVantage", "https://www.alphavantage.co/query")
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
    
    async def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch stock data from Alpha Vantage"""
        if not self.api_key:
            logger.warning("Alpha Vantage API key not configured")
            return {}
        
        if not self.validate_ticker(ticker):
            return {}
        
        # Check cache first
        cached_data = cache_manager.load_cache(ticker, "alpha_vantage", ttl_seconds=3600)
        if cached_data:
            return cached_data
        
        stock_data = {}
        
        try:
            # Get overview data
            overview_params = {
                'function': 'OVERVIEW',
                'symbol': ticker,
                'apikey': self.api_key
            }
            
            overview_data = await self._make_request(self.base_url, overview_params)
            if overview_data and 'Symbol' in overview_data:
                stock_data['overview'] = overview_data
            
            # Get technical indicators
            rsi_params = {
                'function': 'RSI',
                'symbol': ticker,
                'interval': 'daily',
                'time_period': 14,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            rsi_data = await self._make_request(self.base_url, rsi_params)
            if rsi_data and 'Technical Analysis: RSI' in rsi_data:
                stock_data['rsi'] = rsi_data['Technical Analysis: RSI']
            
            # Cache the data
            if stock_data:
                cache_manager.save_cache(ticker, stock_data, "alpha_vantage")
                logger.info(f"Successfully fetched Alpha Vantage data for {ticker}")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Failed to fetch Alpha Vantage data for {ticker}: {e}")
            return {}
    
    async def fetch_multiple_stocks(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch data for multiple stocks"""
        results = {}
        
        # Process sequentially to avoid rate limits
        for ticker in tickers:
            try:
                data = await self.fetch_stock_data(ticker)
                results[ticker] = data
                
                # Add delay to respect rate limits
                import asyncio
                await asyncio.sleep(12)  # Alpha Vantage free tier: 5 calls per minute
                
            except Exception as e:
                logger.error(f"Error fetching Alpha Vantage data for {ticker}: {e}")
                results[ticker] = {}
        
        return results