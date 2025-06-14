#!/usr/bin/env python3
"""
Insider Trading Monitor Pro v2.0
Enhanced version with modular architecture, async operations, and improved analysis
"""

import sys
import subprocess
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = {
        'requests': 'requests',
        'cloudscraper': 'cloudscraper',
        'beautifulsoup4': 'bs4',
        'yfinance': 'yfinance',
        'finnhub-python': 'finnhub',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'ta': 'ta',
        'python-dotenv': 'dotenv',
        'pydantic': 'pydantic',
        'aiohttp': 'aiohttp',
        'asyncio-throttle': 'asyncio_throttle'
    }

    missing_packages = []

    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)

    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        
        # Try to auto-install missing packages
        auto_install = input("Do you want to auto-install missing packages? (y/n): ").lower().strip()
        if auto_install == 'y':
            print("Installing missing packages...")
            failed_packages = []
            for package in missing_packages:
                print(f"Installing {package}...")
                if not install_package(package):
                    failed_packages.append(package)
            
            if failed_packages:
                print(f"Failed to install: {', '.join(failed_packages)}")
                print(f"Please install manually: pip install {' '.join(failed_packages)}")
                return False
            else:
                print("All packages installed successfully!")
                return True
        else:
            print(f"Please install missing packages: pip install {' '.join(missing_packages)}")
            return False

    return True

def setup_environment():
    """Setup application environment"""
    from config.settings import settings
    from utils.logging_config import logger
    
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
        print("Starting Insider Trading Monitor Pro v2.0")
        
        # Check requirements
        if not check_requirements():
            sys.exit(1)
        
        # Import after requirements check
        from gui.main_window import MainWindow
        from utils.logging_config import logger
        
        logger.info("Starting Insider Trading Monitor Pro v2.0")
        
        # Setup environment
        setup_environment()
        
        # Create and run main window
        app = MainWindow()
        app.run()
        
    except KeyboardInterrupt:
        print("Application interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        try:
            from utils.logging_config import logger
            logger.error(f"Application failed to start: {e}", exc_info=True)
        except:
            pass
        sys.exit(1)
    finally:
        try:
            from utils.logging_config import logger
            logger.info("Application shutdown")
        except:
            pass

if __name__ == "__main__":
    main()