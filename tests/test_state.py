"""Tests for state management."""

import pytest

from argent.orchestrator.state import (
    FinancialAnalysisState,
    AnalysisPhase,
    TimeHorizon,
    TokenUsage,
)


class TestTokenUsage:
    """Tests for token usage tracking."""

    def test_initial_values(self):
        """Test initial token values are zero."""
        usage = TokenUsage()
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.total_tokens == 0

    def test_add_tokens(self):
        """Test adding tokens."""
        usage = TokenUsage()
        usage.add(100, 50)
        usage.add(200, 100)

        assert usage.input_tokens == 300
        assert usage.output_tokens == 150
        assert usage.total_tokens == 450


class TestFinancialAnalysisState:
    """Tests for financial analysis state."""

    def test_initial_state(self):
        """Test initial state values."""
        state = FinancialAnalysisState()

        assert state.session_id is not None
        assert len(state.session_id) == 8
        assert state.current_phase == AnalysisPhase.INITIALIZED
        assert state.symbols == []
        assert state.errors == []

    def test_symbol_categorization(self):
        """Test symbol categorization into stocks and crypto."""
        state = FinancialAnalysisState(
            symbols=["AAPL", "BTC", "MSFT", "ETH", "SPY", "SOL"]
        )

        stocks = state.get_stock_symbols()
        crypto = state.get_crypto_symbols()

        assert "AAPL" in stocks
        assert "MSFT" in stocks
        assert "SPY" in stocks
        assert "BTC" in crypto
        assert "ETH" in crypto
        assert "SOL" in crypto

    def test_phase_tracking(self):
        """Test phase start and completion tracking."""
        state = FinancialAnalysisState()

        state.start_phase(AnalysisPhase.DATA_COLLECTION)
        assert state.current_phase == AnalysisPhase.DATA_COLLECTION
        assert "data_collection" in state.tasks
        assert state.tasks["data_collection"].status == "in_progress"

        state.complete_phase(AnalysisPhase.DATA_COLLECTION)
        assert state.tasks["data_collection"].status == "completed"

    def test_phase_failure(self):
        """Test phase failure tracking."""
        state = FinancialAnalysisState()

        state.start_phase(AnalysisPhase.TECHNICAL_ANALYSIS)
        state.fail_phase(AnalysisPhase.TECHNICAL_ANALYSIS, "API error")

        assert state.tasks["technical_analysis"].status == "failed"
        assert "technical_analysis: API error" in state.errors

    def test_add_price_data(self):
        """Test adding price data."""
        state = FinancialAnalysisState()

        price_data = [
            {"timestamp": "2024-01-01", "close": 100},
            {"timestamp": "2024-01-02", "close": 101},
        ]
        state.add_price_data("AAPL", price_data)

        assert "AAPL" in state.price_data
        assert len(state.price_data["AAPL"]) == 2

    def test_add_company_data(self):
        """Test adding company data."""
        state = FinancialAnalysisState()

        company_data = {"name": "Apple Inc.", "sector": "Technology"}
        state.add_company_data("AAPL", company_data)

        assert "AAPL" in state.company_data
        assert state.company_data["AAPL"]["name"] == "Apple Inc."

    def test_get_all_analysis_results(self):
        """Test getting all analysis results."""
        state = FinancialAnalysisState(symbols=["AAPL"])
        state.macro_analysis = {"cycle": "expansion"}
        state.technical_analysis = {"trend": "bullish"}

        results = state.get_all_analysis_results()

        assert "macro_analysis" in results
        assert "technical_analysis" in results
        assert results["macro_analysis"]["cycle"] == "expansion"

    def test_progress_summary(self):
        """Test progress summary generation."""
        state = FinancialAnalysisState()
        state.start_phase(AnalysisPhase.DATA_COLLECTION)
        state.complete_phase(AnalysisPhase.DATA_COLLECTION)
        state.start_phase(AnalysisPhase.TECHNICAL_ANALYSIS)
        state.token_usage.add(1000, 500)

        summary = state.get_progress_summary()

        assert summary["session_id"] == state.session_id
        assert summary["current_phase"] == "technical_analysis"
        assert "1/2" in summary["progress"]
        assert summary["token_usage"]["total"] == 1500

    def test_to_dict(self):
        """Test state serialization."""
        state = FinancialAnalysisState(
            symbols=["AAPL", "BTC"],
            time_horizon=TimeHorizon.MEDIUM,
        )
        state.macro_analysis = {"test": "data"}

        data = state.to_dict()

        assert data["symbols"] == ["AAPL", "BTC"]
        assert data["time_horizon"] == "medium"
        assert data["macro_analysis"]["test"] == "data"


class TestTimeHorizon:
    """Tests for time horizon enum."""

    def test_horizon_values(self):
        """Test time horizon values."""
        assert TimeHorizon.SHORT.value == "short"
        assert TimeHorizon.MEDIUM.value == "medium"
        assert TimeHorizon.LONG.value == "long"

    def test_horizon_from_string(self):
        """Test creating horizon from string."""
        assert TimeHorizon("short") == TimeHorizon.SHORT
        assert TimeHorizon("medium") == TimeHorizon.MEDIUM
        assert TimeHorizon("long") == TimeHorizon.LONG


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
