from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
from models.trade_models import InsiderTrade, Recommendation, TechnicalAnalysis
from utils.logging_config import logger

class FinancialAnalyzer:
    """Enhanced financial analysis with multiple data sources"""
    
    def __init__(self):
        self.score_weights = {
            'pe_ratio': 1.0,
            'peg_ratio': 1.5,
            'roe': 2.0,
            'debt_to_equity': 1.0,
            'free_cash_flow': 1.5,
            'ebitda': 1.0,
            'insider_ownership': 0.5,
            'institutional_ownership': 0.5,
            'short_ratio': 1.0,
            'rsi': 1.0,
            'performance_ytd': 1.0,
            'beta': 0.5,
            'dividend_yield': 0.5,
            'profit_margin': 1.0,
            'insider_trade_type': 2.0
        }
    
    def calculate_financial_score(
        self, 
        yahoo_data: Dict[str, Any], 
        finviz_data: Dict[str, Any],
        stockanalysis_data: Dict[str, Any], 
        finnhub_data: Dict[str, Any],
        trade_type: str
    ) -> Tuple[int, List[str]]:
        """Calculate comprehensive financial score"""
        
        score = 0
        reasons = []
        
        # P/E Ratio Analysis
        pe_ratio = self._get_metric_value(
            yahoo_data.get('trailingPE'),
            finviz_data.get("P/E"),
            stockanalysis_data.get("trailingPE"),
            finnhub_data.get("peTTM")
        )
        
        if pe_ratio:
            try:
                pe_val = float(pe_ratio)
                if 0 < pe_val < 15:
                    score += int(2 * self.score_weights['pe_ratio'])
                    reasons.append("Низький P/E (< 15)")
                elif 15 <= pe_val <= 25:
                    score += int(1 * self.score_weights['pe_ratio'])
                    reasons.append("Помірний P/E (15-25)")
                elif pe_val > 30:
                    score -= int(1 * self.score_weights['pe_ratio'])
                    reasons.append("Високий P/E (> 30)")
            except (ValueError, TypeError):
                pass
        
        # PEG Ratio Analysis
        peg_ratio = self._get_metric_value(
            yahoo_data.get('pegRatio'),
            finviz_data.get("PEG"),
            None,
            finnhub_data.get("pegRatio")
        )
        
        if peg_ratio:
            try:
                peg_val = float(peg_ratio)
                if peg_val < 1:
                    score += int(2 * self.score_weights['peg_ratio'])
                    reasons.append("Відмінний PEG (< 1)")
                elif peg_val > 2:
                    score -= int(1 * self.score_weights['peg_ratio'])
                    reasons.append("Високий PEG (> 2)")
            except (ValueError, TypeError):
                pass
        
        # ROE Analysis
        roe = self._get_metric_value(
            yahoo_data.get('returnOnEquity'),
            finviz_data.get("ROE"),
            stockanalysis_data.get("returnOnEquity"),
            finnhub_data.get("roeTTM")
        )
        
        if roe:
            try:
                roe_val = float(str(roe).replace('%', ''))
                if isinstance(roe, str) and '%' in roe:
                    roe_val = roe_val / 100
                
                if roe_val > 0.20:
                    score += int(3 * self.score_weights['roe'])
                    reasons.append("Відмінний ROE (> 20%)")
                elif roe_val > 0.15:
                    score += int(2 * self.score_weights['roe'])
                    reasons.append("Хороший ROE (> 15%)")
                elif roe_val < 0:
                    score -= int(2 * self.score_weights['roe'])
                    reasons.append("Негативний ROE")
            except (ValueError, TypeError):
                pass
        
        # Debt to Equity Analysis
        debt_to_equity = self._get_metric_value(
            yahoo_data.get('debtToEquity'),
            finviz_data.get("Debt/Eq"),
            stockanalysis_data.get("debtToEquity"),
            finnhub_data.get("debtToEquity")
        )
        
        if debt_to_equity:
            try:
                d2e_val = float(debt_to_equity)
                if d2e_val < 0.3:
                    score += int(2 * self.score_weights['debt_to_equity'])
                    reasons.append("Низький борг/капітал (< 0.3)")
                elif d2e_val > 2:
                    score -= int(2 * self.score_weights['debt_to_equity'])
                    reasons.append("Високий борг/капітал (> 2)")
            except (ValueError, TypeError):
                pass
        
        # Free Cash Flow Analysis
        fcf = yahoo_data.get('freeCashflow') or finnhub_data.get("freeCashflow")
        if fcf and fcf > 0:
            score += int(2 * self.score_weights['free_cash_flow'])
            reasons.append("Позитивний вільний грошовий потік")
        elif fcf and fcf < 0:
            score -= int(1 * self.score_weights['free_cash_flow'])
            reasons.append("Негативний вільний грошовий потік")
        
        # EBITDA Analysis
        ebitda = yahoo_data.get('ebitda') or finnhub_data.get("ebitdaTTM")
        if ebitda and ebitda > 0:
            score += int(1 * self.score_weights['ebitda'])
            reasons.append("Позитивний EBITDA")
        
        # RSI Analysis
        rsi = self._get_metric_value(
            None,
            finviz_data.get("RSI (14)"),
            None,
            finnhub_data.get("rsi14")
        )
        
        if rsi:
            try:
                rsi_val = float(rsi)
                if rsi_val < 30:
                    score += int(2 * self.score_weights['rsi'])
                    reasons.append("RSI < 30 (перепродано)")
                elif rsi_val > 70:
                    score -= int(1 * self.score_weights['rsi'])
                    reasons.append("RSI > 70 (перекуплено)")
            except (ValueError, TypeError):
                pass
        
        # Performance YTD Analysis
        perf_ytd = finviz_data.get("Perf YTD") or finnhub_data.get("yearToDateReturn")
        if perf_ytd:
            try:
                if isinstance(perf_ytd, str):
                    if perf_ytd.startswith('+'):
                        score += int(1 * self.score_weights['performance_ytd'])
                        reasons.append("Позитивна динаміка YTD")
                    elif perf_ytd.startswith('-'):
                        score -= int(1 * self.score_weights['performance_ytd'])
                        reasons.append("Негативна динаміка YTD")
                elif isinstance(perf_ytd, (int, float)):
                    if perf_ytd > 0:
                        score += int(1 * self.score_weights['performance_ytd'])
                        reasons.append("Позитивна динаміка YTD")
                    elif perf_ytd < 0:
                        score -= int(1 * self.score_weights['performance_ytd'])
                        reasons.append("Негативна динаміка YTD")
            except (ValueError, TypeError):
                pass
        
        # Insider Trade Type Impact
        if 'purchase' in trade_type.lower():
            score += int(3 * self.score_weights['insider_trade_type'])
            reasons.append("Інсайдер купує (позитивний сигнал)")
        elif 'sale' in trade_type.lower():
            score -= int(1 * self.score_weights['insider_trade_type'])
            reasons.append("Інсайдер продає")
        
        return score, reasons
    
    def _get_metric_value(self, *values) -> Optional[Any]:
        """Get first non-None value from multiple sources"""
        for value in values:
            if value is not None and value != "" and value != "N/A":
                return value
        return None
    
    def get_recommendation(self, score: int) -> Recommendation:
        """Convert score to recommendation"""
        if score >= 8:
            return Recommendation.STRONG_BUY
        elif score >= 4:
            return Recommendation.BUY
        elif score >= -2:
            return Recommendation.HOLD
        elif score >= -6:
            return Recommendation.SELL
        else:
            return Recommendation.STRONG_SELL
    
    def analyze_insider_trade(
        self, 
        trade: InsiderTrade, 
        market_data: Dict[str, Any]
    ) -> InsiderTrade:
        """Analyze insider trade with market data"""
        
        yahoo_data = market_data.get('yahoo', {}).get('info', {})
        web_data = market_data.get('web', {})
        finviz_data = web_data.get('finviz', {})
        stockanalysis_data = web_data.get('stockanalysis', {})
        finnhub_data = market_data.get('finnhub', {}).get('metrics', {})
        
        # Calculate financial score
        score, reasons = self.calculate_financial_score(
            yahoo_data, finviz_data, stockanalysis_data, 
            finnhub_data, trade.trade_type.value
        )
        
        # Update trade object
        trade.score = score
        trade.reasons = reasons
        trade.recommendation = self.get_recommendation(score)
        
        # Set current price
        trade.current_price = (
            yahoo_data.get('regularMarketPrice') or 
            stockanalysis_data.get('regularMarketPrice')
        )
        
        # Set target prices
        trade.target_prices = {
            'yahoo': yahoo_data.get('targetMeanPrice'),
            'finviz': finviz_data.get('Target Price'),
            'stockanalysis': stockanalysis_data.get('Target Price')
        }
        
        # Set sector
        trade.sector = yahoo_data.get('sector', 'N/A')
        
        logger.debug(f"Analyzed trade for {trade.ticker}: {trade.recommendation.value} (score: {score})")
        
        return trade