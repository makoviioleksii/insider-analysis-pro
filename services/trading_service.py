import asyncio
from typing import List, Dict, Any, Set
from datetime import datetime, timedelta
from pathlib import Path

from models.trade_models import InsiderTrade, WatchlistItem
from data_sources.yahoo_client import YahooFinanceClient
from data_sources.finnhub_client import FinnhubClient
from data_sources.web_scraper import WebScraperClient
from data_sources.insider_scraper import InsiderTradingScraper
from data_sources.alpha_vantage_client import AlphaVantageClient
from data_sources.polygon_client import PolygonClient
from analysis.financial_analyzer import FinancialAnalyzer
from analysis.technical_analyzer import TechnicalAnalyzer
from utils.logging_config import logger
from config.settings import settings

class TradingService:
    """Enhanced trading service with comprehensive data sources"""
    
    def __init__(self):
        self.insider_scraper = InsiderTradingScraper()
        self.financial_analyzer = FinancialAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        
        # Data clients
        self.yahoo_client = YahooFinanceClient()
        self.finnhub_client = FinnhubClient()
        self.web_scraper = WebScraperClient()
        self.alpha_vantage_client = AlphaVantageClient()
        self.polygon_client = PolygonClient()
    
    def fetch_and_analyze_trades(
        self, 
        hours_back: int = 12, 
        min_amount: float = 100000,
        include_sales: bool = False
    ) -> List[InsiderTrade]:
        """Fetch insider trades and perform comprehensive analysis"""
        
        logger.info(f"Fetching insider trades: {hours_back}h back, min amount: ${min_amount:,.0f}, include_sales: {include_sales}")
        
        # Fetch insider trades - sales only if explicitly requested
        trades = self.insider_scraper.fetch_insider_trades(hours_back, purchases_only=not include_sales)
        
        if not trades:
            logger.warning("No insider trades found")
            return []
        
        # Filter by amount
        filtered_trades = [t for t in trades if abs(t.amount) >= min_amount]
        logger.info(f"Filtered to {len(filtered_trades)} trades above minimum amount")
        
        # Get unique tickers for batch processing
        tickers = list(set(trade.ticker for trade in filtered_trades))
        
        # Separate watchlist tickers for enhanced processing
        watchlist_tickers = self.load_watchlist()
        regular_tickers = [t for t in tickers if t not in watchlist_tickers]
        watchlist_trade_tickers = [t for t in tickers if t in watchlist_tickers]
        
        # Fetch market data - enhanced for watchlist tickers
        market_data = asyncio.run(self._fetch_market_data_batch(regular_tickers, enhanced=False))
        watchlist_market_data = asyncio.run(self._fetch_market_data_batch(watchlist_trade_tickers, enhanced=True))
        
        # Combine market data
        market_data.update(watchlist_market_data)
        
        # Analyze each trade
        analyzed_trades = []
        for trade in filtered_trades:
            try:
                ticker_data = market_data.get(trade.ticker, {})
                analyzed_trade = self.financial_analyzer.analyze_insider_trade(trade, ticker_data)
                analyzed_trades.append(analyzed_trade)
            except Exception as e:
                logger.error(f"Failed to analyze trade for {trade.ticker}: {e}")
                analyzed_trades.append(trade)  # Add unanalyzed trade
        
        logger.info(f"Completed analysis for {len(analyzed_trades)} trades")
        return analyzed_trades
    
    async def _fetch_market_data_batch(self, tickers: List[str], enhanced: bool = False) -> Dict[str, Dict[str, Any]]:
        """Fetch market data for multiple tickers - enhanced mode for watchlist"""
        
        if not tickers:
            return {}
        
        logger.info(f"Fetching market data for {len(tickers)} tickers (enhanced: {enhanced})")
        
        market_data = {}
        
        try:
            # Create async context managers for clients that support it
            async with self.web_scraper:
                # Fetch data from available sources
                yahoo_task = self.yahoo_client.fetch_multiple_stocks(tickers)
                web_task = self.web_scraper.fetch_multiple_stocks(tickers)
                
                # Enhanced mode includes additional API sources
                if enhanced and (settings.ALPHA_VANTAGE_API_KEY or settings.POLYGON_API_KEY):
                    tasks = [yahoo_task, web_task]
                    
                    if settings.ALPHA_VANTAGE_API_KEY:
                        alpha_vantage_task = self.alpha_vantage_client.fetch_multiple_stocks(tickers)
                        tasks.append(alpha_vantage_task)
                    
                    if settings.POLYGON_API_KEY:
                        polygon_task = self.polygon_client.fetch_multiple_stocks(tickers)
                        tasks.append(polygon_task)
                    
                    # Wait for all tasks to complete
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    yahoo_data = results[0] if not isinstance(results[0], Exception) else {}
                    web_data = results[1] if not isinstance(results[1], Exception) else {}
                    alpha_vantage_data = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else {}
                    polygon_data = results[3] if len(results) > 3 and not isinstance(results[3], Exception) else {}
                    
                else:
                    # Standard mode - only Yahoo and Web scraper
                    yahoo_data, web_data = await asyncio.gather(
                        yahoo_task, web_task, return_exceptions=True
                    )
                    
                    if isinstance(yahoo_data, Exception):
                        logger.error(f"Yahoo Finance batch fetch failed: {yahoo_data}")
                        yahoo_data = {}
                    
                    if isinstance(web_data, Exception):
                        logger.error(f"Web scraper batch fetch failed: {web_data}")
                        web_data = {}
                    
                    alpha_vantage_data = {}
                    polygon_data = {}
                
                # Combine data for each ticker
                for ticker in tickers:
                    market_data[ticker] = {
                        'yahoo': yahoo_data.get(ticker, {}),
                        'web': web_data.get(ticker, {}),
                        'alpha_vantage': alpha_vantage_data.get(ticker, {}),
                        'polygon': polygon_data.get(ticker, {}),
                        'finnhub': {}  # Empty by default - manual only
                    }
                    
                    # Enhanced processing for watchlist tickers
                    if enhanced:
                        logger.info(f"Enhanced processing for watchlist ticker: {ticker}")
        
        except Exception as e:
            logger.error(f"Batch market data fetch failed: {e}")
            # Fallback to individual requests
            for ticker in tickers:
                try:
                    yahoo_data = await self.yahoo_client.fetch_stock_data(ticker)
                    web_data = await self.web_scraper.fetch_stock_data(ticker)
                    
                    market_data[ticker] = {
                        'yahoo': yahoo_data,
                        'web': web_data,
                        'alpha_vantage': {},
                        'polygon': {},
                        'finnhub': {}
                    }
                except Exception as ticker_error:
                    logger.error(f"Failed to fetch data for {ticker}: {ticker_error}")
                    market_data[ticker] = {}
        
        logger.info(f"Fetched market data for {len(market_data)} tickers")
        return market_data
    
    def analyze_watchlist_comprehensive(self) -> List[WatchlistItem]:
        """Comprehensive analysis for watchlist tickers with all data sources"""
        
        tickers = self.load_watchlist()
        if not tickers:
            logger.warning("Watchlist is empty")
            return []
        
        logger.info(f"Comprehensive analysis for {len(tickers)} watchlist tickers")
        
        # Fetch comprehensive market data for watchlist
        market_data = asyncio.run(self._fetch_market_data_batch(list(tickers), enhanced=True))
        
        watchlist_items = []
        
        for ticker in tickers:
            try:
                ticker_data = market_data.get(ticker, {})
                
                # Get price data for technical analysis
                yahoo_data = ticker_data.get('yahoo', {})
                price_history = yahoo_data.get('history', {})
                
                # Create enhanced watchlist item
                item = WatchlistItem(ticker=ticker)
                
                if price_history:
                    # Convert to DataFrame for technical analysis
                    import pandas as pd
                    df = pd.DataFrame(price_history)
                    
                    if not df.empty and 'Close' in df.columns:
                        # Rename columns to lowercase for consistency
                        df.columns = [col.lower() for col in df.columns]
                        
                        # Perform technical analysis
                        technical_analysis = self.technical_analyzer.analyze_stock(ticker, df)
                        item.technical_analysis = technical_analysis
                        
                        # Get current price from multiple sources
                        current_price = (
                            yahoo_data.get('info', {}).get('regularMarketPrice') or
                            ticker_data.get('web', {}).get('stockanalysis', {}).get('regularMarketPrice')
                        )
                        item.current_price = current_price
                        
                        # Aggregate target prices from all sources
                        target_prices = []
                        yahoo_target = yahoo_data.get('info', {}).get('targetMeanPrice')
                        finviz_target = ticker_data.get('web', {}).get('finviz', {}).get('Target Price')
                        stockanalysis_target = ticker_data.get('web', {}).get('stockanalysis', {}).get('Target Price')
                        
                        for price in [yahoo_target, finviz_target, stockanalysis_target]:
                            if price and isinstance(price, (int, float)) and price > 0:
                                target_prices.append(price)
                        
                        item.target_price = sum(target_prices) / len(target_prices) if target_prices else None
                        
                        # Add comprehensive financial metrics
                        yahoo_info = yahoo_data.get('info', {})
                        alpha_vantage_overview = ticker_data.get('alpha_vantage', {}).get('overview', {})
                        polygon_details = ticker_data.get('polygon', {}).get('details', {})
                        
                        # Financial metrics from multiple sources
                        item.pe_ratio = (
                            yahoo_info.get('trailingPE') or
                            alpha_vantage_overview.get('PERatio') or
                            polygon_details.get('pe_ratio')
                        )
                        
                        item.peg_ratio = (
                            yahoo_info.get('pegRatio') or
                            alpha_vantage_overview.get('PEGRatio')
                        )
                        
                        item.roe = (
                            yahoo_info.get('returnOnEquity') or
                            alpha_vantage_overview.get('ReturnOnEquityTTM')
                        )
                        
                        item.debt_to_equity = (
                            yahoo_info.get('debtToEquity') or
                            alpha_vantage_overview.get('DebtToEquityRatio')
                        )
                        
                        item.market_cap = (
                            yahoo_info.get('marketCap') or
                            alpha_vantage_overview.get('MarketCapitalization') or
                            polygon_details.get('market_cap')
                        )
                        
                        item.free_cash_flow = yahoo_info.get('freeCashflow')
                        item.ebitda = yahoo_info.get('ebitda')
                        item.sector = yahoo_info.get('sector', 'N/A')
                        
                        # Calculate comprehensive score
                        item.score = self._calculate_comprehensive_score(item)
                        
                        # Generate recommendation
                        if technical_analysis and current_price:
                            recommendation = self.technical_analyzer.generate_recommendation(
                                technical_analysis, current_price, item.target_price
                            )
                            item.recommendation = recommendation
                        
                        logger.debug(f"Comprehensive analysis completed for watchlist item: {ticker}")
                
                watchlist_items.append(item)
                    
            except Exception as e:
                logger.error(f"Failed to analyze watchlist ticker {ticker}: {e}")
                item = WatchlistItem(ticker=ticker)
                watchlist_items.append(item)
        
        logger.info(f"Completed comprehensive watchlist analysis for {len(watchlist_items)} items")
        return watchlist_items
    
    def _calculate_comprehensive_score(self, item: WatchlistItem) -> int:
        """Calculate comprehensive score for watchlist item"""
        score = 0
        
        try:
            # P/E Ratio scoring
            if item.pe_ratio:
                if 0 < item.pe_ratio < 15:
                    score += 2
                elif 15 <= item.pe_ratio <= 25:
                    score += 1
                elif item.pe_ratio > 30:
                    score -= 1
            
            # PEG Ratio scoring
            if item.peg_ratio:
                if item.peg_ratio < 1:
                    score += 2
                elif item.peg_ratio > 2:
                    score -= 1
            
            # ROE scoring
            if item.roe:
                if item.roe > 0.20:
                    score += 3
                elif item.roe > 0.15:
                    score += 2
                elif item.roe < 0:
                    score -= 2
            
            # Debt to Equity scoring
            if item.debt_to_equity:
                if item.debt_to_equity < 0.3:
                    score += 2
                elif item.debt_to_equity > 2:
                    score -= 2
            
            # Technical analysis scoring
            if item.technical_analysis:
                tech = item.technical_analysis
                
                # RSI scoring
                if tech.rsi:
                    if tech.rsi < 30:
                        score += 2
                    elif tech.rsi > 70:
                        score -= 1
                
                # Trend scoring
                if tech.trend == "Bullish":
                    score += 2
                elif tech.trend == "Bearish":
                    score -= 2
                
                # Price vs moving averages
                if tech.sma20 and item.current_price and item.current_price > tech.sma20:
                    score += 1
                if tech.ema50 and item.current_price and item.current_price > tech.ema50:
                    score += 1
            
            # Target price vs current price
            if item.target_price and item.current_price:
                potential = (item.target_price - item.current_price) / item.current_price
                if potential > 0.2:  # 20% upside
                    score += 2
                elif potential > 0.1:  # 10% upside
                    score += 1
                elif potential < -0.1:  # 10% downside
                    score -= 1
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive score for {item.ticker}: {e}")
        
        return score
    
    def manual_finnhub_analysis(self, ticker: str) -> Dict[str, Any]:
        """Manual Finnhub analysis for specific ticker"""
        
        logger.info(f"Manual Finnhub analysis for {ticker}")
        
        try:
            # Manual Finnhub data fetch
            finnhub_data = self.finnhub_client.fetch_stock_data_manual(ticker)
            
            if not finnhub_data:
                return {"error": "No Finnhub data available"}
            
            # Extract key metrics
            metrics = finnhub_data.get('metrics', {})
            profile = finnhub_data.get('profile', {})
            
            analysis = {
                'ticker': ticker,
                'company_name': profile.get('name', 'N/A'),
                'industry': profile.get('finnhubIndustry', 'N/A'),
                'market_cap': profile.get('marketCapitalization', 'N/A'),
                'pe_ratio': metrics.get('peTTM', 'N/A'),
                'peg_ratio': metrics.get('pegRatio', 'N/A'),
                'roe': metrics.get('roeTTM', 'N/A'),
                'debt_to_equity': metrics.get('debtToEquity', 'N/A'),
                'free_cash_flow': metrics.get('freeCashflow', 'N/A'),
                'price_target': finnhub_data.get('price_target', 'N/A'),
                'news_sentiment': finnhub_data.get('news_sentiment', {}).get('bullishPercent', 'N/A'),
                'beta': metrics.get('beta', 'N/A'),
                'dividend_yield': metrics.get('dividendYield', 'N/A'),
                'profit_margin': metrics.get('netProfitMarginTTM', 'N/A'),
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info(f"Manual Finnhub analysis completed for {ticker}")
            return analysis
            
        except Exception as e:
            logger.error(f"Manual Finnhub analysis failed for {ticker}: {e}")
            return {"error": str(e)}
    
    def load_watchlist(self) -> Set[str]:
        """Load watchlist tickers from file"""
        try:
            if not settings.WATCHLIST_FILE.exists():
                # Create default watchlist
                settings.WATCHLIST_FILE.write_text(
                    "# Add tickers here, one per line\n"
                    "# Lines starting with # are comments\n"
                    "AAPL\n"
                    "MSFT\n"
                    "GOOGL\n"
                    "TSLA\n"
                )
                logger.info("Created default watchlist file")
            
            with open(settings.WATCHLIST_FILE, 'r', encoding='utf-8') as f:
                tickers = set()
                for line in f:
                    line = line.strip().upper()
                    if line and not line.startswith('#'):
                        tickers.add(line)
                
                logger.debug(f"Loaded {len(tickers)} tickers from watchlist")
                return tickers
                
        except Exception as e:
            logger.error(f"Failed to load watchlist: {e}")
            return set()
    
    def add_to_watchlist(self, ticker: str):
        """Add ticker to watchlist"""
        try:
            ticker = ticker.upper().strip()
            
            # Load existing tickers
            existing_tickers = self.load_watchlist()
            
            if ticker in existing_tickers:
                logger.info(f"{ticker} already in watchlist")
                return
            
            # Add to file
            with open(settings.WATCHLIST_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{ticker}\n")
            
            logger.info(f"Added {ticker} to watchlist")
            
        except Exception as e:
            logger.error(f"Failed to add {ticker} to watchlist: {e}")
            raise
    
    def remove_from_watchlist(self, ticker: str):
        """Remove ticker from watchlist"""
        try:
            ticker = ticker.upper().strip()
            
            # Read all lines
            with open(settings.WATCHLIST_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter out the ticker
            filtered_lines = [line for line in lines if line.strip().upper() != ticker]
            
            # Write back
            with open(settings.WATCHLIST_FILE, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
            
            logger.info(f"Removed {ticker} from watchlist")
            
        except Exception as e:
            logger.error(f"Failed to remove {ticker} from watchlist: {e}")
            raise