from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import numpy as np

class TradeType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    OPTION_EXERCISE = "option_exercise"
    GIFT = "gift"
    INHERITANCE = "inheritance"
    OTHER = "other"

class Recommendation(str, Enum):
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"

class RiskLevel(str, Enum):
    VERY_LOW = "Very Low"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very High"

class MarketSentiment(str, Enum):
    VERY_BEARISH = "Very Bearish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"
    BULLISH = "Bullish"
    VERY_BULLISH = "Very Bullish"

class Sector(str, Enum):
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCIALS = "Financials"
    CONSUMER_DISCRETIONARY = "Consumer Discretionary"
    CONSUMER_STAPLES = "Consumer Staples"
    INDUSTRIALS = "Industrials"
    ENERGY = "Energy"
    UTILITIES = "Utilities"
    MATERIALS = "Materials"
    REAL_ESTATE = "Real Estate"
    COMMUNICATION_SERVICES = "Communication Services"

class MacroEconomicData(BaseModel):
    """Macroeconomic indicators"""
    date: datetime
    gdp_growth: Optional[float] = None
    inflation_rate: Optional[float] = None
    unemployment_rate: Optional[float] = None
    interest_rate: Optional[float] = None
    vix: Optional[float] = None
    dollar_index: Optional[float] = None
    oil_price: Optional[float] = None
    gold_price: Optional[float] = None

class SentimentData(BaseModel):
    """News and social media sentiment data"""
    ticker: str
    date: datetime
    news_sentiment: Optional[float] = Field(None, ge=-1, le=1)
    social_sentiment: Optional[float] = Field(None, ge=-1, le=1)
    analyst_sentiment: Optional[float] = Field(None, ge=-1, le=1)
    insider_sentiment: Optional[float] = Field(None, ge=-1, le=1)
    overall_sentiment: Optional[float] = Field(None, ge=-1, le=1)
    sentiment_volatility: Optional[float] = Field(None, ge=0)
    news_volume: Optional[int] = Field(None, ge=0)

class TechnicalIndicators(BaseModel):
    """Comprehensive technical indicators"""
    ticker: str
    date: datetime
    
    # Moving Averages
    sma_5: Optional[float] = None
    sma_10: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    ema_50: Optional[float] = None
    
    # Momentum Indicators
    rsi_14: Optional[float] = Field(None, ge=0, le=100)
    rsi_21: Optional[float] = Field(None, ge=0, le=100)
    stoch_k: Optional[float] = Field(None, ge=0, le=100)
    stoch_d: Optional[float] = Field(None, ge=0, le=100)
    williams_r: Optional[float] = Field(None, ge=-100, le=0)
    
    # Trend Indicators
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    adx: Optional[float] = Field(None, ge=0, le=100)
    cci: Optional[float] = None
    
    # Volatility Indicators
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_width: Optional[float] = None
    atr: Optional[float] = Field(None, ge=0)
    
    # Volume Indicators
    obv: Optional[float] = None
    ad_line: Optional[float] = None
    cmf: Optional[float] = Field(None, ge=-1, le=1)
    
    # Support and Resistance
    support_1: Optional[float] = None
    support_2: Optional[float] = None
    resistance_1: Optional[float] = None
    resistance_2: Optional[float] = None
    
    # Pattern Recognition
    bullish_patterns: List[str] = Field(default_factory=list)
    bearish_patterns: List[str] = Field(default_factory=list)

class FundamentalData(BaseModel):
    """Enhanced fundamental analysis data"""
    ticker: str
    date: datetime
    
    # Valuation Metrics
    pe_ratio: Optional[float] = Field(None, ge=0)
    peg_ratio: Optional[float] = Field(None, ge=0)
    pb_ratio: Optional[float] = Field(None, ge=0)
    ps_ratio: Optional[float] = Field(None, ge=0)
    ev_ebitda: Optional[float] = Field(None, ge=0)
    ev_sales: Optional[float] = Field(None, ge=0)
    
    # Profitability Metrics
    roe: Optional[float] = None
    roa: Optional[float] = None
    roic: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    
    # Financial Health
    debt_to_equity: Optional[float] = Field(None, ge=0)
    current_ratio: Optional[float] = Field(None, ge=0)
    quick_ratio: Optional[float] = Field(None, ge=0)
    interest_coverage: Optional[float] = None
    
    # Growth Metrics
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    book_value_growth: Optional[float] = None
    
    # Cash Flow
    free_cash_flow: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    fcf_yield: Optional[float] = None
    
    # Market Data
    market_cap: Optional[float] = Field(None, ge=0)
    enterprise_value: Optional[float] = Field(None, ge=0)
    shares_outstanding: Optional[float] = Field(None, ge=0)
    float_shares: Optional[float] = Field(None, ge=0)
    
    # Dividend Data
    dividend_yield: Optional[float] = Field(None, ge=0)
    payout_ratio: Optional[float] = Field(None, ge=0, le=1)
    dividend_growth: Optional[float] = None

