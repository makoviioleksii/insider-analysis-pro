import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

from models.enhanced_models import Portfolio, EnhancedInsiderTrade, RiskLevel
from utils.logging_config import logger
from config.settings import settings

class RiskManager:
    """Advanced risk management and portfolio optimization"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
        self.confidence_levels = [0.90, 0.95, 0.99]
        
        # Risk limits
        self.max_position_size = settings.MAX_POSITION_SIZE
        self.max_sector_allocation = 0.30  # 30% max in any sector
        self.max_correlation = 0.70  # Maximum correlation between positions
        
    def calculate_portfolio_risk(
        self, 
        portfolio: Portfolio, 
        price_data: Dict[str, pd.DataFrame],
        correlation_matrix: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive portfolio risk metrics"""
        
        risk_metrics = {
            'var_95': None,
            'var_99': None,
            'expected_shortfall_95': None,
            'expected_shortfall_99': None,
            'max_drawdown': None,
            'volatility': None,
            'sharpe_ratio': None,
            'sortino_ratio': None,
            'beta': None,
            'tracking_error': None,
            'information_ratio': None,
            'concentration_risk': None,
            'liquidity_risk': None
        }
        
        try:
            if not portfolio.positions:
                return risk_metrics
            
            # Calculate portfolio returns
            portfolio_returns = self._calculate_portfolio_returns(portfolio, price_data)
            
            if portfolio_returns is None or len(portfolio_returns) < 30:
                logger.warning("Insufficient data for risk calculation")
                return risk_metrics
            
            # Value at Risk (VaR)
            risk_metrics['var_95'] = self._calculate_var(portfolio_returns, 0.95)
            risk_metrics['var_99'] = self._calculate_var(portfolio_returns, 0.99)
            
            # Expected Shortfall (Conditional VaR)
            risk_metrics['expected_shortfall_95'] = self._calculate_expected_shortfall(portfolio_returns, 0.95)
            risk_metrics['expected_shortfall_99'] = self._calculate_expected_shortfall(portfolio_returns, 0.99)
            
            # Maximum Drawdown
            risk_metrics['max_drawdown'] = self._calculate_max_drawdown(portfolio_returns)
            
            # Volatility
            risk_metrics['volatility'] = portfolio_returns.std() * np.sqrt(252)  # Annualized
            
            # Sharpe Ratio
            excess_returns = portfolio_returns.mean() * 252 - self.risk_free_rate
            risk_metrics['sharpe_ratio'] = excess_returns / risk_metrics['volatility'] if risk_metrics['volatility'] > 0 else 0
            
            # Sortino Ratio
            downside_returns = portfolio_returns[portfolio_returns < 0]
            downside_volatility = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            risk_metrics['sortino_ratio'] = excess_returns / downside_volatility if downside_volatility > 0 else 0
            
            # Beta (if benchmark data available)
            # risk_metrics['beta'] = self._calculate_beta(portfolio_returns, benchmark_returns)
            
            # Concentration Risk
            risk_metrics['concentration_risk'] = self._calculate_concentration_risk(portfolio)
            
            # Liquidity Risk
            risk_metrics['liquidity_risk'] = self._calculate_liquidity_risk(portfolio, price_data)
            
            logger.info("Portfolio risk metrics calculated successfully")
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
        
        return risk_metrics
    
    def _calculate_portfolio_returns(
        self, 
        portfolio: Portfolio, 
        price_data: Dict[str, pd.DataFrame]
    ) -> Optional[pd.Series]:
        """Calculate portfolio returns time series"""
        
        try:
            if not portfolio.positions:
                return None
            
            # Get common date range
            all_dates = None
            for ticker in portfolio.positions.keys():
                if ticker in price_data and not price_data[ticker].empty:
                    if all_dates is None:
                        all_dates = price_data[ticker].index
                    else:
                        all_dates = all_dates.intersection(price_data[ticker].index)
            
            if all_dates is None or len(all_dates) < 30:
                return None
            
            # Calculate weighted returns
            portfolio_returns = pd.Series(0.0, index=all_dates)
            total_value = sum(portfolio.positions.values())
            
            for ticker, position_value in portfolio.positions.items():
                if ticker in price_data and not price_data[ticker].empty:
                    ticker_data = price_data[ticker].reindex(all_dates)
                    ticker_returns = ticker_data['close'].pct_change()
                    weight = position_value / total_value
                    portfolio_returns += weight * ticker_returns
            
            return portfolio_returns.dropna()
            
        except Exception as e:
            logger.error(f"Error calculating portfolio returns: {e}")
            return None
    
    def _calculate_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Value at Risk using historical simulation"""
        
        try:
            return np.percentile(returns, (1 - confidence_level) * 100)
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return 0.0
    
    def _calculate_expected_shortfall(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        
        try:
            var = self._calculate_var(returns, confidence_level)
            tail_returns = returns[returns <= var]
            return tail_returns.mean() if len(tail_returns) > 0 else 0.0
        except Exception as e:
            logger.error(f"Error calculating Expected Shortfall: {e}")
            return 0.0
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        
        try:
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            return drawdown.min()
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    def _calculate_concentration_risk(self, portfolio: Portfolio) -> float:
        """Calculate concentration risk using Herfindahl-Hirschman Index"""
        
        try:
            if not portfolio.positions:
                return 0.0
            
            total_value = sum(portfolio.positions.values())
            weights = [value / total_value for value in portfolio.positions.values()]
            hhi = sum(w**2 for w in weights)
            
            # Normalize HHI to 0-1 scale (1 = maximum concentration)
            n = len(weights)
            normalized_hhi = (hhi - 1/n) / (1 - 1/n) if n > 1 else 1.0
            
            return normalized_hhi
            
        except Exception as e:
            logger.error(f"Error calculating concentration risk: {e}")
            return 0.0
    
    def _calculate_liquidity_risk(
        self, 
        portfolio: Portfolio, 
        price_data: Dict[str, pd.DataFrame]
    ) -> float:
        """Calculate liquidity risk based on volume and bid-ask spreads"""
        
        try:
            if not portfolio.positions:
                return 0.0
            
            liquidity_scores = []
            
            for ticker in portfolio.positions.keys():
                if ticker in price_data and not price_data[ticker].empty:
                    data = price_data[ticker]
                    
                    # Volume-based liquidity
                    avg_volume = data['volume'].mean()
                    volume_score = min(1.0, avg_volume / 1000000)  # Normalize by 1M shares
                    
                    # Spread-based liquidity (proxy using high-low spread)
                    avg_spread = ((data['high'] - data['low']) / data['close']).mean()
                    spread_score = max(0.0, 1.0 - avg_spread * 100)  # Lower spread = higher liquidity
                    
                    # Combined liquidity score
                    liquidity_score = (volume_score + spread_score) / 2
                    liquidity_scores.append(liquidity_score)
            
            # Portfolio liquidity risk (inverse of average liquidity)
            avg_liquidity = np.mean(liquidity_scores) if liquidity_scores else 0.5
            return 1.0 - avg_liquidity
            
        except Exception as e:
            logger.error(f"Error calculating liquidity risk: {e}")
            return 0.5
    
    def optimize_portfolio(
        self, 
        expected_returns: pd.Series,
        covariance_matrix: pd.DataFrame,
        risk_tolerance: float = 0.5,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Optimize portfolio using Modern Portfolio Theory"""
        
        try:
            n_assets = len(expected_returns)
            
            if n_assets == 0:
                return {}
            
            # Objective function (maximize Sharpe ratio)
            def objective(weights):
                portfolio_return = np.sum(weights * expected_returns)
                portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
                portfolio_std = np.sqrt(portfolio_variance)
                
                # Sharpe ratio (negative for minimization)
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
                return -sharpe_ratio
            
            # Constraints
            constraints_list = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
            ]
            
            # Individual position limits
            bounds = [(0, self.max_position_size) for _ in range(n_assets)]
            
            # Additional constraints
            if constraints:
                # Sector constraints
                if 'sector_limits' in constraints:
                    for sector, tickers in constraints['sector_limits'].items():
                        sector_indices = [i for i, ticker in enumerate(expected_returns.index) if ticker in tickers]
                        if sector_indices:
                            constraints_list.append({
                                'type': 'ineq',
                                'fun': lambda x, indices=sector_indices: self.max_sector_allocation - np.sum([x[i] for i in indices])
                            })
            
            # Initial guess (equal weights)
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimization
            result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list,
                options={'maxiter': 1000}
            )
            
            if result.success:
                optimal_weights = dict(zip(expected_returns.index, result.x))
                logger.info("Portfolio optimization completed successfully")
                return optimal_weights
            else:
                logger.warning("Portfolio optimization failed, using equal weights")
                return dict(zip(expected_returns.index, initial_weights))
                
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            return {}
    
    def calculate_position_size(
        self, 
        trade: EnhancedInsiderTrade,
        portfolio_value: float,
        risk_per_trade: float = 0.02
    ) -> Dict[str, Any]:
        """Calculate optimal position size based on risk management"""
        
        position_info = {
            'recommended_size': 0.0,
            'max_size': 0.0,
            'risk_adjusted_size': 0.0,
            'stop_loss': None,
            'take_profit': None,
            'risk_reward_ratio': None
        }
        
        try:
            if not trade.current_price:
                return position_info
            
            # Maximum position size based on portfolio rules
            max_position_value = portfolio_value * self.max_position_size
            position_info['max_size'] = max_position_value / trade.current_price
            
            # Risk-based position sizing
            if trade.var_1d:
                # Use VaR for position sizing
                daily_risk = abs(trade.var_1d)
                risk_amount = portfolio_value * risk_per_trade
                shares_by_risk = risk_amount / (daily_risk * trade.current_price)
                position_info['risk_adjusted_size'] = min(shares_by_risk, position_info['max_size'])
            else:
                # Fallback to volatility-based sizing
                position_info['risk_adjusted_size'] = position_info['max_size'] * 0.5
            
            # Kelly Criterion sizing (if we have probability estimates)
            if trade.probability_up_30d and trade.price_prediction_30d:
                win_prob = trade.probability_up_30d
                expected_return = (trade.price_prediction_30d - trade.current_price) / trade.current_price
                
                if expected_return > 0:
                    # Simplified Kelly formula
                    kelly_fraction = (win_prob * expected_return - (1 - win_prob)) / expected_return
                    kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
                    kelly_size = (portfolio_value * kelly_fraction) / trade.current_price
                    position_info['risk_adjusted_size'] = min(position_info['risk_adjusted_size'], kelly_size)
            
            # Final recommended size
            position_info['recommended_size'] = position_info['risk_adjusted_size']
            
            # Stop loss and take profit levels
            if trade.technical_indicators:
                # Support level as stop loss
                if trade.technical_indicators.support_1:
                    position_info['stop_loss'] = trade.technical_indicators.support_1
                else:
                    # Default stop loss at 10%
                    position_info['stop_loss'] = trade.current_price * (1 - settings.STOP_LOSS_PERCENTAGE)
                
                # Resistance level as take profit
                if trade.technical_indicators.resistance_1:
                    position_info['take_profit'] = trade.technical_indicators.resistance_1
                elif trade.fair_value:
                    position_info['take_profit'] = trade.fair_value
                else:
                    # Default take profit at 20%
                    position_info['take_profit'] = trade.current_price * (1 + settings.TAKE_PROFIT_PERCENTAGE)
            
            # Risk-reward ratio
            if position_info['stop_loss'] and position_info['take_profit']:
                risk = trade.current_price - position_info['stop_loss']
                reward = position_info['take_profit'] - trade.current_price
                if risk > 0:
                    position_info['risk_reward_ratio'] = reward / risk
            
            logger.debug(f"Position sizing calculated for {trade.ticker}")
            
        except Exception as e:
            logger.error(f"Error calculating position size for {trade.ticker}: {e}")
        
        return position_info
    
    def assess_trade_risk(self, trade: EnhancedInsiderTrade) -> Dict[str, Any]:
        """Comprehensive trade risk assessment"""
        
        risk_assessment = {
            'overall_risk': RiskLevel.MODERATE,
            'risk_score': 5.0,  # 1-10 scale
            'risk_factors': [],
            'risk_mitigation': [],
            'confidence': 0.5
        }
        
        try:
            risk_score = 5.0  # Base risk
            risk_factors = []
            
            # Volatility risk
            if trade.technical_indicators and trade.technical_indicators.atr:
                atr_ratio = trade.technical_indicators.atr / trade.current_price if trade.current_price else 0
                if atr_ratio > 0.05:  # 5% ATR
                    risk_score += 1.5
                    risk_factors.append("High volatility (ATR > 5%)")
                elif atr_ratio > 0.03:  # 3% ATR
                    risk_score += 0.5
                    risk_factors.append("Moderate volatility")
            
            # Fundamental risk
            if trade.fundamental_data:
                fund = trade.fundamental_data
                
                # P/E risk
                if fund.pe_ratio and fund.pe_ratio > 50:
                    risk_score += 1.0
                    risk_factors.append("Very high P/E ratio")
                elif fund.pe_ratio and fund.pe_ratio > 30:
                    risk_score += 0.5
                    risk_factors.append("High P/E ratio")
                
                # Debt risk
                if fund.debt_to_equity and fund.debt_to_equity > 3:
                    risk_score += 1.5
                    risk_factors.append("Very high debt-to-equity")
                elif fund.debt_to_equity and fund.debt_to_equity > 1.5:
                    risk_score += 0.5
                    risk_factors.append("High debt levels")
                
                # Profitability risk
                if fund.net_margin and fund.net_margin < 0:
                    risk_score += 2.0
                    risk_factors.append("Negative profit margins")
                elif fund.roe and fund.roe < 0:
                    risk_score += 1.5
                    risk_factors.append("Negative return on equity")
            
            # Market cap risk
            if trade.market_cap:
                if trade.market_cap < 300e6:  # < $300M
                    risk_score += 2.0
                    risk_factors.append("Micro-cap stock (high volatility)")
                elif trade.market_cap < 2e9:  # < $2B
                    risk_score += 1.0
                    risk_factors.append("Small-cap stock (moderate volatility)")
            
            # Sector risk
            high_risk_sectors = ['Technology', 'Biotechnology', 'Energy', 'Materials']
            if trade.sector and str(trade.sector) in high_risk_sectors:
                risk_score += 0.5
                risk_factors.append(f"High-risk sector: {trade.sector}")
            
            # Technical risk
            if trade.technical_indicators:
                tech = trade.technical_indicators
                
                # Overbought conditions
                if tech.rsi_14 and tech.rsi_14 > 80:
                    risk_score += 1.0
                    risk_factors.append("Extremely overbought (RSI > 80)")
                elif tech.rsi_14 and tech.rsi_14 > 70:
                    risk_score += 0.5
                    risk_factors.append("Overbought conditions")
                
                # Trend risk
                if tech.sma_20 and tech.sma_50 and trade.current_price:
                    if trade.current_price < tech.sma_50:
                        risk_score += 0.5
                        risk_factors.append("Price below long-term trend")
            
            # Insider trade risk
            if trade.trade_type.value == 'sale':
                risk_score += 1.0
                risk_factors.append("Insider selling signal")
            
            # Sentiment risk
            if trade.sentiment_data and trade.sentiment_data.overall_sentiment:
                if trade.sentiment_data.overall_sentiment < -0.5:
                    risk_score += 1.0
                    risk_factors.append("Very negative sentiment")
                elif trade.sentiment_data.overall_sentiment < -0.2:
                    risk_score += 0.5
                    risk_factors.append("Negative sentiment")
            
            # Liquidity risk (simplified)
            if trade.volume and trade.market_cap:
                daily_turnover = (trade.volume * trade.current_price) / trade.market_cap if trade.current_price else 0
                if daily_turnover < 0.001:  # < 0.1% daily turnover
                    risk_score += 1.0
                    risk_factors.append("Low liquidity")
            
            # Convert risk score to risk level
            if risk_score <= 3:
                risk_assessment['overall_risk'] = RiskLevel.LOW
            elif risk_score <= 4:
                risk_assessment['overall_risk'] = RiskLevel.MODERATE
            elif risk_score <= 6:
                risk_assessment['overall_risk'] = RiskLevel.HIGH
            else:
                risk_assessment['overall_risk'] = RiskLevel.VERY_HIGH
            
            risk_assessment['risk_score'] = min(10, max(1, risk_score))
            risk_assessment['risk_factors'] = risk_factors
            
            # Risk mitigation suggestions
            mitigation = []
            if risk_score > 6:
                mitigation.append("Consider smaller position size")
                mitigation.append("Use tight stop-loss orders")
                mitigation.append("Monitor closely for exit signals")
            
            if 'High volatility' in str(risk_factors):
                mitigation.append("Use volatility-adjusted position sizing")
            
            if 'Negative' in str(risk_factors):
                mitigation.append("Wait for fundamental improvement")
            
            risk_assessment['risk_mitigation'] = mitigation
            
            # Confidence in risk assessment
            data_quality_score = 0
            if trade.fundamental_data: data_quality_score += 0.3
            if trade.technical_indicators: data_quality_score += 0.3
            if trade.sentiment_data: data_quality_score += 0.2
            if trade.market_cap: data_quality_score += 0.2
            
            risk_assessment['confidence'] = data_quality_score
            
        except Exception as e:
            logger.error(f"Error assessing trade risk: {e}")
        
        return risk_assessment
    
    def generate_risk_report(
        self, 
        portfolio: Portfolio,
        trades: List[EnhancedInsiderTrade],
        price_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        
        report = {
            'portfolio_risk': {},
            'individual_risks': {},
            'correlation_analysis': {},
            'stress_test_results': {},
            'recommendations': [],
            'risk_budget': {},
            'generated_at': datetime.now().isoformat()
        }
        
        try:
            # Portfolio-level risk
            report['portfolio_risk'] = self.calculate_portfolio_risk(portfolio, price_data)
            
            # Individual trade risks
            for trade in trades:
                risk_assessment = self.assess_trade_risk(trade)
                report['individual_risks'][trade.ticker] = risk_assessment
            
            # Correlation analysis
            if len(portfolio.positions) > 1:
                report['correlation_analysis'] = self._analyze_correlations(portfolio, price_data)
            
            # Stress testing
            report['stress_test_results'] = self._perform_stress_tests(portfolio, price_data)
            
            # Risk budget allocation
            report['risk_budget'] = self._calculate_risk_budget(portfolio, price_data)
            
            # Generate recommendations
            report['recommendations'] = self._generate_risk_recommendations(report)
            
            logger.info("Risk report generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
        
        return report
    
    def _analyze_correlations(
        self, 
        portfolio: Portfolio, 
        price_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Analyze correlations between portfolio positions"""
        
        correlation_analysis = {
            'correlation_matrix': {},
            'high_correlations': [],
            'diversification_ratio': 0.0
        }
        
        try:
            # Calculate correlation matrix
            returns_data = {}
            for ticker in portfolio.positions.keys():
                if ticker in price_data and not price_data[ticker].empty:
                    returns = price_data[ticker]['close'].pct_change().dropna()
                    returns_data[ticker] = returns
            
            if len(returns_data) > 1:
                returns_df = pd.DataFrame(returns_data)
                correlation_matrix = returns_df.corr()
                
                # Convert to dict for JSON serialization
                correlation_analysis['correlation_matrix'] = correlation_matrix.to_dict()
                
                # Find high correlations
                high_corr_pairs = []
                for i in range(len(correlation_matrix.columns)):
                    for j in range(i+1, len(correlation_matrix.columns)):
                        corr = correlation_matrix.iloc[i, j]
                        if abs(corr) > self.max_correlation:
                            high_corr_pairs.append({
                                'ticker1': correlation_matrix.columns[i],
                                'ticker2': correlation_matrix.columns[j],
                                'correlation': corr
                            })
                
                correlation_analysis['high_correlations'] = high_corr_pairs
                
                # Diversification ratio
                weights = np.array(list(portfolio.positions.values()))
                weights = weights / weights.sum()
                
                portfolio_variance = np.dot(weights.T, np.dot(correlation_matrix.values, weights))
                weighted_avg_variance = np.sum(weights**2)
                
                correlation_analysis['diversification_ratio'] = 1 - (portfolio_variance / weighted_avg_variance)
        
        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
        
        return correlation_analysis
    
    def _perform_stress_tests(
        self, 
        portfolio: Portfolio, 
        price_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Perform stress tests on portfolio"""
        
        stress_results = {
            'market_crash_scenario': {},
            'sector_rotation_scenario': {},
            'volatility_spike_scenario': {},
            'liquidity_crisis_scenario': {}
        }
        
        try:
            portfolio_returns = self._calculate_portfolio_returns(portfolio, price_data)
            
            if portfolio_returns is None:
                return stress_results
            
            current_value = portfolio.total_value
            
            # Market crash scenario (-20% market drop)
            market_shock = -0.20
            crash_loss = current_value * market_shock
            stress_results['market_crash_scenario'] = {
                'scenario': '20% market crash',
                'portfolio_loss': crash_loss,
                'loss_percentage': market_shock,
                'recovery_time_estimate': '12-18 months'
            }
            
            # Volatility spike scenario (3x normal volatility)
            normal_vol = portfolio_returns.std()
            stressed_vol = normal_vol * 3
            vol_var = np.percentile(portfolio_returns, 5) * 3  # 3x worse 5th percentile
            vol_loss = current_value * vol_var
            stress_results['volatility_spike_scenario'] = {
                'scenario': '3x volatility spike',
                'portfolio_loss': vol_loss,
                'loss_percentage': vol_var,
                'new_volatility': stressed_vol * np.sqrt(252)  # Annualized
            }
            
            # Sector rotation scenario (tech selloff)
            # This would require sector classification of holdings
            stress_results['sector_rotation_scenario'] = {
                'scenario': 'Major sector rotation',
                'impact': 'Varies by sector exposure',
                'mitigation': 'Diversification across sectors'
            }
            
            # Liquidity crisis scenario
            stress_results['liquidity_crisis_scenario'] = {
                'scenario': 'Market liquidity crisis',
                'impact': 'Increased bid-ask spreads, difficulty exiting positions',
                'mitigation': 'Focus on liquid, large-cap holdings'
            }
        
        except Exception as e:
            logger.error(f"Error performing stress tests: {e}")
        
        return stress_results
    
    def _calculate_risk_budget(
        self, 
        portfolio: Portfolio, 
        price_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Calculate risk budget allocation"""
        
        risk_budget = {
            'total_risk_budget': 0.02,  # 2% daily VaR budget
            'allocated_risk': {},
            'remaining_budget': 0.0,
            'risk_utilization': 0.0
        }
        
        try:
            # Calculate individual position risks
            total_allocated_risk = 0.0
            
            for ticker, position_value in portfolio.positions.items():
                if ticker in price_data and not price_data[ticker].empty:
                    returns = price_data[ticker]['close'].pct_change().dropna()
                    if len(returns) > 20:
                        position_var = np.percentile(returns, 5)  # 95% VaR
                        weight = position_value / portfolio.total_value
                        position_risk = abs(position_var) * weight
                        
                        risk_budget['allocated_risk'][ticker] = {
                            'position_var': position_var,
                            'weight': weight,
                            'risk_contribution': position_risk
                        }
                        
                        total_allocated_risk += position_risk
            
            risk_budget['remaining_budget'] = max(0, risk_budget['total_risk_budget'] - total_allocated_risk)
            risk_budget['risk_utilization'] = total_allocated_risk / risk_budget['total_risk_budget']
        
        except Exception as e:
            logger.error(f"Error calculating risk budget: {e}")
        
        return risk_budget
    
    def _generate_risk_recommendations(self, risk_report: Dict[str, Any]) -> List[str]:
        """Generate risk management recommendations"""
        
        recommendations = []
        
        try:
            portfolio_risk = risk_report.get('portfolio_risk', {})
            correlation_analysis = risk_report.get('correlation_analysis', {})
            individual_risks = risk_report.get('individual_risks', {})
            
            # Portfolio-level recommendations
            if portfolio_risk.get('var_95') and portfolio_risk['var_95'] < -0.05:
                recommendations.append("Portfolio VaR exceeds 5% - consider reducing position sizes")
            
            if portfolio_risk.get('max_drawdown') and portfolio_risk['max_drawdown'] < -0.20:
                recommendations.append("Maximum drawdown exceeds 20% - review risk management strategy")
            
            if portfolio_risk.get('sharpe_ratio') and portfolio_risk['sharpe_ratio'] < 0.5:
                recommendations.append("Low Sharpe ratio - consider improving risk-adjusted returns")
            
            # Correlation recommendations
            high_correlations = correlation_analysis.get('high_correlations', [])
            if high_correlations:
                recommendations.append(f"High correlations detected between {len(high_correlations)} pairs - consider diversification")
            
            diversification_ratio = correlation_analysis.get('diversification_ratio', 0)
            if diversification_ratio < 0.3:
                recommendations.append("Low diversification ratio - add uncorrelated assets")
            
            # Individual position recommendations
            high_risk_positions = [
                ticker for ticker, risk in individual_risks.items()
                if risk.get('overall_risk') in ['High', 'Very High']
            ]
            
            if high_risk_positions:
                recommendations.append(f"High-risk positions detected: {', '.join(high_risk_positions[:3])} - monitor closely")
            
            # Risk budget recommendations
            risk_budget = risk_report.get('risk_budget', {})
            risk_utilization = risk_budget.get('risk_utilization', 0)
            
            if risk_utilization > 0.9:
                recommendations.append("Risk budget nearly exhausted - avoid new positions")
            elif risk_utilization < 0.5:
                recommendations.append("Risk budget underutilized - consider additional opportunities")
        
        except Exception as e:
            logger.error(f"Error generating risk recommendations: {e}")
        
        return recommendations