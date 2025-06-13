#!/usr/bin/env python3
"""
Insider Trading Monitor Pro v2.0
Enhanced version with modular architecture, async operations, and improved analysis
"""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from utils.logging_config import logger
from config.settings import settings

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'requests', 'cloudscraper', 'beautifulsoup4', 'yfinance',
        'finnhub-python', 'pandas', 'numpy', 'matplotlib', 'ta',
        'python-dotenv', 'pydantic', 'aiohttp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        print(f"Please install missing packages: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_environment():
    """Setup application environment"""
    
    # Create necessary directories
    for directory in [settings.CACHE_DIR, settings.LOGS_DIR, settings.DATA_DIR]:
        directory.mkdir(exist_ok=True)
    
    # Check for .env file
    env_file = project_root / '.env'
    if not env_file.exists():
        logger.warning(".env file not found. Please create one based on .env.example")
        print("Warning: .env file not found. Some features may not work properly.")
        print("Please copy .env.example to .env and configure your API keys.")
    
    # Check API keys
    if not settings.FINNHUB_API_KEY:
        logger.warning("Finnhub API key not configured. Enhanced analysis will be limited.")
    
    logger.info("Environment setup completed")

def main():
    """Main application entry point"""
    
    try:
        logger.info("Starting Insider Trading Monitor Pro v2.0")
        
        # Check requirements
        if not check_requirements():
            sys.exit(1)
        
        # Setup environment
        setup_environment()
        
        # Create and run main window
        app = MainWindow()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        logger.info("Application shutdown")

if __name__ == "__main__":
    main()