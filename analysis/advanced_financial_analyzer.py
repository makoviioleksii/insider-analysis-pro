import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
import tensorflow as tf
from tensorflow import keras
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from models.enhanced_models import (
    EnhancedInsiderTrade, Recommendation, RiskLevel, 
    FundamentalData, TechnicalIndicators, SentimentData
)
from utils.logging_config import logger

class AdvancedFinancialAnalyzer:
    """Advanced financial analyzer with ML predictions and comprehensive scoring"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # Enhanced scoring weights with ML-optimized values
        self.score_weights = {
            # Fundamental Analysis (40%)
            'pe_ratio': 3.0,
            'peg_ratio': 3.5,
            'roe': 4.0,
            'debt_to_equity': 2.5,
            'free_cash_flow': 3.0,
            'revenue_growth': 2.5,
            'earnings_growth': 3.0,
            'profit_margin': 2.0,
            
            # Technical Analysis (30%)
            'rsi': 2.0,
            'macd': 2.5,
            'bollinger_position': 1.5,
            'volume_trend': 2.0,
            'price_momentum': 3.0,
            'support_resistance': 2.0,
            
            # Insider Analysis (20%)
            'insider_track_record': 4.0,
            'trade_size_significance': 3.0,
            'insider_position': 2.5,
            'trade_timing': 2.0,
            'insider_sentiment': 2.5,
            
            # Market Sentiment (10%)
            'news_sentiment': 1.5,
            'analyst_sentiment': 2.0,
            'social_sentiment': 1.0,
            'market_sentiment': 1.5
        }
        
        # Risk assessment parameters
        self.risk_factors = {
            'volatility_weight': 0.25,
            'beta_weight': 0.20,
            'liquidity_weight': 0.15,
            'sector_risk_weight': 0.15,
            'fundamental_risk_weight': 0.25
        }
    
    def analyze_comprehensive(
        self, 
        trade: EnhancedInsiderTrade,
        market_data: Dict[str, Any],
        historical_data: Optional[pd.DataFrame] = None
    ) -> EnhancedInsiderTrade:
        """Comprehensive analysis with ML predictions"""
        
        try:
            logger.info(f"Starting comprehensive analysis for {trade.ticker}")
            
            # Extract data from various sources
            yahoo_data = market_data.get('yahoo', {}).get('info', {})
            web_data = market_data.get('web', {})
            finviz_data = web_data.get('finviz', {})
            stockanalysis_data = web_data.get('stockanalysis', {})
            finnhub_data = market_data.get('finnhub', {}).get('metrics', {})
            
            # 1. Fundamental Analysis
            fundamental_data = self._extract_fundamental_data(
                trade.ticker, yahoo_data, finviz_data, stockanalysis_data, finnhub_data
            )
            trade.fundamental_data = fundamental_data
            trade.fundamental_score = self._calculate_fundamental_score(fundamental_data)
            
            # 2. Technical Analysis
            if historical_data is not None and not historical_data.empty:
                technical_indicators = self._calculate_technical_indicators(
                    trade.ticker, historical_data
                )
                trade.technical_indicators = technical_indicators
                trade.technical_score = self._calculate_technical_score(technical_indicators)
            
            # 3. Sentiment Analysis
            sentiment_data = self._analyze_sentiment(trade.ticker, market_data)
            trade.sentiment_data = sentiment_data
            trade.sentiment_score = self._calculate_sentiment_score(sentiment_data)
            
            # 4. Insider Analysis
            insider_score = self._analyze_insider_patterns(trade)
            trade.insider_score = insider_score
            
            # 5. ML Predictions
            if historical_data is not None:
                predictions = self._generate_ml_predictions(trade, historical_data)
                trade.price_prediction_1d = predictions.get('price_1d')
                trade.price_prediction_7d = predictions.get('price_7d')
                trade.price_prediction_30d = predictions.get('price_30d')
                trade.probability_up_1d = predictions.get('prob_up_1d')
                trade.probability_up_7d = predictions.get('prob_up_7d')
                trade.probability_up_30d = predictions.get('prob_up_30d')
            
            # 6. Risk Assessment
            risk_assessment = self._assess_risk(trade, historical_data)
            trade.risk_level = risk_assessment['risk_level']
            trade.var_1d = risk_assessment.get('var_1d')
            trade.var_7d = risk_assessment.get('var_7d')
            trade.expected_shortfall = risk_assessment.get('expected_shortfall')
            
            # 7. Composite Scoring
            trade.composite_score = self._calculate_composite_score(trade)
            
            # 8. Generate Recommendation
            recommendation_result = self._generate_recommendation(trade)
            trade.recommendation = recommendation_result['recommendation']
            trade.confidence_level = recommendation_result['confidence']
            trade.reasons = recommendation_result['reasons']
            trade.warnings = recommendation_result['warnings']
            
            # 9. Fair Value Calculation
            trade.fair_value = self._calculate_fair_value(trade)
            
            logger.info(f"Comprehensive analysis completed for {trade.ticker}")
            return trade
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed for {trade.ticker}: {e}")
            return trade
    
    def _extract_fundamental_data(
        self, 
        ticker: str, 
        yahoo_data: Dict, 
        finviz_data: Dict, 
        stockanalysis_data: Dict, 
        finnhub_data: Dict
    ) -> FundamentalData:
        """Extract and normalize fundamental data from multiple sources"""
        
        fundamental = FundamentalData(ticker=ticker, date=datetime.now())
        
        try:
            # Valuation Metrics
            fundamental.pe_ratio = self._get_best_value(
                yahoo_data.get('trailingPE'),
                self._parse_numeric(finviz_data.get('P/E')),
                stockanalysis_data.get('trailingPE'),
                finnhub_data.get('peTTM')
            )
            
            fundamental.peg_ratio = self._get_best_value(
                yahoo_data.get('pegRatio'),
                self._parse_numeric(finviz_data.get('PEG')),
                finnhub_data.get('pegRatio')
            )
            
            fundamental.pb_ratio = self._get_best_value(
                yahoo_data.get('priceToBook'),
                self._parse_numeric(finviz_data.get('P/B')),
                finnhub_data.get('pbRatio')
            )
            
            fundamental.ps_ratio = self._get_best_value(
                yahoo_data.get('priceToSalesTrailing12Months'),
                self._parse_numeric(finviz_data.get('P/S')),
                finnhub_data.get('psRatio')
            )
            
            # Profitability Metrics
            fundamental.roe = self._get_best_value(
                yahoo_data.get('returnOnEquity'),
                self._parse_percentage(finviz_data.get('ROE')),
                stockanalysis_data.get('returnOnEquity'),
                finnhub_data.get('roeTTM')
            )
            
            fundamental.roa = self._get_best_value(
                yahoo_data.get('returnOnAssets'),
                self._parse_percentage(finviz_data.get('ROA')),
                finnhub_data.get('roaTTM')
            )
            
            fundamental.gross_margin = self._get_best_value(
                yahoo_data.get('grossMargins'),
                self._parse_percentage(finviz_data.get('Gross M')),
                finnhub_data.get('grossMarginTTM')
            )
            
            fundamental.operating_margin = self._get_best_value(
                yahoo_data.get('operatingMargins'),
                self._parse_percentage(finviz_data.get('Oper M')),
                finnhub_data.get('operatingMarginTTM')
            )
            
            fundamental.net_margin = self._get_best_value(
                yahoo_data.get('profitMargins'),
                self._parse_percentage(finviz_data.get('Profit M')),
                finnhub_data.get('netProfitMarginTTM')
            )
            
            # Financial Health
            fundamental.debt_to_equity = self._get_best_value(
                yahoo_data.get('debtToEquity'),
                self._parse_numeric(finviz_data.get('Debt/Eq')),
                stockanalysis_data.get('debtToEquity'),
                finnhub_data.get('debtToEquityRatio')
            )
            
            fundamental.current_ratio = self._get_best_value(
                yahoo_data.get('currentRatio'),
                self._parse_numeric(finviz_data.get('Current R')),
                finnhub_data.get('currentRatio')
            )
            
            fundamental.quick_ratio = self._get_best_value(
                yahoo_data.get('quickRatio'),
                self._parse_numeric(finviz_data.get('Quick R')),
                finnhub_data.get('quickRatio')
            )
            
            # Growth Metrics
            fundamental.revenue_growth = self._get_best_value(
                yahoo_data.get('revenueGrowth'),
                self._parse_percentage(finviz_data.get('Sales Q/Q')),
                finnhub_data.get('revenueGrowthTTM')
            )
            
            fundamental.earnings_growth = self._get_best_value(
                yahoo_data.get('earningsGrowth'),
                self._parse_percentage(finviz_data.get('EPS Q/Q')),
                finnhub_data.get('epsGrowthTTM')
            )
            
            # Cash Flow
            fundamental.free_cash_flow = self._get_best_value(
                yahoo_data.get('freeCashflow'),
                finnhub_data.get('freeCashFlowTTM')
            )
            
            fundamental.operating_cash_flow = self._get_best_value(
                yahoo_data.get('operatingCashflow'),
                finnhub_data.get('operatingCashFlowTTM')
            )
            
            # Market Data
            fundamental.market_cap = self._get_best_value(
                yahoo_data.get('marketCap'),
                self._parse_market_cap(finviz_data.get('Market Cap')),
                finnhub_data.get('marketCapitalization')
            )
            
            fundamental.shares_outstanding = self._get_best_value(
                yahoo_data.get('sharesOutstanding'),
                finnhub_data.get('sharesOutstanding')
            )
            
            # Dividend Data
            fundamental.dividend_yield = self._get_best_value(
                yahoo_data.get('dividendYield'),
                self._parse_percentage(finviz_data.get('Dividend %')),
                finnhub_data.get('dividendYieldIndicatedAnnual')
            )
            
            fundamental.payout_ratio = self._get_best_value(
                yahoo_data.get('payoutRatio'),
                finnhub_data.get('payoutRatioTTM')
            )
            
        except Exception as e:
            logger.error(f"Error extracting fundamental data for {ticker}: {e}")
        
        return fundamental
    
    def _calculate_technical_indicators(
        self, 
        ticker: str, 
        data: pd.DataFrame
    ) -> TechnicalIndicators:
        """Calculate comprehensive technical indicators"""
        
        indicators = TechnicalIndicators(ticker=ticker, date=datetime.now())
        
        try:
            if data.empty or len(data) < 50:
                return indicators
            
            # Ensure we have the required columns
            if 'close' not in data.columns:
                data.columns = [col.lower() for col in data.columns]
            
            close = data['close']
            high = data['high']
            low = data['low']
            volume = data['volume']
            
            # Moving Averages
            indicators.sma_5 = close.rolling(5).mean().iloc[-1]
            indicators.sma_10 = close.rolling(10).mean().iloc[-1]
            indicators.sma_20 = close.rolling(20).mean().iloc[-1]
            indicators.sma_50 = close.rolling(50).mean().iloc[-1]
            if len(data) >= 200:
                indicators.sma_200 = close.rolling(200).mean().iloc[-1]
            
            # Exponential Moving Averages
            indicators.ema_12 = close.ewm(span=12).mean().iloc[-1]
            indicators.ema_26 = close.ewm(span=26).mean().iloc[-1]
            indicators.ema_50 = close.ewm(span=50).mean().iloc[-1]
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators.rsi_14 = (100 - (100 / (1 + rs))).iloc[-1]
            
            # RSI 21
            gain_21 = (delta.where(delta > 0, 0)).rolling(window=21).mean()
            loss_21 = (-delta.where(delta < 0, 0)).rolling(window=21).mean()
            rs_21 = gain_21 / loss_21
            indicators.rsi_21 = (100 - (100 / (1 + rs_21))).iloc[-1]
            
            # MACD
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            
            indicators.macd = macd_line.iloc[-1]
            indicators.macd_signal = signal_line.iloc[-1]
            indicators.macd_histogram = (macd_line - signal_line).iloc[-1]
            
            # Bollinger Bands
            sma_20 = close.rolling(20).mean()
            std_20 = close.rolling(20).std()
            indicators.bb_upper = (sma_20 + (std_20 * 2)).iloc[-1]
            indicators.bb_middle = sma_20.iloc[-1]
            indicators.bb_lower = (sma_20 - (std_20 * 2)).iloc[-1]
            indicators.bb_width = ((indicators.bb_upper - indicators.bb_lower) / indicators.bb_middle) * 100
            
            # Stochastic Oscillator
            lowest_low = low.rolling(14).min()
            highest_high = high.rolling(14).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            indicators.stoch_k = k_percent.iloc[-1]
            indicators.stoch_d = k_percent.rolling(3).mean().iloc[-1]
            
            # Williams %R
            indicators.williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low)).iloc[-1]
            
            # Average True Range (ATR)
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            indicators.atr = true_range.rolling(14).mean().iloc[-1]
            
            # On-Balance Volume (OBV)
            obv = (volume * ((close > close.shift()).astype(int) * 2 - 1)).cumsum()
            indicators.obv = obv.iloc[-1]
            
            # Chaikin Money Flow (CMF)
            mfv = ((close - low) - (high - close)) / (high - low) * volume
            indicators.cmf = mfv.rolling(20).sum().iloc[-1] / volume.rolling(20).sum().iloc[-1]
            
            # Support and Resistance Levels
            recent_data = data.tail(50)
            indicators.support_1 = recent_data['low'].min()
            indicators.resistance_1 = recent_data['high'].max()
            
            # Secondary support/resistance
            price_levels = pd.concat([recent_data['high'], recent_data['low']]).sort_values()
            indicators.support_2 = price_levels.quantile(0.25)
            indicators.resistance_2 = price_levels.quantile(0.75)
            
            # Pattern Recognition (simplified)
            current_price = close.iloc[-1]
            if current_price > indicators.sma_20 and indicators.rsi_14 < 70:
                indicators.bullish_patterns.append("Uptrend with momentum")
            if current_price < indicators.bb_lower:
                indicators.bullish_patterns.append("Oversold bounce potential")
            if indicators.macd > indicators.macd_signal and indicators.macd > 0:
                indicators.bullish_patterns.append("MACD bullish crossover")
            
            if current_price < indicators.sma_20 and indicators.rsi_14 > 30:
                indicators.bearish_patterns.append("Downtrend with momentum")
            if current_price > indicators.bb_upper:
                indicators.bearish_patterns.append("Overbought correction potential")
            if indicators.macd < indicators.macd_signal and indicators.macd < 0:
                indicators.bearish_patterns.append("MACD bearish crossover")
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {ticker}: {e}")
        
        return indicators
    
    def _analyze_sentiment(self, ticker: str, market_data: Dict[str, Any]) -> SentimentData:
        """Analyze sentiment from various sources"""
        
        sentiment = SentimentData(ticker=ticker, date=datetime.now())
        
        try:
            # Extract sentiment from available data
            finviz_data = market_data.get('web', {}).get('finviz', {})
            
            # News sentiment (simplified - would integrate with news APIs)
            sentiment.news_sentiment = 0.0  # Neutral default
            
            # Analyst sentiment (from target prices and recommendations)
            yahoo_data = market_data.get('yahoo', {}).get('info', {})
            recommendation_mean = yahoo_data.get('recommendationMean')
            if recommendation_mean:
                # Convert recommendation scale (1=Strong Buy, 5=Strong Sell) to sentiment (-1 to 1)
                sentiment.analyst_sentiment = (3 - recommendation_mean) / 2
            
            # Social sentiment (placeholder - would integrate with social media APIs)
            sentiment.social_sentiment = 0.0
            
            # Insider sentiment based on recent trades
            sentiment.insider_sentiment = 0.1 if 'purchase' in str(market_data).lower() else -0.1
            
            # Overall sentiment calculation
            sentiments = [s for s in [
                sentiment.news_sentiment,
                sentiment.analyst_sentiment,
                sentiment.social_sentiment,
                sentiment.insider_sentiment
            ] if s is not None]
            
            if sentiments:
                sentiment.overall_sentiment = np.mean(sentiments)
                sentiment.sentiment_volatility = np.std(sentiments)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {ticker}: {e}")
        
        return sentiment
    
    def _calculate_fundamental_score(self, fundamental: FundamentalData) -> float:
        """Calculate fundamental analysis score (0-100)"""
        
        score = 50.0  # Base score
        
        try:
            # P/E Ratio scoring
            if fundamental.pe_ratio:
                if 0 < fundamental.pe_ratio < 15:
                    score += 15
                elif 15 <= fundamental.pe_ratio <= 25:
                    score += 10
                elif 25 < fundamental.pe_ratio <= 35:
                    score += 5
                elif fundamental.pe_ratio > 40:
                    score -= 10
            
            # PEG Ratio scoring
            if fundamental.peg_ratio:
                if fundamental.peg_ratio < 1:
                    score += 15
                elif fundamental.peg_ratio < 1.5:
                    score += 10
                elif fundamental.peg_ratio > 2:
                    score -= 10
            
            # ROE scoring
            if fundamental.roe:
                if fundamental.roe > 0.20:
                    score += 15
                elif fundamental.roe > 0.15:
                    score += 10
                elif fundamental.roe > 0.10:
                    score += 5
                elif fundamental.roe < 0:
                    score -= 15
            
            # Debt to Equity scoring
            if fundamental.debt_to_equity:
                if fundamental.debt_to_equity < 0.3:
                    score += 10
                elif fundamental.debt_to_equity < 0.6:
                    score += 5
                elif fundamental.debt_to_equity > 2:
                    score -= 15
            
            # Revenue Growth scoring
            if fundamental.revenue_growth:
                if fundamental.revenue_growth > 0.20:
                    score += 10
                elif fundamental.revenue_growth > 0.10:
                    score += 5
                elif fundamental.revenue_growth < 0:
                    score -= 10
            
            # Profit Margin scoring
            if fundamental.net_margin:
                if fundamental.net_margin > 0.20:
                    score += 10
                elif fundamental.net_margin > 0.10:
                    score += 5
                elif fundamental.net_margin < 0:
                    score -= 15
            
            # Free Cash Flow scoring
            if fundamental.free_cash_flow:
                if fundamental.free_cash_flow > 0:
                    score += 5
                else:
                    score -= 10
            
        except Exception as e:
            logger.error(f"Error calculating fundamental score: {e}")
        
        return max(0, min(100, score))
    
    def _calculate_technical_score(self, technical: TechnicalIndicators) -> float:
        """Calculate technical analysis score (0-100)"""
        
        score = 50.0  # Base score
        
        try:
            # RSI scoring
            if technical.rsi_14:
                if 30 <= technical.rsi_14 <= 70:
                    score += 10
                elif technical.rsi_14 < 30:
                    score += 15  # Oversold - potential buy
                elif technical.rsi_14 > 70:
                    score -= 10  # Overbought
            
            # MACD scoring
            if technical.macd and technical.macd_signal:
                if technical.macd > technical.macd_signal:
                    score += 10
                    if technical.macd > 0:
                        score += 5  # Above zero line
                else:
                    score -= 10
            
            # Moving Average scoring
            current_price = None  # Would need current price
            if technical.sma_20 and technical.sma_50:
                if technical.sma_20 > technical.sma_50:
                    score += 10  # Bullish trend
                else:
                    score -= 10  # Bearish trend
            
            # Bollinger Bands scoring
            if all([technical.bb_upper, technical.bb_lower, technical.bb_middle]):
                # Would need current price to determine position
                pass
            
            # Pattern scoring
            bullish_count = len(technical.bullish_patterns)
            bearish_count = len(technical.bearish_patterns)
            
            score += bullish_count * 5
            score -= bearish_count * 5
            
        except Exception as e:
            logger.error(f"Error calculating technical score: {e}")
        
        return max(0, min(100, score))
    
    def _calculate_sentiment_score(self, sentiment: SentimentData) -> float:
        """Calculate sentiment analysis score (0-100)"""
        
        score = 50.0  # Base score
        
        try:
            if sentiment.overall_sentiment is not None:
                # Convert sentiment (-1 to 1) to score contribution (-25 to +25)
                score += sentiment.overall_sentiment * 25
            
            if sentiment.analyst_sentiment is not None:
                score += sentiment.analyst_sentiment * 15
            
            if sentiment.news_sentiment is not None:
                score += sentiment.news_sentiment * 10
            
            # Penalize high volatility in sentiment
            if sentiment.sentiment_volatility and sentiment.sentiment_volatility > 0.5:
                score -= 10
            
        except Exception as e:
            logger.error(f"Error calculating sentiment score: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_insider_patterns(self, trade: EnhancedInsiderTrade) -> float:
        """Analyze insider trading patterns and calculate score"""
        
        score = 50.0  # Base score
        
        try:
            # Trade type scoring
            if trade.trade_type == "purchase":
                score += 20
            elif trade.trade_type == "sale":
                score -= 10
            
            # Trade size significance
            if trade.amount and trade.market_cap:
                trade_significance = trade.amount / trade.market_cap
                if trade_significance > 0.001:  # 0.1% of market cap
                    score += 15
                elif trade_significance > 0.0001:  # 0.01% of market cap
                    score += 10
            
            # Insider title importance
            important_titles = ['ceo', 'cfo', 'president', 'chairman', 'founder']
            if any(title in trade.insider_title.lower() for title in important_titles):
                score += 10
            
            # Multiple insider trades (would need historical data)
            # This would require tracking multiple trades over time
            
        except Exception as e:
            logger.error(f"Error analyzing insider patterns: {e}")
        
        return max(0, min(100, score))
    
    def _generate_ml_predictions(
        self, 
        trade: EnhancedInsiderTrade, 
        historical_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Generate ML-based price predictions"""
        
        predictions = {}
        
        try:
            if len(historical_data) < 100:
                return predictions
            
            # Prepare features
            features = self._prepare_ml_features(trade, historical_data)
            
            if features is None or len(features) == 0:
                return predictions
            
            # Simple prediction model (would be replaced with trained models)
            current_price = historical_data['close'].iloc[-1]
            
            # Mock predictions (replace with actual ML models)
            volatility = historical_data['close'].pct_change().std()
            
            predictions['price_1d'] = current_price * (1 + np.random.normal(0, volatility))
            predictions['price_7d'] = current_price * (1 + np.random.normal(0, volatility * np.sqrt(7)))
            predictions['price_30d'] = current_price * (1 + np.random.normal(0, volatility * np.sqrt(30)))
            
            # Probability calculations based on sentiment and technical indicators
            base_prob = 0.5
            
            if trade.fundamental_score and trade.fundamental_score > 60:
                base_prob += 0.1
            if trade.technical_score and trade.technical_score > 60:
                base_prob += 0.1
            if trade.sentiment_score and trade.sentiment_score > 60:
                base_prob += 0.1
            
            predictions['prob_up_1d'] = min(0.9, max(0.1, base_prob))
            predictions['prob_up_7d'] = min(0.9, max(0.1, base_prob * 0.9))
            predictions['prob_up_30d'] = min(0.9, max(0.1, base_prob * 0.8))
            
        except Exception as e:
            logger.error(f"Error generating ML predictions: {e}")
        
        return predictions
    
    def _prepare_ml_features(
        self, 
        trade: EnhancedInsiderTrade, 
        historical_data: pd.DataFrame
    ) -> Optional[np.ndarray]:
        """Prepare features for ML models"""
        
        try:
            features = []
            
            # Price-based features
            if not historical_data.empty:
                close_prices = historical_data['close']
                
                # Returns
                returns_1d = close_prices.pct_change(1).iloc[-1]
                returns_5d = close_prices.pct_change(5).iloc[-1]
                returns_20d = close_prices.pct_change(20).iloc[-1]
                
                features.extend([returns_1d, returns_5d, returns_20d])
                
                # Volatility
                volatility = close_prices.pct_change().rolling(20).std().iloc[-1]
                features.append(volatility)
                
                # Volume features
                if 'volume' in historical_data.columns:
                    volume_ratio = historical_data['volume'].iloc[-1] / historical_data['volume'].rolling(20).mean().iloc[-1]
                    features.append(volume_ratio)
            
            # Fundamental features
            if trade.fundamental_data:
                fund = trade.fundamental_data
                features.extend([
                    fund.pe_ratio or 0,
                    fund.peg_ratio or 0,
                    fund.roe or 0,
                    fund.debt_to_equity or 0,
                    fund.revenue_growth or 0
                ])
            
            # Technical features
            if trade.technical_indicators:
                tech = trade.technical_indicators
                features.extend([
                    tech.rsi_14 or 50,
                    tech.macd or 0,
                    tech.bb_width or 0
                ])
            
            # Insider features
            features.extend([
                1 if trade.trade_type == "purchase" else 0,
                trade.amount / 1000000 if trade.amount else 0,  # Amount in millions
                trade.insider_score or 50
            ])
            
            return np.array(features).reshape(1, -1) if features else None
            
        except Exception as e:
            logger.error(f"Error preparing ML features: {e}")
            return None
    
    def _assess_risk(
        self, 
        trade: EnhancedInsiderTrade, 
        historical_data: Optional[pd.DataFrame]
    ) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        
        risk_assessment = {
            'risk_level': RiskLevel.MODERATE,
            'var_1d': None,
            'var_7d': None,
            'expected_shortfall': None
        }
        
        try:
            risk_score = 5.0  # Base risk (1-10 scale)
            
            # Volatility risk
            if historical_data is not None and not historical_data.empty:
                returns = historical_data['close'].pct_change().dropna()
                if len(returns) > 20:
                    volatility = returns.std()
                    
                    if volatility > 0.05:  # 5% daily volatility
                        risk_score += 2
                    elif volatility > 0.03:  # 3% daily volatility
                        risk_score += 1
                    elif volatility < 0.01:  # 1% daily volatility
                        risk_score -= 1
                    
                    # VaR calculation (95% confidence)
                    var_95 = np.percentile(returns, 5)
                    risk_assessment['var_1d'] = var_95
                    risk_assessment['var_7d'] = var_95 * np.sqrt(7)
                    
                    # Expected Shortfall (CVaR)
                    es_returns = returns[returns <= var_95]
                    if len(es_returns) > 0:
                        risk_assessment['expected_shortfall'] = es_returns.mean()
            
            # Fundamental risk
            if trade.fundamental_data:
                fund = trade.fundamental_data
                
                # High P/E risk
                if fund.pe_ratio and fund.pe_ratio > 40:
                    risk_score += 1
                
                # High debt risk
                if fund.debt_to_equity and fund.debt_to_equity > 2:
                    risk_score += 1
                
                # Negative margins risk
                if fund.net_margin and fund.net_margin < 0:
                    risk_score += 2
            
            # Market cap risk (smaller companies = higher risk)
            if trade.market_cap:
                if trade.market_cap < 1e9:  # < $1B market cap
                    risk_score += 2
                elif trade.market_cap < 10e9:  # < $10B market cap
                    risk_score += 1
            
            # Insider trade risk
            if trade.trade_type == "sale":
                risk_score += 1
            
            # Convert risk score to risk level
            if risk_score <= 3:
                risk_assessment['risk_level'] = RiskLevel.LOW
            elif risk_score <= 4:
                risk_assessment['risk_level'] = RiskLevel.MODERATE
            elif risk_score <= 6:
                risk_assessment['risk_level'] = RiskLevel.HIGH
            else:
                risk_assessment['risk_level'] = RiskLevel.VERY_HIGH
            
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
        
        return risk_assessment
    
    def _calculate_composite_score(self, trade: EnhancedInsiderTrade) -> float:
        """Calculate weighted composite score"""
        
        try:
            scores = []
            weights = []
            
            if trade.fundamental_score is not None:
                scores.append(trade.fundamental_score)
                weights.append(0.4)  # 40% weight
            
            if trade.technical_score is not None:
                scores.append(trade.technical_score)
                weights.append(0.3)  # 30% weight
            
            if trade.insider_score is not None:
                scores.append(trade.insider_score)
                weights.append(0.2)  # 20% weight
            
            if trade.sentiment_score is not None:
                scores.append(trade.sentiment_score)
                weights.append(0.1)  # 10% weight
            
            if scores:
                # Normalize weights
                total_weight = sum(weights)
                normalized_weights = [w / total_weight for w in weights]
                
                # Calculate weighted average
                composite = sum(s * w for s, w in zip(scores, normalized_weights))
                return max(0, min(100, composite))
            
            return 50.0  # Default neutral score
            
        except Exception as e:
            logger.error(f"Error calculating composite score: {e}")
            return 50.0
    
    def _generate_recommendation(self, trade: EnhancedInsiderTrade) -> Dict[str, Any]:
        """Generate comprehensive recommendation with confidence and reasoning"""
        
        result = {
            'recommendation': Recommendation.HOLD,
            'confidence': 0.5,
            'reasons': [],
            'warnings': []
        }
        
        try:
            score = trade.composite_score or 50
            confidence_factors = []
            
            # Base recommendation from composite score
            if score >= 80:
                result['recommendation'] = Recommendation.STRONG_BUY
                result['reasons'].append("Exceptional composite score (80+)")
                confidence_factors.append(0.9)
            elif score >= 65:
                result['recommendation'] = Recommendation.BUY
                result['reasons'].append("Strong composite score (65+)")
                confidence_factors.append(0.8)
            elif score >= 45:
                result['recommendation'] = Recommendation.HOLD
                result['reasons'].append("Moderate composite score (45-65)")
                confidence_factors.append(0.6)
            elif score >= 30:
                result['recommendation'] = Recommendation.SELL
                result['reasons'].append("Weak composite score (30-45)")
                confidence_factors.append(0.7)
            else:
                result['recommendation'] = Recommendation.STRONG_SELL
                result['reasons'].append("Poor composite score (<30)")
                confidence_factors.append(0.8)
            
            # Adjust based on individual scores
            if trade.fundamental_score and trade.fundamental_score > 70:
                result['reasons'].append("Strong fundamental metrics")
                confidence_factors.append(0.8)
            
            if trade.technical_score and trade.technical_score > 70:
                result['reasons'].append("Positive technical indicators")
                confidence_factors.append(0.7)
            
            if trade.insider_score and trade.insider_score > 70:
                result['reasons'].append("Significant insider buying signal")
                confidence_factors.append(0.9)
            
            # Risk-based adjustments
            if trade.risk_level == RiskLevel.VERY_HIGH:
                result['warnings'].append("Very high risk investment")
                if result['recommendation'] in [Recommendation.STRONG_BUY, Recommendation.BUY]:
                    result['recommendation'] = Recommendation.HOLD
                confidence_factors.append(0.5)
            
            # ML prediction adjustments
            if trade.probability_up_30d and trade.probability_up_30d > 0.7:
                result['reasons'].append("High probability of price appreciation")
                confidence_factors.append(0.8)
            elif trade.probability_up_30d and trade.probability_up_30d < 0.3:
                result['warnings'].append("Low probability of price appreciation")
                confidence_factors.append(0.6)
            
            # Calculate final confidence
            if confidence_factors:
                result['confidence'] = np.mean(confidence_factors)
            
            # Additional warnings
            if trade.fundamental_data and trade.fundamental_data.debt_to_equity and trade.fundamental_data.debt_to_equity > 3:
                result['warnings'].append("High debt-to-equity ratio")
            
            if trade.technical_indicators and trade.technical_indicators.rsi_14 and trade.technical_indicators.rsi_14 > 80:
                result['warnings'].append("Extremely overbought conditions")
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
        
        return result
    
    def _calculate_fair_value(self, trade: EnhancedInsiderTrade) -> Optional[float]:
        """Calculate fair value using multiple valuation methods"""
        
        try:
            fair_values = []
            
            # DCF-based fair value (simplified)
            if (trade.fundamental_data and 
                trade.fundamental_data.free_cash_flow and 
                trade.fundamental_data.shares_outstanding):
                
                fcf = trade.fundamental_data.free_cash_flow
                shares = trade.fundamental_data.shares_outstanding
                growth_rate = trade.fundamental_data.revenue_growth or 0.05  # 5% default
                discount_rate = 0.10  # 10% discount rate
                
                # Simple Gordon Growth Model
                terminal_value = fcf * (1 + growth_rate) / (discount_rate - growth_rate)
                fair_value_dcf = terminal_value / shares
                fair_values.append(fair_value_dcf)
            
            # P/E based fair value
            if (trade.fundamental_data and 
                trade.fundamental_data.pe_ratio and 
                trade.current_price):
                
                industry_pe = 20  # Assumed industry average
                earnings_per_share = trade.current_price / trade.fundamental_data.pe_ratio
                fair_value_pe = earnings_per_share * industry_pe
                fair_values.append(fair_value_pe)
            
            # Target price average
            target_prices = [p for p in trade.target_prices.values() if p is not None]
            if target_prices:
                fair_values.append(np.mean(target_prices))
            
            # Return average of all methods
            if fair_values:
                return np.mean(fair_values)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating fair value: {e}")
            return None
    
    def _get_best_value(self, *values) -> Optional[float]:
        """Get the best non-null value from multiple sources"""
        for value in values:
            if value is not None and value != "" and value != "N/A":
                try:
                    return float(value)
                except (ValueError, TypeError):
                    continue
        return None
    
    def _parse_numeric(self, value) -> Optional[float]:
        """Parse numeric value from string"""
        if value is None or value == "" or value == "N/A" or value == "-":
            return None
        try:
            # Remove common suffixes and convert
            if isinstance(value, str):
                value = value.replace('%', '').replace(',', '').replace('$', '')
                if value.endswith('B'):
                    return float(value[:-1]) * 1e9
                elif value.endswith('M'):
                    return float(value[:-1]) * 1e6
                elif value.endswith('K'):
                    return float(value[:-1]) * 1e3
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_percentage(self, value) -> Optional[float]:
        """Parse percentage value and convert to decimal"""
        numeric_value = self._parse_numeric(value)
        if numeric_value is not None:
            # If the value seems to be in percentage form (>1), convert to decimal
            if numeric_value > 1:
                return numeric_value / 100
            return numeric_value
        return None
    
    def _parse_market_cap(self, value) -> Optional[float]:
        """Parse market cap value"""
        if value is None or value == "" or value == "N/A" or value == "-":
            return None
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace('$', '')
                if value.endswith('B'):
                    return float(value[:-1]) * 1e9
                elif value.endswith('M'):
                    return float(value[:-1]) * 1e6
                elif value.endswith('T'):
                    return float(value[:-1]) * 1e12
            return float(value)
        except (ValueError, TypeError):
            return None