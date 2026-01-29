"""SQLAlchemy models for financial data storage."""

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class AssetType(str, Enum):
    """Asset type enumeration."""

    STOCK = "stock"
    ETF = "etf"
    CRYPTO = "crypto"
    INDEX = "index"


class AnalysisPhase(str, Enum):
    """Analysis workflow phase."""

    DATA_COLLECTION = "data_collection"
    MACRO_ANALYSIS = "macro_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    RISK_ANALYSIS = "risk_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    SYNTHESIS = "synthesis"
    REPORT = "report"
    COMPLETED = "completed"


class Symbol(Base):
    """Symbol/ticker information."""

    __tablename__ = "symbols"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    asset_type: Mapped[AssetType] = mapped_column(SQLEnum(AssetType))
    sector: Mapped[str | None] = mapped_column(String(100))
    industry: Mapped[str | None] = mapped_column(String(100))
    exchange: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    price_history: Mapped[list["PriceHistory"]] = relationship(back_populates="symbol_rel")
    technical_results: Mapped[list["TechnicalAnalysisResult"]] = relationship(back_populates="symbol_rel")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="symbol_rel")


class PriceHistory(Base):
    """Historical price data."""

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    symbol_rel: Mapped["Symbol"] = relationship(back_populates="price_history")


class EconomicDataPoint(Base):
    """Economic indicator data from FRED."""

    __tablename__ = "economic_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    series_id: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(255))
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    value: Mapped[float] = mapped_column(Float)
    frequency: Mapped[str] = mapped_column(String(20))
    units: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnalysisSession(Base):
    """Analysis session tracking."""

    __tablename__ = "analysis_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    request: Mapped[str] = mapped_column(Text)
    symbols: Mapped[str] = mapped_column(Text)  # JSON list of symbols
    time_horizon: Mapped[str] = mapped_column(String(20))
    phase: Mapped[AnalysisPhase] = mapped_column(SQLEnum(AnalysisPhase), default=AnalysisPhase.DATA_COLLECTION)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Analysis results stored as JSON
    macro_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    technical_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    fundamental_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    risk_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    sentiment_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    final_report: Mapped[str | None] = mapped_column(Text)

    # Token usage tracking
    total_input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_output_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    technical_results: Mapped[list["TechnicalAnalysisResult"]] = relationship(back_populates="session")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="session")


class TechnicalAnalysisResult(Base):
    """Technical analysis results for a symbol."""

    __tablename__ = "technical_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("analysis_sessions.id"), index=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id"), index=True)

    # Technical indicators
    rsi: Mapped[float | None] = mapped_column(Float)
    macd: Mapped[float | None] = mapped_column(Float)
    macd_signal: Mapped[float | None] = mapped_column(Float)
    macd_histogram: Mapped[float | None] = mapped_column(Float)
    sma_20: Mapped[float | None] = mapped_column(Float)
    sma_50: Mapped[float | None] = mapped_column(Float)
    sma_200: Mapped[float | None] = mapped_column(Float)
    ema_20: Mapped[float | None] = mapped_column(Float)
    bollinger_upper: Mapped[float | None] = mapped_column(Float)
    bollinger_lower: Mapped[float | None] = mapped_column(Float)
    atr: Mapped[float | None] = mapped_column(Float)

    # Support/Resistance levels stored as JSON
    support_levels: Mapped[list[float] | None] = mapped_column(JSON)
    resistance_levels: Mapped[list[float] | None] = mapped_column(JSON)

    # Signals
    trend_direction: Mapped[str | None] = mapped_column(String(20))  # bullish, bearish, neutral
    signal_strength: Mapped[float | None] = mapped_column(Float)
    analysis_summary: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped["AnalysisSession"] = relationship(back_populates="technical_results")
    symbol_rel: Mapped["Symbol"] = relationship(back_populates="technical_results")


class Recommendation(Base):
    """Investment recommendations."""

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("analysis_sessions.id"), index=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id"), index=True)

    action: Mapped[str] = mapped_column(String(20))  # buy, sell, hold, watch
    conviction: Mapped[str] = mapped_column(String(20))  # high, medium, low
    time_horizon: Mapped[str] = mapped_column(String(20))  # short, medium, long
    target_price: Mapped[float | None] = mapped_column(Float)
    stop_loss: Mapped[float | None] = mapped_column(Float)
    position_size: Mapped[float | None] = mapped_column(Float)  # Suggested allocation %

    # Reasoning
    rationale: Mapped[str] = mapped_column(Text)
    key_risks: Mapped[str | None] = mapped_column(Text)
    catalysts: Mapped[str | None] = mapped_column(Text)

    # Supporting evidence
    technical_score: Mapped[float | None] = mapped_column(Float)
    fundamental_score: Mapped[float | None] = mapped_column(Float)
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    risk_score: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped["AnalysisSession"] = relationship(back_populates="recommendations")
    symbol_rel: Mapped["Symbol"] = relationship(back_populates="recommendations")
