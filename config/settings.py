import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # API Keys
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")
    
    # Cache settings
    CACHE_DURATION_HOURS: int = int(os.getenv("CACHE_DURATION_HOURS", "1"))
    FINNHUB_CACHE_TTL: int = int(os.getenv("FINNHUB_CACHE_TTL", "86400"))
    
    # Rate limiting
    REQUESTS_PER_MINUTE: int = int(os.getenv("REQUESTS_PER_MINUTE", "60"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    
    # File paths
    BASE_DIR: Path = Path(__file__).parent.parent
    CACHE_DIR: Path = BASE_DIR / "cache"
    LOGS_DIR: Path = BASE_DIR / "logs"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Cache files
    STOCKANALYSIS_CACHE_FILE: Path = CACHE_DIR / "stockanalysis_cache.json"
    FINNHUB_CACHE_FILE: Path = CACHE_DIR / "finnhub_cache.json"
    WATCHLIST_FILE: Path = DATA_DIR / "watchlist.txt"
    
    # GUI settings
    AUTO_UPDATE_INTERVAL: int = int(os.getenv("AUTO_UPDATE_INTERVAL", "180"))
    DEFAULT_MIN_AMOUNT: float = float(os.getenv("DEFAULT_MIN_AMOUNT", "100000"))
    DEFAULT_HOURS_BACK: int = int(os.getenv("DEFAULT_HOURS_BACK", "12"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = LOGS_DIR / "insider_trading.log"
    
    def __post_init__(self):
        """Create necessary directories"""
        for directory in [self.CACHE_DIR, self.LOGS_DIR, self.DATA_DIR]:
            directory.mkdir(exist_ok=True)

settings = Settings()
settings.__post_init__()