import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict
from config.settings import settings
from utils.logging_config import logger

class CacheManager:
    """Enhanced cache management with TTL and compression"""
    
    def __init__(self):
        self.cache_dir = settings.CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_file(self, cache_type: str) -> Path:
        """Get cache file path for given type"""
        return self.cache_dir / f"{cache_type}_cache.json"
    
    def load_cache(self, ticker: str, cache_type: str = "default", ttl_seconds: int = None) -> Optional[Any]:
        """Load cached data with TTL check"""
        cache_file = self._get_cache_file(cache_type)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            if ticker not in cache:
                return None
            
            entry = cache[ticker]
            cache_time = entry.get('timestamp', 0)
            
            # Check TTL
            if ttl_seconds:
                if time.time() - cache_time > ttl_seconds:
                    logger.debug(f"Cache expired for {ticker} in {cache_type}")
                    return None
            else:
                # Use datetime for backward compatibility
                try:
                    cache_datetime = datetime.fromisoformat(entry.get('timestamp_iso', ''))
                    if datetime.now() - cache_datetime > timedelta(hours=settings.CACHE_DURATION_HOURS):
                        logger.debug(f"Cache expired for {ticker} in {cache_type}")
                        return None
                except (ValueError, KeyError):
                    pass
            
            logger.debug(f"Cache hit for {ticker} in {cache_type}")
            return entry.get('data')
            
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            logger.warning(f"Cache read error for {ticker} in {cache_type}: {e}")
            return None
    
    def save_cache(self, ticker: str, data: Any, cache_type: str = "default"):
        """Save data to cache with timestamp"""
        cache_file = self._get_cache_file(cache_type)
        
        # Load existing cache
        cache = {}
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning(f"Could not load existing cache {cache_type}, creating new")
        
        # Add new entry
        now = datetime.now()
        cache[ticker] = {
            'data': data,
            'timestamp': time.time(),
            'timestamp_iso': now.isoformat(),
            'cache_type': cache_type
        }
        
        # Save cache
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, default=str)
            logger.debug(f"Cached data for {ticker} in {cache_type}")
        except Exception as e:
            logger.error(f"Failed to save cache for {ticker} in {cache_type}: {e}")
    
    def clear_cache(self, cache_type: str = None):
        """Clear cache files"""
        if cache_type:
            cache_file = self._get_cache_file(cache_type)
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"Cleared cache: {cache_type}")
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*_cache.json"):
                cache_file.unlink()
            logger.info("Cleared all caches")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {}
        for cache_file in self.cache_dir.glob("*_cache.json"):
            cache_type = cache_file.stem.replace('_cache', '')
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                stats[cache_type] = {
                    'entries': len(cache),
                    'size_mb': cache_file.stat().st_size / (1024 * 1024),
                    'last_modified': datetime.fromtimestamp(cache_file.stat().st_mtime)
                }
            except Exception as e:
                logger.warning(f"Could not read cache stats for {cache_type}: {e}")
        return stats

# Global cache manager instance
cache_manager = CacheManager()