class InsiderProfile(BaseModel):
    """Enhanced insider profile"""
    name: str
    title: str
    company: str
    ticker: str
    
    # Historical Trading Patterns
    total_trades: int = 0
    purchase_trades: int = 0
    sale_trades: int = 0
    total_volume: float = 0
    average_trade_size: float = 0
    
    # Performance Metrics
    success_rate: Optional[float] = Field(None, ge=0, le=1)
    average_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    
    # Timing Analysis
    average_days_to_peak: Optional[float] = None
    average_days_to_trough: Optional[float] = None
    
    # Ownership Data
    shares_owned: Optional[float] = Field(None, ge=0)
    ownership_percentage: Optional[float] = Field(None, ge=0, le=1)
    
    # Risk Metrics
    risk_score: Optional[float] = Field(None, ge=0, le=10)
    reliability_score: Optional[float] = Field(None, ge=0, le=10)

class EnhancedInsiderTrade(BaseModel):
    """Enhanced insider trading data with ML predictions"""
    
    # Basic Trade Information
    date: datetime
    ticker: str = Field(..., min_length=1, max_length=10)
    company_name: Optional[str] = None
    sector: Optional[Sector] = None
    
    # Insider Information
    insider_name: str
    insider_title: str
    insider_profile: Optional[InsiderProfile] = None
    
    # Trade Details
    trade_type: TradeType
    shares: Optional[float] = Field(None, ge=0)
    price_per_share: Optional[float] = Field(None, ge=0)
    amount: float
    
    # Market Data
    current_price: Optional[float] = Field(None, ge=0)
    volume: Optional[float] = Field(None, ge=0)
    market_cap: Optional[float] = Field(None, ge=0)
    
    # Analysis Results
    fundamental_data: Optional[FundamentalData] = None
    technical_indicators: Optional[TechnicalIndicators] = None
    sentiment_data: Optional[SentimentData] = None
    
    # ML Predictions
    price_prediction_1d: Optional[float] = None
    price_prediction_7d: Optional[float] = None
    price_prediction_30d: Optional[float] = None
    probability_up_1d: Optional[float] = Field(None, ge=0, le=1)
    probability_up_7d: Optional[float] = Field(None, ge=0, le=1)
    probability_up_30d: Optional[float] = Field(None, ge=0, le=1)
    
    # Risk Assessment
    risk_level: Optional[RiskLevel] = None
    var_1d: Optional[float] = None
    var_7d: Optional[float] = None
    expected_shortfall: Optional[float] = None
    
    # Scoring and Recommendations
    fundamental_score: Optional[float] = Field(None, ge=0, le=100)
    technical_score: Optional[float] = Field(None, ge=0, le=100)
    sentiment_score: Optional[float] = Field(None, ge=0, le=100)
    insider_score: Optional[float] = Field(None, ge=0, le=100)
    composite_score: Optional[float] = Field(None, ge=0, le=100)
    
    recommendation: Optional[Recommendation] = None
    confidence_level: Optional[float] = Field(None, ge=0, le=1)
    
    # Target Prices
    target_prices: Dict[str, Optional[float]] = Field(default_factory=dict)
    fair_value: Optional[float] = None
    
    # Additional Metadata
    reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()
    
    @property
    def fair_avg(self) -> Optional[float]:
        """Calculate average fair value from available target prices"""
        valid_prices = [p for p in self.target_prices.values() if p is not None]
        return sum(valid_prices) / len(valid_prices) if valid_prices else self.fair_value

class Portfolio(BaseModel):
    """Portfolio management model"""
    name: str
    description: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.now)
    
    # Holdings
    positions: Dict[str, float] = Field(default_factory=dict)  # ticker -> quantity
    cash: float = 0.0
    total_value: float = 0.0
    
    # Performance Metrics
    total_return: Optional[float] = None
    annualized_return: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    
    # Risk Metrics
    beta: Optional[float] = None
    var_95: Optional[float] = None
    expected_shortfall: Optional[float] = None
    
    # Allocation
    sector_allocation: Dict[str, float] = Field(default_factory=dict)
    risk_allocation: Dict[str, float] = Field(default_factory=dict)

class Alert(BaseModel):
    """Trading alert model"""
    id: str
    ticker: str
    alert_type: str  # price, volume, insider_trade, technical, fundamental
    condition: str
    threshold: float
    current_value: Optional[float] = None
    triggered: bool = False
    triggered_date: Optional[datetime] = None
    created_date: datetime = Field(default_factory=datetime.now)
    active: bool = True
    
    # Notification settings
    email_notification: bool = False
    push_notification: bool = False
    telegram_notification: bool = False

class BacktestResult(BaseModel):
    """Backtesting result model"""
    strategy_name: str
    start_date: date
    end_date: date
    
    # Performance Metrics
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    
    # Trade Statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float
    
    # Risk Metrics
    var_95: float
    expected_shortfall: float
    beta: float
    alpha: float
    
    # Benchmark Comparison
    benchmark_return: Optional[float] = None
    excess_return: Optional[float] = None
    information_ratio: Optional[float] = None
    
    # Additional Data
    equity_curve: List[float] = Field(default_factory=list)
    drawdown_curve: List[float] = Field(default_factory=list)
    trade_log: List[Dict[str, Any]] = Field(default_factory=list)

class MarketRegime(BaseModel):
    """Market regime classification"""
    date: datetime
    regime: str  # bull, bear, sideways, volatile
    confidence: float = Field(..., ge=0, le=1)
    
    # Market Characteristics
    trend_strength: Optional[float] = None
    volatility_level: Optional[float] = None
    correlation_level: Optional[float] = None
    
    # Economic Indicators
    macro_data: Optional[MacroEconomicData] = None