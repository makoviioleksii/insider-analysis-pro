from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

class TradeType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"

class Recommendation(str, Enum):
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"

class FinancialData(BaseModel):
    """Base model for financial data"""
    ticker: str = Field(..., min_length=1, max_length=10)
    current_price: Optional[float] = Field(None, ge=0)
    target_price: Optional[float] = Field(None, ge=0)
    pe_ratio: Optional[float] = Field(None, ge=0)
    peg_ratio: Optional[float] = Field(None, ge=0)
    roe: Optional[float] = Field(None, ge=-1, le=1)
    debt_to_equity: Optional[float] = Field(None, ge=0)
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()

class InsiderTrade(BaseModel):
    """Model for insider trading data"""
    date: datetime
    ticker: str = Field(..., min_length=1, max_length=10)
    sector: str = "N/A"
    insider_name: str
    insider_title: str
    trade_type: TradeType
    amount: float
    current_price: Optional[float] = Field(None, ge=0)
    target_prices: Dict[str, Optional[float]] = Field(default_factory=dict)
    recommendation: Optional[Recommendation] = None
    score: int = 0
    reasons: List[str] = Field(default_factory=list)
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()
    
    @validator('amount')
    def amount_must_be_reasonable(cls, v):
        if abs(v) > 1e12:  # 1 trillion limit
            raise ValueError('Amount too large')
        return v
    
    @property
    def fair_avg(self) -> Optional[float]:
        """Calculate average fair value from available target prices"""
        valid_prices = [p for p in self.target_prices.values() if p is not None]
        return sum(valid_prices) / len(valid_prices) if valid_prices else None

class TechnicalAnalysis(BaseModel):
    """Model for technical analysis data"""
    ticker: str
    sma20: Optional[float] = None
    ema50: Optional[float] = None
    rsi: Optional[float] = Field(None, ge=0, le=100)
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    support: Optional[float] = None
    resistance: Optional[float] = None
    trend: str = "Neutral"
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()

class WatchlistItem(BaseModel):
    """Model for watchlist analysis item"""
    ticker: str
    current_price: Optional[float] = None
    target_price: Optional[float] = None
    technical_analysis: Optional[TechnicalAnalysis] = None
    recommendation: Optional[Recommendation] = None
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()