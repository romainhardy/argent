"""Data access layer for financial data."""

import json
from datetime import datetime
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from argent.storage.models import (
    AnalysisPhase,
    AnalysisSession,
    AssetType,
    Base,
    EconomicDataPoint,
    PriceHistory,
    Recommendation,
    Symbol,
    TechnicalAnalysisResult,
)


class Repository:
    """Repository for data access operations."""

    def __init__(self, database_url: str):
        self._engine = create_engine(database_url)
        self._session_factory = sessionmaker(bind=self._engine)
        Base.metadata.create_all(self._engine)

    def _get_session(self) -> Session:
        """Get a new database session."""
        return self._session_factory()

    # Symbol operations
    def get_or_create_symbol(
        self,
        symbol: str,
        name: str | None = None,
        asset_type: AssetType = AssetType.STOCK,
        sector: str | None = None,
        industry: str | None = None,
    ) -> Symbol:
        """Get existing symbol or create new one."""
        with self._get_session() as session:
            stmt = select(Symbol).where(Symbol.symbol == symbol)
            existing = session.execute(stmt).scalar_one_or_none()

            if existing:
                return existing

            new_symbol = Symbol(
                symbol=symbol,
                name=name,
                asset_type=asset_type,
                sector=sector,
                industry=industry,
            )
            session.add(new_symbol)
            session.commit()
            session.refresh(new_symbol)
            return new_symbol

    def get_symbol(self, symbol: str) -> Symbol | None:
        """Get symbol by ticker."""
        with self._get_session() as session:
            stmt = select(Symbol).where(Symbol.symbol == symbol)
            return session.execute(stmt).scalar_one_or_none()

    # Price history operations
    def save_price_history(
        self,
        symbol: str,
        prices: list[dict[str, Any]],
        source: str = "yahoo_finance",
    ) -> int:
        """Save price history data."""
        sym = self.get_or_create_symbol(symbol)

        with self._get_session() as session:
            count = 0
            for price in prices:
                record = PriceHistory(
                    symbol_id=sym.id,
                    timestamp=price["timestamp"],
                    open=price["open"],
                    high=price["high"],
                    low=price["low"],
                    close=price["close"],
                    volume=price["volume"],
                    source=source,
                )
                session.add(record)
                count += 1

            session.commit()
            return count

    def get_price_history(
        self,
        symbol: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 365,
    ) -> list[PriceHistory]:
        """Get price history for a symbol."""
        sym = self.get_symbol(symbol)
        if not sym:
            return []

        with self._get_session() as session:
            stmt = select(PriceHistory).where(PriceHistory.symbol_id == sym.id)

            if start_date:
                stmt = stmt.where(PriceHistory.timestamp >= start_date)
            if end_date:
                stmt = stmt.where(PriceHistory.timestamp <= end_date)

            stmt = stmt.order_by(PriceHistory.timestamp.desc()).limit(limit)
            return list(session.execute(stmt).scalars().all())

    # Economic data operations
    def save_economic_data(self, indicators: list[dict[str, Any]]) -> int:
        """Save economic indicator data."""
        with self._get_session() as session:
            count = 0
            for indicator in indicators:
                record = EconomicDataPoint(
                    series_id=indicator["series_id"],
                    name=indicator["name"],
                    date=indicator["date"],
                    value=indicator["value"],
                    frequency=indicator["frequency"],
                    units=indicator.get("units"),
                )
                session.add(record)
                count += 1

            session.commit()
            return count

    def get_economic_data(
        self,
        series_id: str,
        limit: int = 100,
    ) -> list[EconomicDataPoint]:
        """Get economic data for a series."""
        with self._get_session() as session:
            stmt = (
                select(EconomicDataPoint)
                .where(EconomicDataPoint.series_id == series_id)
                .order_by(EconomicDataPoint.date.desc())
                .limit(limit)
            )
            return list(session.execute(stmt).scalars().all())

    # Analysis session operations
    def create_analysis_session(
        self,
        session_id: str,
        request: str,
        symbols: list[str],
        time_horizon: str,
    ) -> AnalysisSession:
        """Create a new analysis session."""
        with self._get_session() as session:
            analysis_session = AnalysisSession(
                session_id=session_id,
                request=request,
                symbols=json.dumps(symbols),
                time_horizon=time_horizon,
            )
            session.add(analysis_session)
            session.commit()
            session.refresh(analysis_session)
            return analysis_session

    def get_analysis_session(self, session_id: str) -> AnalysisSession | None:
        """Get analysis session by ID."""
        with self._get_session() as session:
            stmt = select(AnalysisSession).where(AnalysisSession.session_id == session_id)
            return session.execute(stmt).scalar_one_or_none()

    def update_analysis_session(
        self,
        session_id: str,
        phase: AnalysisPhase | None = None,
        status: str | None = None,
        macro_analysis: dict | None = None,
        technical_analysis: dict | None = None,
        fundamental_analysis: dict | None = None,
        risk_analysis: dict | None = None,
        sentiment_analysis: dict | None = None,
        final_report: str | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> AnalysisSession | None:
        """Update analysis session with results."""
        with self._get_session() as session:
            stmt = select(AnalysisSession).where(AnalysisSession.session_id == session_id)
            analysis_session = session.execute(stmt).scalar_one_or_none()

            if not analysis_session:
                return None

            if phase:
                analysis_session.phase = phase
            if status:
                analysis_session.status = status
            if macro_analysis:
                analysis_session.macro_analysis = macro_analysis
            if technical_analysis:
                analysis_session.technical_analysis = technical_analysis
            if fundamental_analysis:
                analysis_session.fundamental_analysis = fundamental_analysis
            if risk_analysis:
                analysis_session.risk_analysis = risk_analysis
            if sentiment_analysis:
                analysis_session.sentiment_analysis = sentiment_analysis
            if final_report:
                analysis_session.final_report = final_report
                analysis_session.completed_at = datetime.utcnow()

            analysis_session.total_input_tokens += input_tokens
            analysis_session.total_output_tokens += output_tokens

            session.commit()
            session.refresh(analysis_session)
            return analysis_session

    # Technical analysis results
    def save_technical_result(
        self,
        session_id: str,
        symbol: str,
        indicators: dict[str, Any],
    ) -> TechnicalAnalysisResult | None:
        """Save technical analysis results."""
        analysis_session = self.get_analysis_session(session_id)
        sym = self.get_symbol(symbol)

        if not analysis_session or not sym:
            return None

        with self._get_session() as session:
            result = TechnicalAnalysisResult(
                session_id=analysis_session.id,
                symbol_id=sym.id,
                rsi=indicators.get("rsi"),
                macd=indicators.get("macd"),
                macd_signal=indicators.get("macd_signal"),
                macd_histogram=indicators.get("macd_histogram"),
                sma_20=indicators.get("sma_20"),
                sma_50=indicators.get("sma_50"),
                sma_200=indicators.get("sma_200"),
                ema_20=indicators.get("ema_20"),
                bollinger_upper=indicators.get("bollinger_upper"),
                bollinger_lower=indicators.get("bollinger_lower"),
                atr=indicators.get("atr"),
                support_levels=indicators.get("support_levels"),
                resistance_levels=indicators.get("resistance_levels"),
                trend_direction=indicators.get("trend_direction"),
                signal_strength=indicators.get("signal_strength"),
                analysis_summary=indicators.get("analysis_summary"),
            )
            session.add(result)
            session.commit()
            session.refresh(result)
            return result

    # Recommendation operations
    def save_recommendation(
        self,
        session_id: str,
        symbol: str,
        recommendation: dict[str, Any],
    ) -> Recommendation | None:
        """Save an investment recommendation."""
        analysis_session = self.get_analysis_session(session_id)
        sym = self.get_or_create_symbol(symbol)

        if not analysis_session:
            return None

        with self._get_session() as session:
            rec = Recommendation(
                session_id=analysis_session.id,
                symbol_id=sym.id,
                action=recommendation["action"],
                conviction=recommendation.get("conviction", "medium"),
                time_horizon=recommendation.get("time_horizon", "medium"),
                target_price=recommendation.get("target_price"),
                stop_loss=recommendation.get("stop_loss"),
                position_size=recommendation.get("position_size"),
                rationale=recommendation["rationale"],
                key_risks=recommendation.get("key_risks"),
                catalysts=recommendation.get("catalysts"),
                technical_score=recommendation.get("technical_score"),
                fundamental_score=recommendation.get("fundamental_score"),
                sentiment_score=recommendation.get("sentiment_score"),
                risk_score=recommendation.get("risk_score"),
            )
            session.add(rec)
            session.commit()
            session.refresh(rec)
            return rec

    def get_recommendations(self, session_id: str) -> list[Recommendation]:
        """Get recommendations for a session."""
        analysis_session = self.get_analysis_session(session_id)
        if not analysis_session:
            return []

        with self._get_session() as session:
            stmt = select(Recommendation).where(Recommendation.session_id == analysis_session.id)
            return list(session.execute(stmt).scalars().all())

    def close(self):
        """Close database connections."""
        self._engine.dispose()
