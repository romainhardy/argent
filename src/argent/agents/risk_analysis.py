"""Risk analysis agent for portfolio risk assessment."""

from dataclasses import dataclass, field
from typing import Any

from argent.agents.base import AgentResult, FinancialAgentType
from argent.tools import calculations


@dataclass
class RiskAnalysisAgent:
    """Agent responsible for risk analysis using computational methods."""

    _price_cache: dict[str, list[float]] = field(default_factory=dict)

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.RISK_ANALYSIS

    def _calculate_risk_score(self, volatility: float, max_drawdown: float, var: float) -> dict[str, Any]:
        """Calculate overall risk score from individual metrics."""
        # Normalize each metric to 0-1 scale (1 = highest risk)
        vol_score = min(volatility / 0.5, 1.0)  # 50% vol = max score
        dd_score = min(abs(max_drawdown) / 0.5, 1.0)  # 50% drawdown = max score
        var_score = min(abs(var) / 0.1, 1.0)  # 10% daily VaR = max score

        # Weighted average
        overall = vol_score * 0.4 + dd_score * 0.35 + var_score * 0.25

        if overall < 0.3:
            level = "low"
        elif overall < 0.6:
            level = "moderate"
        else:
            level = "high"

        return {"score": overall, "level": level}

    def _assess_diversification(self, corr: dict[str, dict[str, float]]) -> str:
        """Assess portfolio diversification based on correlation matrix."""
        if not corr:
            return "Unable to assess diversification"

        symbols = list(corr.keys())
        if len(symbols) < 2:
            return "Need multiple assets to assess diversification"

        total_corr = 0
        count = 0
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i + 1:]:
                total_corr += abs(corr[sym1].get(sym2, 0))
                count += 1

        avg_corr = total_corr / count if count > 0 else 0

        if avg_corr < 0.3:
            return "Well diversified - low correlation between assets"
        elif avg_corr < 0.6:
            return "Moderately diversified - some correlation between assets"
        else:
            return "Poorly diversified - high correlation between assets"

    def analyze(
        self,
        price_data: dict[str, list[dict[str, Any]]],
        symbols: list[str],
    ) -> AgentResult:
        """Perform risk analysis using computational methods."""
        # Extract closing prices
        self._price_cache = {}
        for symbol in symbols:
            if symbol in price_data:
                self._price_cache[symbol] = [p["close"] for p in price_data[symbol]]

        results = {"symbols": {}}

        for symbol in symbols:
            prices = self._price_cache.get(symbol, [])
            if not prices or len(prices) < 30:
                continue

            # Calculate all risk metrics
            volatility = calculations.calculate_volatility(prices)
            var_result = calculations.calculate_var(prices, confidence=0.95, horizon=1)
            drawdown = calculations.calculate_max_drawdown(prices)
            sharpe = calculations.calculate_sharpe_ratio(prices, risk_free_rate=0.05)
            sortino = calculations.calculate_sortino_ratio(prices, risk_free_rate=0.05)

            # Calculate beta if we have market data
            market_prices = self._price_cache.get("SPY", [])
            beta = calculations.calculate_beta(prices, market_prices) if market_prices else None

            # Risk score
            risk_score = self._calculate_risk_score(volatility, drawdown["max_drawdown"], var_result["var"])

            results["symbols"][symbol] = {
                "volatility": {
                    "annualized": volatility,
                    "annualized_pct": volatility * 100,
                    "level": "low" if volatility < 0.15 else "moderate" if volatility < 0.30 else "high",
                },
                "value_at_risk": {
                    "daily_95": var_result["var"],
                    "daily_95_pct": var_result["var"] * 100,
                    "cvar": var_result.get("cvar"),
                },
                "max_drawdown": {
                    "value": drawdown["max_drawdown"],
                    "value_pct": drawdown["max_drawdown"] * 100,
                    "level": "low" if abs(drawdown["max_drawdown"]) < 0.15 else "moderate" if abs(drawdown["max_drawdown"]) < 0.30 else "high",
                },
                "risk_adjusted_returns": {
                    "sharpe_ratio": sharpe,
                    "sharpe_interpretation": "excellent" if sharpe > 1.5 else "good" if sharpe > 1.0 else "acceptable" if sharpe > 0.5 else "poor",
                    "sortino_ratio": sortino,
                    "sortino_interpretation": "excellent" if sortino > 2.0 else "good" if sortino > 1.0 else "acceptable" if sortino > 0.5 else "poor",
                },
                "beta": beta,
                "beta_interpretation": "defensive" if beta and beta < 0.8 else "neutral" if beta and beta < 1.2 else "aggressive" if beta else None,
                "overall_risk": risk_score,
            }

        # Correlation matrix
        if len(self._price_cache) > 1:
            corr = calculations.calculate_correlation_matrix(self._price_cache)
            results["correlation"] = corr
            results["diversification"] = self._assess_diversification(corr)

        # Summary
        risk_levels = [r["overall_risk"]["level"] for r in results["symbols"].values()]
        if risk_levels:
            high_risk_count = sum(1 for l in risk_levels if l == "high")
            results["summary"] = f"Risk analysis complete. {high_risk_count}/{len(risk_levels)} symbols show high risk."
        else:
            results["summary"] = "No symbols analyzed."

        return AgentResult(
            success=True,
            data=results,
            error=None,
        )
