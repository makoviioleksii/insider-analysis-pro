import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any
from utils.logging_config import logger
from utils.rate_limiter import rate_limit
from models.trade_models import InsiderTrade, TradeType

class InsiderTradingScraper:
    """Scraper for insider trading data from OpenInsider"""
    
    def __init__(self):
        self.base_url = "http://openinsider.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    @rate_limit("openinsider", calls_per_minute=30)
    def fetch_insider_trades(self, hours_back: int = 12, purchases_only: bool = False) -> List[InsiderTrade]:
        """Fetch insider trades from OpenInsider"""
        url = f"{self.base_url}/latest-insider-trading"
        trades = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'tinytable'})
            
            if not table:
                logger.warning("No insider trading table found on OpenInsider")
                return []
            
            now = datetime.now()
            time_threshold = now - timedelta(hours=hours_back)
            
            for row in table.find_all('tr')[1:]:  # Skip header row
                try:
                    cols = row.find_all('td')
                    if len(cols) < 13:
                        continue
                    
                    # Parse trade date
                    trade_date_str = cols[1].text.strip()
                    try:
                        trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d %H:%M:%S')
                        if trade_date < time_threshold:
                            continue
                    except ValueError:
                        logger.warning(f"Invalid date format: {trade_date_str}")
                        continue
                    
                    # Extract trade information
                    ticker = cols[3].text.strip().upper()
                    if not ticker:
                        continue
                    
                    trade_type_str = cols[7].text.strip().lower()
                    
                    # Determine trade type
                    if 'p - purchase' in trade_type_str:
                        trade_type = TradeType.PURCHASE
                    elif 's - sale' in trade_type_str:
                        if purchases_only:
                            continue
                        trade_type = TradeType.SALE
                    else:
                        continue
                    
                    # Parse amount
                    try:
                        amount_str = cols[12].text.strip().replace('$', '').replace(',', '')
                        amount = float(amount_str)
                        if trade_type == TradeType.SALE:
                            amount = -amount  # Negative for sales
                    except (ValueError, IndexError):
                        logger.warning(f"Invalid amount for {ticker}: {cols[12].text.strip()}")
                        continue
                    
                    # Create InsiderTrade object
                    trade = InsiderTrade(
                        date=trade_date,
                        ticker=ticker,
                        insider_name=cols[5].text.strip(),
                        insider_title=cols[6].text.strip(),
                        trade_type=trade_type,
                        amount=amount
                    )
                    
                    trades.append(trade)
                    logger.debug(f"Processed trade for {ticker}: {trade_type.value}, amount: {amount}")
                    
                except Exception as e:
                    logger.warning(f"Error processing trade row: {e}")
                    continue
            
            logger.info(f"Fetched {len(trades)} insider trades from OpenInsider")
            return trades
            
        except Exception as e:
            logger.error(f"Failed to fetch insider trades: {e}")
            return []
    
    def fetch_specific_ticker_trades(self, ticker: str, days_back: int = 30) -> List[InsiderTrade]:
        """Fetch insider trades for a specific ticker"""
        url = f"{self.base_url}/search?q={ticker}"
        trades = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'tinytable'})
            
            if not table:
                logger.warning(f"No insider trading data found for {ticker}")
                return []
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for row in table.find_all('tr')[1:]:
                try:
                    cols = row.find_all('td')
                    if len(cols) < 13:
                        continue
                    
                    trade_date_str = cols[1].text.strip()
                    trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d %H:%M:%S')
                    
                    if trade_date < cutoff_date:
                        continue
                    
                    trade_type_str = cols[7].text.strip().lower()
                    if 'p - purchase' in trade_type_str:
                        trade_type = TradeType.PURCHASE
                    elif 's - sale' in trade_type_str:
                        trade_type = TradeType.SALE
                    else:
                        continue
                    
                    amount_str = cols[12].text.strip().replace('$', '').replace(',', '')
                    amount = float(amount_str)
                    if trade_type == TradeType.SALE:
                        amount = -amount
                    
                    trade = InsiderTrade(
                        date=trade_date,
                        ticker=ticker,
                        insider_name=cols[5].text.strip(),
                        insider_title=cols[6].text.strip(),
                        trade_type=trade_type,
                        amount=amount
                    )
                    
                    trades.append(trade)
                    
                except Exception as e:
                    logger.warning(f"Error processing trade for {ticker}: {e}")
                    continue
            
            logger.info(f"Fetched {len(trades)} trades for {ticker}")
            return trades
            
        except Exception as e:
            logger.error(f"Failed to fetch trades for {ticker}: {e}")
            return []