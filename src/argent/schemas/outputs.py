"""Structured output schemas for agent responses.

These Pydantic models define the contract between agents, ensuring
consistent data formats for inter-agent communication and final reports.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SignalOutput(BaseModel):
    """Trading signal with confidence level."""

    signal: Literal["strong_buy", "buy", "hold", "sell", "strong_sell"]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level 0.0-1.0")
    rationale: str | None = Field(default=None, description="Brief explanation")


class TechnicalAnalysisOutput(BaseModel):
    """Output schema for technical analysis."""

    symbol: str
    timestamp: datetime = Field(default_factory=datetime.now)
    signal: SignalOutput

    # Price data
    current_price: float
    price_change_pct: float | None = None

    # Key technical metrics
    key_metrics: dict[str, float] = Field(
        default_factory=dict,
        description="Technical indicators (RSI, MACD, etc.)",
    )

    # Trend analysis
    trend: Literal["strong_uptrend", "uptrend", "sideways", "downtrend", "strong_downtrend"]
    trend_strength: float = Field(ge=0.0, le=1.0)

    # Key levels
    support_levels: list[float] = Field(default_factory=list)
    resistance_levels: list[float] = Field(default_factory=list)

    # Interpretation
    interpretation: str = Field(description="Human-readable analysis summary")


class RiskAnalysisOutput(BaseModel):
    """Output schema for risk analysis."""

    symbol: str
    timestamp: datetime = Field(default_factory=datetime.now)
    signal: SignalOutput

    # Risk classification
    risk_level: Literal["low", "moderate", "high", "very_high"]

    # Key risk metrics
    key_metrics: dict[str, float] = Field(
        default_factory=dict,
        description="Risk metrics (VaR, volatility, Sharpe, etc.)",
    )

    # Detailed metrics
    annualized_volatility: float | None = None
    var_95: float | None = Field(default=None, description="95% Value at Risk")
    var_99: float | None = Field(default=None, description="99% Value at Risk")
    max_drawdown: float | None = None
    sharpe_ratio: float | None = None
    sortino_ratio: float | None = None
    beta: float | None = None

    # Position sizing recommendation
    recommended_position_pct: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Recommended position size as % of portfolio",
    )

    # Interpretation
    interpretation: str = Field(description="Human-readable risk assessment")


class FundamentalAnalysisOutput(BaseModel):
    """Output schema for fundamental analysis (stocks only)."""

    symbol: str
    timestamp: datetime = Field(default_factory=datetime.now)
    signal: SignalOutput

    # Valuation assessment
    valuation: Literal["deeply_undervalued", "undervalued", "fair", "overvalued", "deeply_overvalued"]

    # Key fundamental metrics
    key_metrics: dict[str, float | None] = Field(
        default_factory=dict,
        description="Fundamental metrics (P/E, PEG, margins, etc.)",
    )

    # Detailed metrics
    pe_ratio: float | None = None
    forward_pe: float | None = None
    peg_ratio: float | None = None
    price_to_book: float | None = None
    debt_to_equity: float | None = None
    profit_margin: float | None = None
    roe: float | None = None
    revenue_growth: float | None = None
    earnings_growth: float | None = None

    # Valuation estimate
    fair_value_estimate: float | None = None
    fair_value_low: float | None = None
    fair_value_high: float | None = None
    margin_of_safety: float | None = Field(
        default=None,
        description="Margin of safety at current price (%)",
    )

    # Quality scores (1-5)
    growth_quality: int | None = Field(default=None, ge=1, le=5)
    financial_health: int | None = Field(default=None, ge=1, le=5)

    # Interpretation
    interpretation: str = Field(description="Human-readable fundamental analysis")


class SentimentAnalysisOutput(BaseModel):
    """Output schema for sentiment analysis."""

    symbol: str
    timestamp: datetime = Field(default_factory=datetime.now)
    signal: SignalOutput

    # Sentiment classification
    sentiment: Literal[
        "extremely_bearish", "bearish", "neutral", "bullish", "extremely_bullish"
    ]

    # Sentiment score (-100 to +100)
    sentiment_score: float = Field(ge=-100.0, le=100.0)

    # Key metrics
    key_metrics: dict[str, float | int] = Field(
        default_factory=dict,
        description="Sentiment metrics",
    )

    # News analysis
    news_sentiment: Literal["positive", "negative", "neutral"] | None = None
    news_count: int = 0
    positive_headlines: list[str] = Field(default_factory=list)
    negative_headlines: list[str] = Field(default_factory=list)

    # Sentiment momentum
    sentiment_momentum: Literal["improving", "stable", "deteriorating"]

    # Contrarian signal (if sentiment is extreme)
    contrarian_signal: bool = False
    contrarian_rationale: str | None = None

    # Interpretation
    interpretation: str = Field(description="Human-readable sentiment analysis")


class MacroAnalysisOutput(BaseModel):
    """Output schema for macroeconomic analysis."""

    timestamp: datetime = Field(default_factory=datetime.now)
    signal: SignalOutput

    # Economic cycle
    economic_cycle: Literal["expansion", "peak", "contraction", "trough"]
    cycle_confidence: float = Field(ge=0.0, le=1.0)

    # Monetary policy
    fed_stance: Literal["very_hawkish", "hawkish", "neutral", "dovish", "very_dovish"]

    # Key metrics
    key_metrics: dict[str, float | None] = Field(
        default_factory=dict,
        description="Macro indicators",
    )

    # Key indicators
    fed_funds_rate: float | None = None
    treasury_10y: float | None = None
    treasury_2y: float | None = None
    yield_curve_spread: float | None = None
    yield_curve_inverted: bool = False
    inflation_rate: float | None = None
    unemployment_rate: float | None = None
    gdp_growth: float | None = None
    vix: float | None = None

    # Asset class implications
    stock_outlook: Literal["bullish", "neutral", "bearish"]
    bond_outlook: Literal["bullish", "neutral", "bearish"]
    crypto_outlook: Literal["bullish", "neutral", "bearish"]

    # Risk factors
    risk_factors: list[str] = Field(default_factory=list)

    # Interpretation
    interpretation: str = Field(description="Human-readable macro analysis")


class RecommendationEntry(BaseModel):
    """Single recommendation entry for the report."""

    symbol: str
    action: Literal["strong_buy", "buy", "hold", "sell", "strong_sell"]
    entry_price: float | None = None
    target_price: float | None = None
    stop_loss: float | None = None
    horizon: str | None = Field(default=None, description="Investment horizon (e.g., '3-6 months')")
    conviction: int = Field(ge=1, le=5, description="Conviction level 1-5 stars")
    rationale: str | None = None


class PositionSizing(BaseModel):
    """Position sizing recommendations by risk profile."""

    conservative_pct: float = Field(ge=0.0, le=100.0)
    balanced_pct: float = Field(ge=0.0, le=100.0)
    aggressive_pct: float = Field(ge=0.0, le=100.0)


class ReportOutput(BaseModel):
    """Output schema for the final investment report."""

    timestamp: datetime = Field(default_factory=datetime.now)
    symbols_analyzed: list[str]

    # Executive summary
    executive_summary: str
    primary_recommendation: SignalOutput

    # Market context
    market_context: str

    # Individual analyses (optional, may be summarized)
    technical_summary: str | None = None
    fundamental_summary: str | None = None
    risk_summary: str | None = None
    sentiment_summary: str | None = None
    macro_summary: str | None = None

    # Recommendations table
    recommendations: list[RecommendationEntry] = Field(default_factory=list)

    # Position sizing
    position_sizing: dict[str, PositionSizing] = Field(
        default_factory=dict,
        description="Position sizing by symbol",
    )

    # Risk warnings
    risk_warnings: list[str] = Field(default_factory=list)
    invalidation_scenarios: list[str] = Field(default_factory=list)

    # Catalysts and timeline
    upcoming_catalysts: list[str] = Field(default_factory=list)
    watchlist_items: list[str] = Field(default_factory=list)

    # Confidence and caveats
    overall_confidence: float = Field(ge=0.0, le=1.0)
    analyst_agreement: Literal["strong", "moderate", "mixed", "divergent"]
    caveats: list[str] = Field(default_factory=list)
