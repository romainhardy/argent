"""State management for financial analysis workflow."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AnalysisPhase(str, Enum):
    """Workflow phases for financial analysis."""

    INITIALIZED = "initialized"
    DATA_COLLECTION = "data_collection"
    MACRO_ANALYSIS = "macro_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    RISK_ANALYSIS = "risk_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    SYNTHESIS = "synthesis"
    REPORT = "report"
    COMPLETED = "completed"
    FAILED = "failed"


class TimeHorizon(str, Enum):
    """Investment time horizons."""

    SHORT = "short"  # 1-4 weeks
    MEDIUM = "medium"  # 1-6 months
    LONG = "long"  # 6+ months


@dataclass
class TaskProgress:
    """Track progress of a single task."""

    name: str
    status: str = "pending"  # pending, in_progress, completed, failed
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


@dataclass
class TokenUsage:
    """Track token usage across the workflow."""

    input_tokens: int = 0
    output_tokens: int = 0

    def add(self, input_tokens: int, output_tokens: int) -> None:
        """Add tokens from an agent run."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens


@dataclass
class FinancialAnalysisState:
    """
    Central state management for financial analysis workflow.

    Tracks all collected data, analysis results, and workflow progress.
    """

    # Session identification
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)

    # Request parameters
    analysis_request: str = ""
    symbols: list[str] = field(default_factory=list)
    time_horizon: TimeHorizon = TimeHorizon.MEDIUM
    analysis_types: list[str] = field(default_factory=lambda: ["all"])

    # Collected data
    price_data: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    company_data: dict[str, dict[str, Any]] = field(default_factory=dict)
    economic_data: dict[str, Any] = field(default_factory=dict)
    news_data: dict[str, Any] = field(default_factory=dict)
    crypto_data: dict[str, Any] = field(default_factory=dict)

    # Analysis results
    macro_analysis: dict[str, Any] | None = None
    technical_analysis: dict[str, Any] | None = None
    fundamental_analysis: dict[str, Any] | None = None
    risk_analysis: dict[str, Any] | None = None
    sentiment_analysis: dict[str, Any] | None = None

    # Final outputs
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    final_report: dict[str, Any] | None = None
    report_text: str = ""

    # Workflow tracking
    current_phase: AnalysisPhase = AnalysisPhase.INITIALIZED
    tasks: dict[str, TaskProgress] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    # Token usage
    token_usage: TokenUsage = field(default_factory=TokenUsage)

    def start_phase(self, phase: AnalysisPhase) -> None:
        """Mark a phase as starting."""
        self.current_phase = phase
        task_name = phase.value
        self.tasks[task_name] = TaskProgress(
            name=task_name,
            status="in_progress",
            started_at=datetime.now(),
        )

    def complete_phase(self, phase: AnalysisPhase) -> None:
        """Mark a phase as completed."""
        task_name = phase.value
        if task_name in self.tasks:
            self.tasks[task_name].status = "completed"
            self.tasks[task_name].completed_at = datetime.now()

    def fail_phase(self, phase: AnalysisPhase, error: str) -> None:
        """Mark a phase as failed."""
        task_name = phase.value
        if task_name in self.tasks:
            self.tasks[task_name].status = "failed"
            self.tasks[task_name].error = error
        self.errors.append(f"{phase.value}: {error}")

    def add_price_data(self, symbol: str, data: list[dict[str, Any]]) -> None:
        """Add price data for a symbol."""
        self.price_data[symbol] = data

    def add_company_data(self, symbol: str, data: dict[str, Any]) -> None:
        """Add company data for a symbol."""
        self.company_data[symbol] = data

    def get_stock_symbols(self) -> list[str]:
        """Get non-crypto symbols."""
        crypto = {"BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "LINK", "AVAX", "UNI", "ATOM", "LTC", "FIL"}
        return [s for s in self.symbols if s.upper() not in crypto]

    def get_crypto_symbols(self) -> list[str]:
        """Get crypto symbols."""
        crypto = {"BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "LINK", "AVAX", "UNI", "ATOM", "LTC", "FIL"}
        return [s for s in self.symbols if s.upper() in crypto]

    def get_all_analysis_results(self) -> dict[str, Any]:
        """Get all analysis results for report generation."""
        return {
            "macro_analysis": self.macro_analysis,
            "technical_analysis": self.technical_analysis,
            "fundamental_analysis": self.fundamental_analysis,
            "risk_analysis": self.risk_analysis,
            "sentiment_analysis": self.sentiment_analysis,
            "price_data_summary": {
                symbol: {
                    "data_points": len(data),
                    "latest_price": data[-1]["close"] if data else None,
                    "date_range": f"{data[0]['timestamp']} to {data[-1]['timestamp']}" if data else None,
                }
                for symbol, data in self.price_data.items()
            },
        }

    def get_progress_summary(self) -> dict[str, Any]:
        """Get a summary of workflow progress."""
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        failed = sum(1 for t in self.tasks.values() if t.status == "failed")
        total = len(self.tasks)

        return {
            "session_id": self.session_id,
            "current_phase": self.current_phase.value,
            "progress": f"{completed}/{total} tasks completed",
            "failed_tasks": failed,
            "errors": self.errors,
            "token_usage": {
                "input": self.token_usage.input_tokens,
                "output": self.token_usage.output_tokens,
                "total": self.token_usage.total_tokens,
            },
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for persistence."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "analysis_request": self.analysis_request,
            "symbols": self.symbols,
            "time_horizon": self.time_horizon.value,
            "current_phase": self.current_phase.value,
            "macro_analysis": self.macro_analysis,
            "technical_analysis": self.technical_analysis,
            "fundamental_analysis": self.fundamental_analysis,
            "risk_analysis": self.risk_analysis,
            "sentiment_analysis": self.sentiment_analysis,
            "recommendations": self.recommendations,
            "final_report": self.final_report,
            "errors": self.errors,
            "token_usage": {
                "input": self.token_usage.input_tokens,
                "output": self.token_usage.output_tokens,
            },
        }
