import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from models.trade_models import TechnicalAnalysis, Recommendation
from utils.logging_config import logger

class TechnicalAnalyzer:
    """Technical analysis with multiple indicators"""
    
    def __init__(self):
        self.min_data_points = 50
    
    def analyze_stock(self, ticker: str, price_data: pd.DataFrame) -> Optional[TechnicalAnalysis]:
        """Perform comprehensive technical analysis"""
        
        if price_data.empty or len(price_data) < self.min_data_points:
            logger.warning(f"Insufficient data for technical analysis of {ticker}")
            return None
        
        try:
            # Ensure we have the required columns
            required_columns = ['close', 'high', 'low', 'volume']
            if not all(col in price_data.columns for col in required_columns):
                logger.warning(f"Missing required columns for {ticker}")
                return None
            
            analysis = TechnicalAnalysis(ticker=ticker)
            
            # Moving Averages
            analysis.sma20 = self._calculate_sma(price_data['close'], 20)
            analysis.ema50 = self._calculate_ema(price_data['close'], 50)
            
            # RSI
            analysis.rsi = self._calculate_rsi(price_data['close'])
            
            # MACD
            macd_line, macd_signal = self._calculate_macd(price_data['close'])
            analysis.macd = macd_line
            analysis.macd_signal = macd_signal
            
            # Bollinger Bands
            bb_upper, bb_lower = self._calculate_bollinger_bands(price_data['close'])
            analysis.bb_upper = bb_upper
            analysis.bb_lower = bb_lower
            
            # Support and Resistance
            analysis.support, analysis.resistance = self._calculate_support_resistance(
                price_data['high'], price_data['low']
            )
            
            # Trend Analysis
            analysis.trend = self._determine_trend(analysis.sma20, analysis.ema50, price_data['close'])
            
            logger.debug(f"Technical analysis completed for {ticker}")
            return analysis
            
        except Exception as e:
            logger.error(f"Technical analysis failed for {ticker}: {e}")
            return None
    
    def _calculate_sma(self, prices: pd.Series, window: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        try:
            if len(prices) >= window:
                sma = SMAIndicator(prices, window=window).sma_indicator()
                return float(sma.iloc[-1]) if not sma.empty else None
        except Exception as e:
            logger.warning(f"SMA calculation failed: {e}")
        return None
    
    def _calculate_ema(self, prices: pd.Series, window: int) -> Optional[float]:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) >= window:
                ema = EMAIndicator(prices, window=window).ema_indicator()
                return float(ema.iloc[-1]) if not ema.empty else None
        except Exception as e:
            logger.warning(f"EMA calculation failed: {e}")
        return None
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index"""
        try:
            if len(prices) >= window + 1:
                rsi = RSIIndicator(prices, window=window).rsi()
                return float(rsi.iloc[-1]) if not rsi.empty else None
        except Exception as e:
            logger.warning(f"RSI calculation failed: {e}")
        return None
    
    def _calculate_macd(self, prices: pd.Series) -> tuple[Optional[float], Optional[float]]:
        """Calculate MACD and Signal line"""
        try:
            if len(prices) >= 34:  # Need at least 34 periods for MACD
                macd_indicator = MACD(prices)
                macd_line = macd_indicator.macd()
                macd_signal = macd_indicator.macd_signal()
                
                macd_val = float(macd_line.iloc[-1]) if not macd_line.empty else None
                signal_val = float(macd_signal.iloc[-1]) if not macd_signal.empty else None
                
                return macd_val, signal_val
        except Exception as e:
            logger.warning(f"MACD calculation failed: {e}")
        return None, None
    
    def _calculate_bollinger_bands(self, prices: pd.Series, window: int = 20) -> tuple[Optional[float], Optional[float]]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) >= window:
                bb = BollingerBands(prices, window=window)
                upper = bb.bollinger_hband()
                lower = bb.bollinger_lband()
                
                upper_val = float(upper.iloc[-1]) if not upper.empty else None
                lower_val = float(lower.iloc[-1]) if not lower.empty else None
                
                return upper_val, lower_val
        except Exception as e:
            logger.warning(f"Bollinger Bands calculation failed: {e}")
        return None, None
    
    def _calculate_support_resistance(self, highs: pd.Series, lows: pd.Series, window: int = 20) -> tuple[Optional[float], Optional[float]]:
        """Calculate support and resistance levels"""
        try:
            if len(highs) >= window and len(lows) >= window:
                # Use rolling windows to find recent support/resistance
                recent_highs = highs.rolling(window=window).max().iloc[-10:]
                recent_lows = lows.rolling(window=window).min().iloc[-10:]
                
                resistance = float(recent_highs.mean()) if not recent_highs.empty else None
                support = float(recent_lows.mean()) if not recent_lows.empty else None
                
                return support, resistance
        except Exception as e:
            logger.warning(f"Support/Resistance calculation failed: {e}")
        return None, None
    
    def _determine_trend(self, sma20: Optional[float], ema50: Optional[float], prices: pd.Series) -> str:
        """Determine overall trend"""
        try:
            if sma20 is None or ema50 is None or prices.empty:
                return "Neutral"
            
            current_price = float(prices.iloc[-1])
            
            # Multiple criteria for trend determination
            trend_signals = []
            
            # SMA vs EMA
            if sma20 > ema50:
                trend_signals.append("bullish")
            elif sma20 < ema50:
                trend_signals.append("bearish")
            
            # Price vs moving averages
            if current_price > sma20 and current_price > ema50:
                trend_signals.append("bullish")
            elif current_price < sma20 and current_price < ema50:
                trend_signals.append("bearish")
            
            # Price momentum (last 5 days)
            if len(prices) >= 5:
                recent_change = (prices.iloc[-1] - prices.iloc[-5]) / prices.iloc[-5]
                if recent_change > 0.02:  # 2% increase
                    trend_signals.append("bullish")
                elif recent_change < -0.02:  # 2% decrease
                    trend_signals.append("bearish")
            
            # Determine overall trend
            bullish_count = trend_signals.count("bullish")
            bearish_count = trend_signals.count("bearish")
            
            if bullish_count > bearish_count:
                return "Bullish"
            elif bearish_count > bullish_count:
                return "Bearish"
            else:
                return "Neutral"
                
        except Exception as e:
            logger.warning(f"Trend determination failed: {e}")
            return "Neutral"
    
    def generate_recommendation(self, analysis: TechnicalAnalysis, current_price: float, target_price: Optional[float] = None) -> Recommendation:
        """Generate trading recommendation based on technical analysis"""
        
        if not analysis:
            return Recommendation.HOLD
        
        score = 0
        
        try:
            # RSI Analysis
            if analysis.rsi:
                if analysis.rsi < 30:
                    score += 2  # Oversold - buy signal
                elif analysis.rsi > 70:
                    score -= 1  # Overbought - sell signal
                elif 40 <= analysis.rsi <= 60:
                    score += 1  # Neutral zone - slight positive
            
            # MACD Analysis
            if analysis.macd and analysis.macd_signal:
                if analysis.macd > analysis.macd_signal and analysis.macd > 0:
                    score += 2  # Bullish crossover above zero
                elif analysis.macd < analysis.macd_signal and analysis.macd < 0:
                    score -= 2  # Bearish crossover below zero
                elif analysis.macd > analysis.macd_signal:
                    score += 1  # Bullish crossover
            
            # Trend Analysis
            if analysis.trend == "Bullish":
                score += 2
            elif analysis.trend == "Bearish":
                score -= 2
            
            # Price vs Moving Averages
            if analysis.sma20 and current_price > analysis.sma20:
                score += 1
            if analysis.ema50 and current_price > analysis.ema50:
                score += 1
            
            # Bollinger Bands Analysis
            if analysis.bb_upper and analysis.bb_lower:
                if current_price < analysis.bb_lower:
                    score += 1  # Near lower band - potential buy
                elif current_price > analysis.bb_upper:
                    score -= 1  # Near upper band - potential sell
            
            # Target Price Analysis
            if target_price and target_price > current_price * 1.1:
                score += 1  # Target significantly above current price
            elif target_price and target_price < current_price * 0.9:
                score -= 1  # Target below current price
            
            # Convert score to recommendation
            if score >= 4:
                return Recommendation.STRONG_BUY
            elif score >= 2:
                return Recommendation.BUY
            elif score >= -1:
                return Recommendation.HOLD
            elif score >= -3:
                return Recommendation.SELL
            else:
                return Recommendation.STRONG_SELL
                
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return Recommendation.HOLD