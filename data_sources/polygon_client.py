from typing import Dict, Any, List, Optional
import aiohttp
from data_sources.base_client import BaseDataClient
from utils.logging_config import logger
from utils.cache_manager import cache_manager
from config.settings import settings

class PolygonClient(BaseDataClient):
    """Polygon.io API client"""
    
    def __init__(self):
        super().__init__("Polygon", "https://api.polygon.io")
        self.api_key = settings.POLYGON_API_KEY
    
    async def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch stock data from Polygon"""
        if not self.api_key:
            logger.warning("Polygon API key not configured")
            return {}
        
        if not self.validate_ticker(ticker):
            return {}
        
        # Check cache first
        cached_data = cache_manager.load_cache(ticker, "polygon", ttl_seconds=3600)
        if cached_data:
            return cached_data
        
        stock_data = {}
        
        try:
            # Get ticker details
            details_url = f"{self.base_url}/v3/reference/tickers/{ticker}"
            details_params = {'apikey': self.api_key}
            
            details_data = await self._make_request(details_url, details_params)
            if details_data and 'results' in details_data:
                stock_data['details'] = details_data['results']
            
            # Get financials
            financials_url = f"{self.base_url}/vX/reference/financials"
            financials_params = {
                'ticker': ticker,
                'apikey': self.api_key,
                'limit': 1
            }
            
            financials_data = await self._make_request(financials_url, financials_params)
            if financials_data and 'results' in financials_data:
                stock_data['financials'] = financials_data['results']
            
            # Get market status
            market_url = f"{self.base_url}/v1/marketstatus/now"
            market_params = {'apikey': self.api_key}
            
            market_data = await self._make_request(market_url, market_params)
            if market_data:
                stock_data['market_status'] = market_data
            
            # Cache the data
            if stock_data:
                cache_manager.save_cache(ticker, stock_data, "polygon")
                logger.info(f"Successfully fetched Polygon data for {ticker}")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Failed to fetch Polygon data for {ticker}: {e}")
            return {}
    
    async def fetch_multiple_stocks(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch data for multiple stocks"""
        results = {}
        
        # Process in small batches to respect rate limits
        batch_size = 3
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            
            tasks = [self.fetch_stock_data(ticker) for ticker in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for ticker, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching Polygon data for {ticker}: {result}")
                    results[ticker] = {}
                else:
                    results[ticker] = result
            
            # Add delay between batches
            if i + batch_size < len(tickers):
                import asyncio
                await asyncio.sleep(2)
        
        return results