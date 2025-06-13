import aiohttp
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from utils.logging_config import logger
from utils.rate_limiter import async_rate_limit
from config.settings import settings

class BaseDataClient(ABC):
    """Base class for data source clients"""
    
    def __init__(self, name: str, base_url: str = None, api_key: str = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self.headers,
            connector=aiohttp.TCPConnector(limit=settings.MAX_CONCURRENT_REQUESTS)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @async_rate_limit()
    async def _make_request(self, url: str, params: Dict = None, method: str = 'GET') -> Optional[Dict]:
        """Make HTTP request with error handling"""
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
        
        try:
            logger.debug(f"[{self.name}] Making {method} request to {url}")
            
            async with self.session.request(method, url, params=params) as response:
                response.raise_for_status()
                
                if 'application/json' in response.headers.get('content-type', ''):
                    data = await response.json()
                else:
                    data = await response.text()
                
                logger.debug(f"[{self.name}] Request successful")
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"[{self.name}] Request failed: {url}, Error: {e}")
            return None
        except Exception as e:
            logger.error(f"[{self.name}] Unexpected error: {e}")
            return None
    
    @abstractmethod
    async def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch stock data for given ticker"""
        pass
    
    @abstractmethod
    async def fetch_multiple_stocks(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch data for multiple stocks"""
        pass
    
    def validate_ticker(self, ticker: str) -> bool:
        """Validate ticker format"""
        if not ticker or not isinstance(ticker, str):
            return False
        
        ticker = ticker.strip().upper()
        if len(ticker) < 1 or len(ticker) > 10:
            return False
        
        # Basic validation - only letters and numbers
        return ticker.replace('.', '').replace('-', '').isalnum()