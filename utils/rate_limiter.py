import time
import asyncio
from functools import wraps
from typing import Dict, Any
from asyncio_throttle import Throttler
from config.settings import settings
from utils.logging_config import logger

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, calls_per_minute: int = None):
        self.calls_per_minute = calls_per_minute or settings.REQUESTS_PER_MINUTE
        self.last_call_times: Dict[str, float] = {}
        self.throttler = Throttler(rate_limit=self.calls_per_minute, period=60)
    
    def wait_if_needed(self, service_name: str):
        """Wait if rate limit would be exceeded"""
        current_time = time.time()
        last_call = self.last_call_times.get(service_name, 0)
        time_since_last = current_time - last_call
        min_interval = 60.0 / self.calls_per_minute
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"Rate limiting {service_name}: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_call_times[service_name] = time.time()
    
    async def async_wait_if_needed(self, service_name: str):
        """Async version of rate limiting"""
        async with self.throttler:
            logger.debug(f"Rate limited request for {service_name}")

def rate_limit(service_name: str = None, calls_per_minute: int = None):
    """Decorator for rate limiting functions"""
    limiter = RateLimiter(calls_per_minute)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = service_name or func.__name__
            limiter.wait_if_needed(name)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def async_rate_limit(service_name: str = None, calls_per_minute: int = None):
    """Decorator for rate limiting async functions"""
    limiter = RateLimiter(calls_per_minute)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            name = service_name or func.__name__
            await limiter.async_wait_if_needed(name)
            return await func(*args, **kwargs)
        return wrapper
    return decorator