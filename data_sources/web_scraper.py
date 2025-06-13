import aiohttp
import asyncio
from bs4 import BeautifulSoup
import cloudscraper
from typing import Dict, Any, Optional, List
from data_sources.base_client import BaseDataClient
from utils.logging_config import logger
from utils.cache_manager import cache_manager
from utils.rate_limiter import rate_limit

class WebScraperClient(BaseDataClient):
    """Web scraper for financial data from various sources"""
    
    def __init__(self):
        super().__init__("WebScraper")
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
    
    @rate_limit("finviz", calls_per_minute=30)
    async def fetch_finviz_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch data from Finviz"""
        if not self.validate_ticker(ticker):
            return {}
        
        # Check cache first
        cached_data = cache_manager.load_cache(ticker, "finviz", ttl_seconds=3600)
        if cached_data:
            return cached_data
        
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        
        try:
            response = self.scraper.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            finviz_data = {}
            
            # Extract target price
            target_price_element = soup.find(string="Target Price")
            if target_price_element:
                value_cell = target_price_element.find_parent('td').find_next_sibling('td')
                if value_cell and value_cell.text.strip() != "-":
                    try:
                        finviz_data['Target Price'] = float(value_cell.text.strip())
                    except ValueError:
                        pass
            
            # Extract other metrics
            metrics = ["RSI (14)", "Perf YTD", "PEG", "P/E", "ROE", "Debt/Eq", "Short Ratio"]
            for label in metrics:
                element = soup.find(string=label)
                if element:
                    value_cell = element.find_parent('td').find_next_sibling('td')
                    if value_cell:
                        finviz_data[label] = value_cell.text.strip()
            
            # Cache the data
            cache_manager.save_cache(ticker, finviz_data, "finviz")
            logger.info(f"Successfully fetched Finviz data for {ticker}")
            
            return finviz_data
            
        except Exception as e:
            logger.error(f"Failed to fetch Finviz data for {ticker}: {e}")
            return {}
    
    @rate_limit("stockanalysis", calls_per_minute=20)
    async def fetch_stockanalysis_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch data from StockAnalysis"""
        if not self.validate_ticker(ticker):
            return {}
        
        # Check cache first
        cached_data = cache_manager.load_cache(ticker, "stockanalysis", ttl_seconds=3600)
        if cached_data:
            return cached_data
        
        url = f"https://stockanalysis.com/stocks/{ticker}/"
        
        try:
            # Add delay to avoid being blocked
            await asyncio.sleep(3)
            
            response = self.scraper.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            stock_data = {}
            
            # Extract price target
            price_target_row = soup.find('td', string="Price Target")
            if price_target_row:
                value_cell = price_target_row.find_next_sibling('td')
                if value_cell:
                    value = value_cell.text.strip()
                    try:
                        price_target = float(value.split('(')[0].replace('$', '').strip())
                        stock_data['Target Price'] = price_target
                    except (ValueError, IndexError):
                        stock_data['Target Price'] = None
            
            # Extract current price
            price_elem = soup.find('span', class_='quote-price')
            if price_elem:
                try:
                    stock_data['regularMarketPrice'] = float(price_elem.text.replace('$', '').strip())
                except ValueError:
                    pass
            
            # Extract metrics from table
            metrics_table = soup.find('table', class_='key-metrics')
            if metrics_table:
                for row in metrics_table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()
                        
                        if key == 'P/E Ratio':
                            try:
                                stock_data['trailingPE'] = float(value)
                            except ValueError:
                                pass
                        elif key == 'Return on Equity':
                            try:
                                stock_data['returnOnEquity'] = float(value.replace('%', '')) / 100
                            except ValueError:
                                pass
                        elif key == 'Debt / Equity':
                            try:
                                stock_data['debtToEquity'] = float(value)
                            except ValueError:
                                pass
            
            # Cache the data
            cache_manager.save_cache(ticker, stock_data, "stockanalysis")
            logger.info(f"Successfully fetched StockAnalysis data for {ticker}")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Failed to fetch StockAnalysis data for {ticker}: {e}")
            return {}
    
    async def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch combined web scraper data"""
        finviz_data = await self.fetch_finviz_data(ticker)
        stockanalysis_data = await self.fetch_stockanalysis_data(ticker)
        
        return {
            'finviz': finviz_data,
            'stockanalysis': stockanalysis_data
        }
    
    async def fetch_multiple_stocks(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch data for multiple stocks"""
        results = {}
        
        # Process in batches to avoid overwhelming servers
        batch_size = 5
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            
            tasks = [self.fetch_stock_data(ticker) for ticker in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for ticker, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching data for {ticker}: {result}")
                    results[ticker] = {}
                else:
                    results[ticker] = result
            
            # Add delay between batches
            if i + batch_size < len(tickers):
                await asyncio.sleep(5)
        
        return results