import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import json

# Load environment variables
load_dotenv()

class Settings:
    """Enhanced application settings and configuration"""
    
    # API Keys
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")
    QUANDL_API_KEY: str = os.getenv("QUANDL_API_KEY", "")
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///insider_trading.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    
    # Cache settings
    CACHE_DURATION_HOURS: int = int(os.getenv("CACHE_DURATION_HOURS", "1"))
    FINNHUB_CACHE_TTL: int = int(os.getenv("FINNHUB_CACHE_TTL", "86400"))
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "3600"))
    
    # Rate limiting
    REQUESTS_PER_MINUTE: int = int(os.getenv("REQUESTS_PER_MINUTE", "60"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    
    # AI/ML settings
    ML_MODEL_UPDATE_INTERVAL: int = int(os.getenv("ML_MODEL_UPDATE_INTERVAL", "24"))  # hours
    SENTIMENT_ANALYSIS_ENABLED: bool = os.getenv("SENTIMENT_ANALYSIS_ENABLED", "true").lower() == "true"
    AI_PREDICTIONS_ENABLED: bool = os.getenv("AI_PREDICTIONS_ENABLED", "true").lower() == "true"
    
    # File paths
    BASE_DIR: Path = Path(__file__).parent.parent
    CACHE_DIR: Path = BASE_DIR / "cache"
    LOGS_DIR: Path = BASE_DIR / "logs"
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    
    # Cache files
    STOCKANALYSIS_CACHE_FILE: Path = CACHE_DIR / "stockanalysis_cache.json"
    FINNHUB_CACHE_FILE: Path = CACHE_DIR / "finnhub_cache.json"
    WATCHLIST_FILE: Path = DATA_DIR / "watchlist.txt"
    PORTFOLIOS_FILE: Path = DATA_DIR / "portfolios.json"
    ALERTS_FILE: Path = DATA_DIR / "alerts.json"
    
    # GUI settings
    AUTO_UPDATE_INTERVAL: int = int(os.getenv("AUTO_UPDATE_INTERVAL", "180"))
    DEFAULT_MIN_AMOUNT: float = float(os.getenv("DEFAULT_MIN_AMOUNT", "100000"))
    DEFAULT_HOURS_BACK: int = int(os.getenv("DEFAULT_HOURS_BACK", "12"))
    THEME: str = os.getenv("THEME", "dark")
    LANGUAGE: str = os.getenv("LANGUAGE", "ua")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = LOGS_DIR / "insider_trading.log"
    
    # Advanced features
    ENABLE_BACKTESTING: bool = os.getenv("ENABLE_BACKTESTING", "true").lower() == "true"
    ENABLE_PAPER_TRADING: bool = os.getenv("ENABLE_PAPER_TRADING", "true").lower() == "true"
    ENABLE_REAL_TIME_ALERTS: bool = os.getenv("ENABLE_REAL_TIME_ALERTS", "true").lower() == "true"
    ENABLE_PORTFOLIO_OPTIMIZATION: bool = os.getenv("ENABLE_PORTFOLIO_OPTIMIZATION", "true").lower() == "true"
    
    # Risk management
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "0.05"))  # 5% of portfolio
    STOP_LOSS_PERCENTAGE: float = float(os.getenv("STOP_LOSS_PERCENTAGE", "0.10"))  # 10%
    TAKE_PROFIT_PERCENTAGE: float = float(os.getenv("TAKE_PROFIT_PERCENTAGE", "0.20"))  # 20%
    
    # Notification settings
    EMAIL_NOTIFICATIONS: bool = os.getenv("EMAIL_NOTIFICATIONS", "false").lower() == "true"
    TELEGRAM_NOTIFICATIONS: bool = os.getenv("TELEGRAM_NOTIFICATIONS", "false").lower() == "true"
    DISCORD_NOTIFICATIONS: bool = os.getenv("DISCORD_NOTIFICATIONS", "false").lower() == "true"
    
    def __post_init__(self):
        """Create necessary directories"""
        for directory in [self.CACHE_DIR, self.LOGS_DIR, self.DATA_DIR, 
                         self.MODELS_DIR, self.EXPORTS_DIR]:
            directory.mkdir(exist_ok=True)
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get ML model configuration"""
        return {
            "ensemble_models": ["xgboost", "lightgbm", "catboost", "neural_network"],
            "feature_engineering": {
                "technical_indicators": True,
                "sentiment_features": True,
                "macro_economic_features": True,
                "insider_pattern_features": True
            },
            "hyperparameter_tuning": {
                "enabled": True,
                "method": "optuna",
                "n_trials": 100
            },
            "cross_validation": {
                "method": "time_series_split",
                "n_splits": 5
            }
        }
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration"""
        return {
            "var_confidence": 0.95,
            "expected_shortfall_confidence": 0.95,
            "max_drawdown": 0.20,
            "sharpe_ratio_threshold": 1.0,
            "correlation_threshold": 0.7,
            "volatility_threshold": 0.30
        }

settings = Settings()
settings.__post_init__()