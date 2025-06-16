import asyncio
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Set, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from models.enhanced_models import (
    EnhancedInsiderTrade, Portfolio, Alert, BacktestResult,
    WatchlistItem, MarketRegime, Sector
)
from data_sources.yahoo_client import YahooFinanceClient
from data_sources.finnhub_client import FinnhubClient
from data_sources.web_scraper import WebScraperClient
from data_sources.insider_scraper import InsiderTradingScraper
from data_sources.alpha_vantage_client import AlphaVantageClient
from data_sources.polygon_client import PolygonClient
from analysis.advanced_financial_analyzer import AdvancedFinancialAnalyzer
from analysis.ml_predictor import MLPredictor
from analysis.risk_manager import RiskManager
from utils.logging_config import logger
from config.settings import settings

class EnhancedTradingService:
    """Enhanced trading service with ML predictions, risk management, and portfolio optimization"""
    
    def __init__(self):
        # Data sources
        self.insider_scraper = InsiderTradingScraper()
        self.yahoo_client = YahooFinanceClient()
        self.finnhub_client = FinnhubClient()
        self.web_scraper = WebScraperClient()
        self.alpha_vantage_client = AlphaVantageClient()
        self.polygon_client = PolygonClient()
        
        # Analysis engines
        self.financial_analyzer = AdvancedFinancialAnalyzer()
        self.ml_predictor = MLPredictor()
        self.risk_manager = RiskManager()
        
        # State management
        self.portfolios: Dict[str, Portfolio] = {}
        self.alerts: List[Alert] = []
        self.market_regime: Optional[MarketRegime] = None
        
        # Load existing data
        self._load_portfolios()
        self._load_alerts()
        
        # Initialize ML models if available
        self._initialize_ml_models()
    
    def fetch_and_analyze_trades_enhanced(
        self, 
        hours_back: int = 12, 
        min_amount: float = 100000,
        include_sales: bool = False,
        enable_ml_predictions: bool = True
    ) -> List[EnhancedInsiderTrade]:
        """Enhanced insider trade analysis with ML predictions"""
        
        logger.info(f"Enhanced analysis: {hours_back}h back, min amount: ${min_amount:,.0f}")
        
        try:
            # Fetch insider trades
            raw_trades = self.insider_scraper.fetch_insider_trades(hours_back, purchases_only=not include_sales)
            
            if not raw_trades:
                logger.warning("No insider trades found")
                return []
            
            # Convert to enhanced model
            enhanced_trades = []
            for trade in raw_trades:
                enhanced_trade = EnhancedInsiderTrade(
                    date=trade.date,
                    ticker=trade.ticker,
                    insider_name=trade.insider_name,
                    insider_title=trade.insider_title,
                    trade_type=trade.trade_type,
                    amount=trade.amount
                )
                enhanced_trades.append(enhanced_trade)
            
            # Filter by amount
            filtered_trades = [t for t in enhanced_trades if abs(t.amount) >= min_amount]
            logger.info(f"Filtered to {len(filtered_trades)} trades above minimum amount")
            
            # Get unique tickers for batch processing
            tickers = list(set(trade.ticker for trade in filtered_trades))
            
            # Fetch comprehensive market data
            market_data = asyncio.run(self._fetch_comprehensive_market_data(tickers))
            
            # Fetch historical data for ML predictions
            historical_data = {}
            if enable_ml_predictions:
                historical_data = asyncio.run(self._fetch_historical_data(tickers))
            
            # Analyze each trade comprehensively
            analyzed_trades = []
            for trade in filtered_trades:
                try:
                    ticker_market_data = market_data.get(trade.ticker, {})
                    ticker_historical_data = historical_data.get(trade.ticker)
                    
                    # Comprehensive analysis
                    analyzed_trade = self.financial_analyzer.analyze_comprehensive(
                        trade, ticker_market_data, ticker_historical_data
                    )
                    
                    # Set additional properties
                    analyzed_trade.sector = self._determine_sector(ticker_market_data)
                    analyzed_trade.company_name = self._get_company_name(ticker_market_data)
                    
                    analyzed_trades.append(analyzed_trade)
                    
                except Exception as e:
                    logger.error(f"Failed to analyze trade for {trade.ticker}: {e}")
                    analyzed_trades.append(trade)  # Add unanalyzed trade
            
            # Sort by composite score
            analyzed_trades.sort(key=lambda x: x.composite_score or 0, reverse=True)
            
            logger.info(f"Enhanced analysis completed for {len(analyzed_trades)} trades")
            return analyzed_trades
            
        except Exception as e:
            logger.error(f"Enhanced trade analysis failed: {e}")
            return []
    
    async def _fetch_comprehensive_market_data(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch comprehensive market data from all available sources"""
        
        market_data = {}
        
        try:
            logger.info(f"Fetching comprehensive data for {len(tickers)} tickers")
            
            # Create async context managers
            async with self.web_scraper:
                # Parallel data fetching
                tasks = []
                
                # Yahoo Finance (always included)
                tasks.append(self.yahoo_client.fetch_multiple_stocks(tickers))
                
                # Web scraping (always included)
                tasks.append(self.web_scraper.fetch_multiple_stocks(tickers))
                
                # Optional API sources
                if settings.ALPHA_VANTAGE_API_KEY:
                    tasks.append(self.alpha_vantage_client.fetch_multiple_stocks(tickers))
                else:
                    tasks.append(asyncio.create_task(self._empty_result(tickers)))
                
                if settings.POLYGON_API_KEY:
                    tasks.append(self.polygon_client.fetch_multiple_stocks(tickers))
                else:
                    tasks.append(asyncio.create_task(self._empty_result(tickers)))
                
                # Execute all tasks
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                yahoo_data = results[0] if not isinstance(results[0], Exception) else {}
                web_data = results[1] if not isinstance(results[1], Exception) else {}
                alpha_vantage_data = results[2] if not isinstance(results[2], Exception) else {}
                polygon_data = results[3] if not isinstance(results[3], Exception) else {}
                
                # Combine data for each ticker
                for ticker in tickers:
                    market_data[ticker] = {
                        'yahoo': yahoo_data.get(ticker, {}),
                        'web': web_data.get(ticker, {}),
                        'alpha_vantage': alpha_vantage_data.get(ticker, {}),
                        'polygon': polygon_data.get(ticker, {}),
                        'finnhub': {}  # Manual only
                    }
            
            logger.info(f"Comprehensive market data fetched for {len(market_data)} tickers")
            
        except Exception as e:
            logger.error(f"Error fetching comprehensive market data: {e}")
        
        return market_data
    
    async def _fetch_historical_data(self, tickers: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch historical price data for ML analysis"""
        
        historical_data = {}
        
        try:
            # Fetch 2 years of data for ML training
            for ticker in tickers:
                try:
                    yahoo_data = await self.yahoo_client.fetch_stock_data(ticker)
                    if yahoo_data and 'history' in yahoo_data:
                        hist_dict = yahoo_data['history']
                        if hist_dict:
                            df = pd.DataFrame(hist_dict)
                            if not df.empty:
                                # Ensure proper column names
                                df.columns = [col.lower() for col in df.columns]
                                historical_data[ticker] = df
                except Exception as e:
                    logger.warning(f"Failed to fetch historical data for {ticker}: {e}")
            
            logger.info(f"Historical data fetched for {len(historical_data)} tickers")
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
        
        return historical_data
    
    async def _empty_result(self, tickers: List[str]) -> Dict[str, Dict]:
        """Return empty result for disabled API sources"""
        return {ticker: {} for ticker in tickers}
    
    def _determine_sector(self, market_data: Dict[str, Any]) -> Optional[Sector]:
        """Determine sector from market data"""
        
        try:
            # Try Yahoo Finance first
            yahoo_info = market_data.get('yahoo', {}).get('info', {})
            sector_name = yahoo_info.get('sector')
            
            if not sector_name:
                # Try other sources
                alpha_vantage = market_data.get('alpha_vantage', {}).get('overview', {})
                sector_name = alpha_vantage.get('Sector')
            
            if sector_name:
                # Map to our Sector enum
                sector_mapping = {
                    'Technology': Sector.TECHNOLOGY,
                    'Healthcare': Sector.HEALTHCARE,
                    'Financial Services': Sector.FINANCIALS,
                    'Financials': Sector.FINANCIALS,
                    'Consumer Cyclical': Sector.CONSUMER_DISCRETIONARY,
                    'Consumer Defensive': Sector.CONSUMER_STAPLES,
                    'Industrials': Sector.INDUSTRIALS,
                    'Energy': Sector.ENERGY,
                    'Utilities': Sector.UTILITIES,
                    'Basic Materials': Sector.MATERIALS,
                    'Real Estate': Sector.REAL_ESTATE,
                    'Communication Services': Sector.COMMUNICATION_SERVICES
                }
                
                return sector_mapping.get(sector_name)
        
        except Exception as e:
            logger.warning(f"Error determining sector: {e}")
        
        return None
    
    def _get_company_name(self, market_data: Dict[str, Any]) -> Optional[str]:
        """Get company name from market data"""
        
        try:
            # Try Yahoo Finance first
            yahoo_info = market_data.get('yahoo', {}).get('info', {})
            company_name = yahoo_info.get('longName') or yahoo_info.get('shortName')
            
            if not company_name:
                # Try other sources
                alpha_vantage = market_data.get('alpha_vantage', {}).get('overview', {})
                company_name = alpha_vantage.get('Name')
            
            return company_name
        
        except Exception as e:
            logger.warning(f"Error getting company name: {e}")
        
        return None
    
    def analyze_watchlist_comprehensive(self) -> List[WatchlistItem]:
        """Comprehensive watchlist analysis with ML predictions"""
        
        tickers = self.load_watchlist()
        if not tickers:
            logger.warning("Watchlist is empty")
            return []
        
        logger.info(f"Comprehensive watchlist analysis for {len(tickers)} tickers")
        
        try:
            # Fetch comprehensive data
            market_data = asyncio.run(self._fetch_comprehensive_market_data(list(tickers)))
            historical_data = asyncio.run(self._fetch_historical_data(list(tickers)))
            
            watchlist_items = []
            
            for ticker in tickers:
                try:
                    # Create enhanced insider trade for analysis
                    dummy_trade = EnhancedInsiderTrade(
                        date=datetime.now(),
                        ticker=ticker,
                        insider_name="Watchlist Analysis",
                        insider_title="System",
                        trade_type="purchase",
                        amount=0
                    )
                    
                    # Comprehensive analysis
                    ticker_market_data = market_data.get(ticker, {})
                    ticker_historical_data = historical_data.get(ticker)
                    
                    analyzed_trade = self.financial_analyzer.analyze_comprehensive(
                        dummy_trade, ticker_market_data, ticker_historical_data
                    )
                    
                    # Create watchlist item
                    item = WatchlistItem(
                        ticker=ticker,
                        current_price=analyzed_trade.current_price,
                        target_price=analyzed_trade.fair_value,
                        technical_analysis=analyzed_trade.technical_indicators,
                        recommendation=analyzed_trade.recommendation
                    )
                    
                    # Add additional attributes
                    if hasattr(analyzed_trade, 'fundamental_data') and analyzed_trade.fundamental_data:
                        item.pe_ratio = analyzed_trade.fundamental_data.pe_ratio
                        item.peg_ratio = analyzed_trade.fundamental_data.peg_ratio
                        item.roe = analyzed_trade.fundamental_data.roe
                        item.debt_to_equity = analyzed_trade.fundamental_data.debt_to_equity
                        item.market_cap = analyzed_trade.fundamental_data.market_cap
                        item.free_cash_flow = analyzed_trade.fundamental_data.free_cash_flow
                        item.ebitda = analyzed_trade.fundamental_data.enterprise_value
                        item.sector = str(analyzed_trade.sector) if analyzed_trade.sector else "N/A"
                    
                    # Add scores
                    item.score = analyzed_trade.composite_score or 50
                    
                    watchlist_items.append(item)
                    
                except Exception as e:
                    logger.error(f"Failed to analyze watchlist ticker {ticker}: {e}")
                    # Add basic item
                    item = WatchlistItem(ticker=ticker)
                    watchlist_items.append(item)
            
            # Sort by score
            watchlist_items.sort(key=lambda x: x.score or 0, reverse=True)
            
            logger.info(f"Comprehensive watchlist analysis completed for {len(watchlist_items)} items")
            return watchlist_items
            
        except Exception as e:
            logger.error(f"Comprehensive watchlist analysis failed: {e}")
            return []
    
    def manual_finnhub_analysis(self, ticker: str) -> Dict[str, Any]:
        """Manual Finnhub analysis with enhanced processing"""
        
        logger.info(f"Manual Finnhub analysis for {ticker}")
        
        try:
            # Manual Finnhub data fetch
            finnhub_data = self.finnhub_client.fetch_stock_data_manual(ticker)
            
            if not finnhub_data:
                return {"error": "No Finnhub data available"}
            
            # Enhanced processing
            analysis = self._process_finnhub_data(ticker, finnhub_data)
            
            # Add ML predictions if historical data available
            try:
                historical_data = asyncio.run(self._fetch_historical_data([ticker]))
                if ticker in historical_data:
                    ml_predictions = self.ml_predictor.predict_price_movement(
                        historical_data[ticker], [1, 7, 30]
                    )
                    analysis['ml_predictions'] = ml_predictions
            except Exception as e:
                logger.warning(f"ML predictions failed for {ticker}: {e}")
            
            logger.info(f"Enhanced Finnhub analysis completed for {ticker}")
            return analysis
            
        except Exception as e:
            logger.error(f"Manual Finnhub analysis failed for {ticker}: {e}")
            return {"error": str(e)}
    
    def _process_finnhub_data(self, ticker: str, finnhub_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Finnhub data into structured analysis"""
        
        try:
            metrics = finnhub_data.get('metrics', {})
            profile = finnhub_data.get('profile', {})
            
            analysis = {
                'ticker': ticker,
                'company_info': {
                    'name': profile.get('name', 'N/A'),
                    'industry': profile.get('finnhubIndustry', 'N/A'),
                    'country': profile.get('country', 'N/A'),
                    'currency': profile.get('currency', 'N/A'),
                    'market_cap': profile.get('marketCapitalization', 'N/A'),
                    'share_outstanding': profile.get('shareOutstanding', 'N/A'),
                    'ipo_date': profile.get('ipo', 'N/A')
                },
                'valuation_metrics': {
                    'pe_ratio': metrics.get('peTTM', 'N/A'),
                    'peg_ratio': metrics.get('pegRatio', 'N/A'),
                    'pb_ratio': metrics.get('pbRatio', 'N/A'),
                    'ps_ratio': metrics.get('psRatio', 'N/A'),
                    'ev_ebitda': metrics.get('evEbitdaTTM', 'N/A'),
                    'ev_sales': metrics.get('evSalesTTM', 'N/A')
                },
                'profitability_metrics': {
                    'roe': metrics.get('roeTTM', 'N/A'),
                    'roa': metrics.get('roaTTM', 'N/A'),
                    'roic': metrics.get('roicTTM', 'N/A'),
                    'gross_margin': metrics.get('grossMarginTTM', 'N/A'),
                    'operating_margin': metrics.get('operatingMarginTTM', 'N/A'),
                    'net_margin': metrics.get('netProfitMarginTTM', 'N/A')
                },
                'financial_health': {
                    'debt_to_equity': metrics.get('debtToEquityRatio', 'N/A'),
                    'current_ratio': metrics.get('currentRatio', 'N/A'),
                    'quick_ratio': metrics.get('quickRatio', 'N/A'),
                    'interest_coverage': metrics.get('interestCoverageRatio', 'N/A')
                },
                'growth_metrics': {
                    'revenue_growth': metrics.get('revenueGrowthTTM', 'N/A'),
                    'earnings_growth': metrics.get('epsGrowthTTM', 'N/A'),
                    'book_value_growth': metrics.get('bookValueGrowthTTM', 'N/A')
                },
                'market_metrics': {
                    'beta': metrics.get('beta', 'N/A'),
                    'dividend_yield': metrics.get('dividendYieldIndicatedAnnual', 'N/A'),
                    'payout_ratio': metrics.get('payoutRatioTTM', 'N/A'),
                    '52_week_high': metrics.get('52WeekHigh', 'N/A'),
                    '52_week_low': metrics.get('52WeekLow', 'N/A')
                },
                'analyst_data': {
                    'price_target': finnhub_data.get('price_target', 'N/A'),
                    'recommendation': 'N/A'  # Would need separate API call
                },
                'sentiment_data': finnhub_data.get('news_sentiment', {}),
                'last_updated': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing Finnhub data for {ticker}: {e}")
            return {"error": str(e)}
    
    def create_portfolio(self, name: str, description: str = "") -> Portfolio:
        """Create a new portfolio"""
        
        portfolio = Portfolio(
            name=name,
            description=description
        )
        
        self.portfolios[name] = portfolio
        self._save_portfolios()
        
        logger.info(f"Created portfolio: {name}")
        return portfolio
    
    def add_position_to_portfolio(
        self, 
        portfolio_name: str, 
        ticker: str, 
        quantity: float,
        price: Optional[float] = None
    ) -> bool:
        """Add position to portfolio"""
        
        try:
            if portfolio_name not in self.portfolios:
                raise ValueError(f"Portfolio {portfolio_name} not found")
            
            portfolio = self.portfolios[portfolio_name]
            
            # Get current price if not provided
            if price is None:
                market_data = asyncio.run(self.yahoo_client.fetch_stock_data(ticker))
                if market_data and 'info' in market_data:
                    price = market_data['info'].get('regularMarketPrice')
                
                if price is None:
                    raise ValueError(f"Could not get price for {ticker}")
            
            # Add or update position
            if ticker in portfolio.positions:
                portfolio.positions[ticker] += quantity
            else:
                portfolio.positions[ticker] = quantity
            
            # Update portfolio value
            position_value = quantity * price
            portfolio.total_value += position_value
            
            self._save_portfolios()
            
            logger.info(f"Added {quantity} shares of {ticker} to portfolio {portfolio_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding position to portfolio: {e}")
            return False
    
    def calculate_portfolio_performance(self, portfolio_name: str) -> Dict[str, Any]:
        """Calculate comprehensive portfolio performance"""
        
        try:
            if portfolio_name not in self.portfolios:
                raise ValueError(f"Portfolio {portfolio_name} not found")
            
            portfolio = self.portfolios[portfolio_name]
            
            if not portfolio.positions:
                return {"error": "Portfolio is empty"}
            
            # Fetch current market data
            tickers = list(portfolio.positions.keys())
            market_data = asyncio.run(self._fetch_comprehensive_market_data(tickers))
            historical_data = asyncio.run(self._fetch_historical_data(tickers))
            
            # Calculate current portfolio value
            current_value = 0
            position_values = {}
            
            for ticker, quantity in portfolio.positions.items():
                ticker_data = market_data.get(ticker, {})
                current_price = None
                
                if ticker_data.get('yahoo', {}).get('info'):
                    current_price = ticker_data['yahoo']['info'].get('regularMarketPrice')
                
                if current_price:
                    position_value = quantity * current_price
                    current_value += position_value
                    position_values[ticker] = {
                        'quantity': quantity,
                        'current_price': current_price,
                        'value': position_value,
                        'weight': 0  # Will be calculated below
                    }
            
            # Calculate weights
            for ticker in position_values:
                position_values[ticker]['weight'] = position_values[ticker]['value'] / current_value
            
            # Risk analysis
            risk_metrics = self.risk_manager.calculate_portfolio_risk(
                portfolio, historical_data
            )
            
            # Performance metrics
            performance = {
                'portfolio_name': portfolio_name,
                'current_value': current_value,
                'initial_value': portfolio.total_value,
                'total_return': (current_value - portfolio.total_value) / portfolio.total_value if portfolio.total_value > 0 else 0,
                'positions': position_values,
                'risk_metrics': risk_metrics,
                'sector_allocation': self._calculate_sector_allocation(tickers, market_data),
                'last_updated': datetime.now().isoformat()
            }
            
            # Update portfolio object
            portfolio.total_value = current_value
            portfolio.total_return = performance['total_return']
            portfolio.volatility = risk_metrics.get('volatility')
            portfolio.sharpe_ratio = risk_metrics.get('sharpe_ratio')
            portfolio.max_drawdown = risk_metrics.get('max_drawdown')
            portfolio.var_95 = risk_metrics.get('var_95')
            
            self._save_portfolios()
            
            return performance
            
        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {e}")
            return {"error": str(e)}
    
    def _calculate_sector_allocation(
        self, 
        tickers: List[str], 
        market_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate sector allocation"""
        
        sector_allocation = {}
        
        try:
            for ticker in tickers:
                sector = self._determine_sector(market_data.get(ticker, {}))
                sector_name = str(sector) if sector else "Unknown"
                
                if sector_name not in sector_allocation:
                    sector_allocation[sector_name] = 0
                
                sector_allocation[sector_name] += 1
            
            # Convert to percentages
            total = len(tickers)
            for sector in sector_allocation:
                sector_allocation[sector] = sector_allocation[sector] / total
        
        except Exception as e:
            logger.error(f"Error calculating sector allocation: {e}")
        
        return sector_allocation
    
    def create_alert(
        self, 
        ticker: str, 
        alert_type: str, 
        condition: str, 
        threshold: float,
        email_notification: bool = False,
        push_notification: bool = False
    ) -> str:
        """Create a new alert"""
        
        try:
            alert_id = f"{ticker}_{alert_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            alert = Alert(
                id=alert_id,
                ticker=ticker,
                alert_type=alert_type,
                condition=condition,
                threshold=threshold,
                email_notification=email_notification,
                push_notification=push_notification
            )
            
            self.alerts.append(alert)
            self._save_alerts()
            
            logger.info(f"Created alert {alert_id} for {ticker}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return ""
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all active alerts"""
        
        triggered_alerts = []
        
        try:
            active_alerts = [alert for alert in self.alerts if alert.active and not alert.triggered]
            
            if not active_alerts:
                return triggered_alerts
            
            # Get unique tickers
            tickers = list(set(alert.ticker for alert in active_alerts))
            
            # Fetch current market data
            market_data = asyncio.run(self._fetch_comprehensive_market_data(tickers))
            
            for alert in active_alerts:
                try:
                    ticker_data = market_data.get(alert.ticker, {})
                    current_value = self._get_alert_value(alert, ticker_data)
                    
                    if current_value is not None:
                        alert.current_value = current_value
                        
                        # Check condition
                        if self._check_alert_condition(alert, current_value):
                            alert.triggered = True
                            alert.triggered_date = datetime.now()
                            
                            triggered_alerts.append({
                                'alert_id': alert.id,
                                'ticker': alert.ticker,
                                'alert_type': alert.alert_type,
                                'condition': alert.condition,
                                'threshold': alert.threshold,
                                'current_value': current_value,
                                'triggered_date': alert.triggered_date.isoformat()
                            })
                            
                            logger.info(f"Alert triggered: {alert.id}")
                
                except Exception as e:
                    logger.error(f"Error checking alert {alert.id}: {e}")
            
            # Save updated alerts
            if triggered_alerts:
                self._save_alerts()
        
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
        
        return triggered_alerts
    
    def _get_alert_value(self, alert: Alert, ticker_data: Dict[str, Any]) -> Optional[float]:
        """Get current value for alert checking"""
        
        try:
            yahoo_info = ticker_data.get('yahoo', {}).get('info', {})
            
            if alert.alert_type == 'price':
                return yahoo_info.get('regularMarketPrice')
            elif alert.alert_type == 'volume':
                return yahoo_info.get('regularMarketVolume')
            elif alert.alert_type == 'market_cap':
                return yahoo_info.get('marketCap')
            # Add more alert types as needed
            
        except Exception as e:
            logger.error(f"Error getting alert value: {e}")
        
        return None
    
    def _check_alert_condition(self, alert: Alert, current_value: float) -> bool:
        """Check if alert condition is met"""
        
        try:
            if alert.condition == 'above':
                return current_value > alert.threshold
            elif alert.condition == 'below':
                return current_value < alert.threshold
            elif alert.condition == 'equals':
                return abs(current_value - alert.threshold) < (alert.threshold * 0.01)  # 1% tolerance
            
        except Exception as e:
            logger.error(f"Error checking alert condition: {e}")
        
        return False
    
    def train_ml_models(self, retrain: bool = False) -> Dict[str, Any]:
        """Train ML models for price prediction"""
        
        try:
            logger.info("Starting ML model training...")
            
            # Check if models exist and are recent
            model_dir = settings.MODELS_DIR
            if not retrain and model_dir.exists():
                model_files = list(model_dir.glob("*.pkl"))
                if model_files:
                    # Check if models are recent (less than 24 hours old)
                    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
                    model_age = datetime.now().timestamp() - latest_model.stat().st_mtime
                    
                    if model_age < 24 * 3600:  # 24 hours
                        logger.info("Recent ML models found, loading existing models")
                        self.ml_predictor.load_models(model_dir)
                        return {"status": "loaded_existing", "model_age_hours": model_age / 3600}
            
            # Get training data
            watchlist_tickers = list(self.load_watchlist())
            if len(watchlist_tickers) < 5:
                # Add some default tickers for training
                watchlist_tickers.extend(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])
                watchlist_tickers = list(set(watchlist_tickers))
            
            # Fetch historical data for training
            logger.info(f"Fetching training data for {len(watchlist_tickers)} tickers")
            historical_data = asyncio.run(self._fetch_historical_data(watchlist_tickers))
            
            # Combine all data for training
            all_features = []
            all_targets = []
            
            for ticker, data in historical_data.items():
                if data is not None and len(data) > 100:
                    try:
                        features, targets = self.ml_predictor.prepare_features(data, target_days=1)
                        if len(features) > 0:
                            all_features.append(features)
                            all_targets.append(targets)
                    except Exception as e:
                        logger.warning(f"Failed to prepare features for {ticker}: {e}")
            
            if not all_features:
                raise ValueError("No training data available")
            
            # Combine all features and targets
            X = np.vstack(all_features)
            y = np.concatenate(all_targets)
            
            logger.info(f"Training with {len(X)} samples and {X.shape[1]} features")
            
            # Train ensemble models
            training_results = self.ml_predictor.train_ensemble_models(X, y)
            
            # Save models
            self.ml_predictor.save_models(model_dir)
            
            logger.info("ML model training completed successfully")
            
            return {
                "status": "training_completed",
                "training_samples": len(X),
                "features": X.shape[1],
                "model_results": training_results
            }
            
        except Exception as e:
            logger.error(f"ML model training failed: {e}")
            return {"status": "training_failed", "error": str(e)}
    
    def _initialize_ml_models(self):
        """Initialize ML models if available"""
        
        try:
            model_dir = settings.MODELS_DIR
            if model_dir.exists():
                model_files = list(model_dir.glob("*.pkl"))
                if model_files:
                    logger.info("Loading existing ML models")
                    self.ml_predictor.load_models(model_dir)
                else:
                    logger.info("No existing ML models found")
            else:
                logger.info("Models directory not found")
        
        except Exception as e:
            logger.warning(f"Failed to initialize ML models: {e}")
    
    def load_watchlist(self) -> Set[str]:
        """Load watchlist tickers from file"""
        try:
            if not settings.WATCHLIST_FILE.exists():
                # Create default watchlist
                default_watchlist = [
                    "# Enhanced Watchlist - Add tickers here, one per line",
                    "# Lines starting with # are comments",
                    "",
                    "# Technology",
                    "AAPL",
                    "MSFT",
                    "GOOGL",
                    "AMZN",
                    "TSLA",
                    "NVDA",
                    "META",
                    "",
                    "# Healthcare",
                    "JNJ",
                    "PFE",
                    "UNH",
                    "",
                    "# Finance",
                    "JPM",
                    "BAC",
                    "WFC",
                    "",
                    "# ETFs",
                    "SPY",
                    "QQQ",
                    "VTI"
                ]
                
                settings.WATCHLIST_FILE.write_text('\n'.join(default_watchlist), encoding='utf-8')
                logger.info("Created enhanced default watchlist file")
            
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
    
    def _load_portfolios(self):
        """Load portfolios from file"""
        try:
            if settings.PORTFOLIOS_FILE.exists():
                with open(settings.PORTFOLIOS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for name, portfolio_data in data.items():
                    portfolio = Portfolio(**portfolio_data)
                    self.portfolios[name] = portfolio
                
                logger.info(f"Loaded {len(self.portfolios)} portfolios")
        
        except Exception as e:
            logger.error(f"Failed to load portfolios: {e}")
    
    def _save_portfolios(self):
        """Save portfolios to file"""
        try:
            data = {}
            for name, portfolio in self.portfolios.items():
                data[name] = portfolio.dict()
            
            with open(settings.PORTFOLIOS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.debug("Portfolios saved")
        
        except Exception as e:
            logger.error(f"Failed to save portfolios: {e}")
    
    def _load_alerts(self):
        """Load alerts from file"""
        try:
            if settings.ALERTS_FILE.exists():
                with open(settings.ALERTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for alert_data in data:
                    alert = Alert(**alert_data)
                    self.alerts.append(alert)
                
                logger.info(f"Loaded {len(self.alerts)} alerts")
        
        except Exception as e:
            logger.error(f"Failed to load alerts: {e}")
    
    def _save_alerts(self):
        """Save alerts to file"""
        try:
            data = [alert.dict() for alert in self.alerts]
            
            with open(settings.ALERTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.debug("Alerts saved")
        
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")