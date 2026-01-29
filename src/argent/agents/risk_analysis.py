"""Risk analysis agent for portfolio risk assessment."""

from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic

from argent.agents.base import AgentResult, BaseAgent, FinancialAgentType, ToolDefinition
from argent.prompts.risk_analysis import RISK_ANALYSIS_SYSTEM_PROMPT
from argent.tools import calculations


@dataclass
class RiskAnalysisAgent(BaseAgent):
    """Agent responsible for risk analysis."""

    client: Anthropic
    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 10
    _price_cache: dict[str, list[float]] = field(default_factory=dict)

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.RISK_ANALYSIS

    @property
    def system_prompt(self) -> str:
        return RISK_ANALYSIS_SYSTEM_PROMPT

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="calculate_volatility",
                description="Calculate annualized volatility for a symbol",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_var",
                description="Calculate Value at Risk",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level (e.g., 0.95 for 95%)",
                            "default": 0.95,
                        },
                        "horizon": {
                            "type": "integer",
                            "description": "Time horizon in days",
                            "default": 1,
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_max_drawdown",
                description="Calculate maximum drawdown",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_sharpe_ratio",
                description="Calculate risk-adjusted return (Sharpe ratio)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                        "risk_free_rate": {
                            "type": "number",
                            "description": "Annual risk-free rate",
                            "default": 0.05,
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_sortino_ratio",
                description="Calculate Sortino ratio (downside risk-adjusted return)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                        "risk_free_rate": {
                            "type": "number",
                            "description": "Annual risk-free rate",
                            "default": 0.05,
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_beta",
                description="Calculate beta (systematic risk) relative to market",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                        "market_symbol": {
                            "type": "string",
                            "description": "Market benchmark symbol",
                            "default": "SPY",
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_correlation_matrix",
                description="Calculate correlation matrix for all symbols",
                input_schema={
                    "type": "object",
                    "properties": {},
                },
            ),
            ToolDefinition(
                name="get_risk_summary",
                description="Get comprehensive risk metrics for a symbol",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                    },
                    "required": ["symbol"],
                },
            ),
        ]

    def execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        symbol = tool_input.get("symbol", "")
        prices = self._price_cache.get(symbol, [])

        if tool_name == "calculate_volatility":
            if not prices:
                return {"error": f"No price data available for {symbol}"}

            volatility = calculations.calculate_volatility(prices)
            return {
                "symbol": symbol,
                "annualized_volatility": volatility,
                "volatility_pct": volatility * 100,
                "risk_level": "low" if volatility < 0.15 else "moderate" if volatility < 0.30 else "high",
            }

        elif tool_name == "calculate_var":
            if not prices:
                return {"error": f"No price data available for {symbol}"}

            var_result = calculations.calculate_var(
                prices,
                confidence=tool_input.get("confidence", 0.95),
                horizon=tool_input.get("horizon", 1),
            )
            return {
                "symbol": symbol,
                **var_result,
                "interpretation": f"With {var_result['confidence']*100}% confidence, daily loss will not exceed {var_result['var']*100:.2f}%",
            }

        elif tool_name == "calculate_max_drawdown":
            if not prices:
                return {"error": f"No price data available for {symbol}"}

            dd = calculations.calculate_max_drawdown(prices)
            return {
                "symbol": symbol,
                "max_drawdown": dd["max_drawdown"],
                "max_drawdown_pct": dd["max_drawdown"] * 100,
                "risk_level": "low" if dd["max_drawdown"] < 0.15 else "moderate" if dd["max_drawdown"] < 0.30 else "high",
            }

        elif tool_name == "calculate_sharpe_ratio":
            if not prices:
                return {"error": f"No price data available for {symbol}"}

            risk_free_rate = tool_input.get("risk_free_rate", 0.05)
            sharpe = calculations.calculate_sharpe_ratio(prices, risk_free_rate)
            return {
                "symbol": symbol,
                "sharpe_ratio": sharpe,
                "risk_free_rate": risk_free_rate,
                "interpretation": "excellent" if sharpe > 1.5 else "good" if sharpe > 1.0 else "acceptable" if sharpe > 0.5 else "poor",
            }

        elif tool_name == "calculate_sortino_ratio":
            if not prices:
                return {"error": f"No price data available for {symbol}"}

            risk_free_rate = tool_input.get("risk_free_rate", 0.05)
            sortino = calculations.calculate_sortino_ratio(prices, risk_free_rate)
            return {
                "symbol": symbol,
                "sortino_ratio": sortino,
                "risk_free_rate": risk_free_rate,
                "interpretation": "excellent" if sortino > 2.0 else "good" if sortino > 1.0 else "acceptable" if sortino > 0.5 else "poor",
            }

        elif tool_name == "calculate_beta":
            market_symbol = tool_input.get("market_symbol", "SPY")
            market_prices = self._price_cache.get(market_symbol, [])

            if not prices:
                return {"error": f"No price data available for {symbol}"}
            if not market_prices:
                return {"error": f"No market data available for {market_symbol}"}

            beta = calculations.calculate_beta(prices, market_prices)
            return {
                "symbol": symbol,
                "beta": beta,
                "market_symbol": market_symbol,
                "interpretation": "defensive" if beta < 0.8 else "neutral" if beta < 1.2 else "aggressive",
                "market_sensitivity": f"Moves {beta:.2f}x the market",
            }

        elif tool_name == "calculate_correlation_matrix":
            corr = calculations.calculate_correlation_matrix(self._price_cache)
            return {
                "correlations": corr,
                "diversification_note": self._assess_diversification(corr),
            }

        elif tool_name == "get_risk_summary":
            if not prices:
                return {"error": f"No price data available for {symbol}"}

            volatility = calculations.calculate_volatility(prices)
            var_result = calculations.calculate_var(prices)
            drawdown = calculations.calculate_max_drawdown(prices)
            sharpe = calculations.calculate_sharpe_ratio(prices)
            sortino = calculations.calculate_sortino_ratio(prices)

            # Calculate beta if market data available
            market_prices = self._price_cache.get("SPY", [])
            beta = calculations.calculate_beta(prices, market_prices) if market_prices else None

            return {
                "symbol": symbol,
                "volatility": {
                    "annualized": volatility,
                    "level": "low" if volatility < 0.15 else "moderate" if volatility < 0.30 else "high",
                },
                "var": {
                    "daily_95": var_result["var"],
                    "cvar": var_result.get("cvar"),
                },
                "drawdown": {
                    "max": drawdown["max_drawdown"],
                    "level": "low" if drawdown["max_drawdown"] < 0.15 else "moderate" if drawdown["max_drawdown"] < 0.30 else "high",
                },
                "risk_adjusted_returns": {
                    "sharpe": sharpe,
                    "sortino": sortino,
                },
                "beta": beta,
                "overall_risk_score": self._calculate_risk_score(volatility, drawdown["max_drawdown"], var_result["var"]),
            }

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _assess_diversification(self, corr: dict[str, dict[str, float]]) -> str:
        """Assess portfolio diversification based on correlation matrix."""
        if not corr:
            return "Unable to assess diversification"

        symbols = list(corr.keys())
        if len(symbols) < 2:
            return "Need multiple assets to assess diversification"

        # Calculate average pairwise correlation
        total_corr = 0
        count = 0
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i + 1 :]:
                total_corr += abs(corr[sym1].get(sym2, 0))
                count += 1

        avg_corr = total_corr / count if count > 0 else 0

        if avg_corr < 0.3:
            return "Well diversified - low correlation between assets"
        elif avg_corr < 0.6:
            return "Moderately diversified - some correlation between assets"
        else:
            return "Poorly diversified - high correlation between assets"

    def _calculate_risk_score(self, volatility: float, max_dd: float, var: float) -> float:
        """Calculate overall risk score (0-100, higher = riskier)."""
        # Weighted combination of risk metrics
        vol_score = min(volatility / 0.5 * 100, 100)  # 50% vol = max score
        dd_score = min(max_dd / 0.5 * 100, 100)  # 50% drawdown = max score
        var_score = min(var / 0.10 * 100, 100)  # 10% daily VaR = max score

        return (vol_score * 0.4 + dd_score * 0.35 + var_score * 0.25)

    def analyze(
        self,
        price_data: dict[str, list[dict[str, Any]]],
        symbols: list[str],
        time_horizon: str = "medium",
    ) -> AgentResult:
        """
        Perform risk analysis on the portfolio.

        Args:
            price_data: Dict mapping symbol to list of OHLCV data
            symbols: List of symbols to analyze
            time_horizon: Investment time horizon

        Returns:
            AgentResult with risk analysis
        """
        # Cache prices for tool execution
        self._price_cache = {}
        for symbol in symbols:
            if symbol in price_data:
                self._price_cache[symbol] = [p["close"] for p in price_data[symbol]]

        # Also cache SPY for beta calculations if not already in symbols
        if "SPY" not in self._price_cache and "SPY" in price_data:
            self._price_cache["SPY"] = [p["close"] for p in price_data["SPY"]]

        task = f"""Perform comprehensive risk analysis on the following portfolio: {symbols}

Time horizon: {time_horizon}

For each symbol, analyze:
1. Volatility
   - Annualized volatility
   - Volatility regime (low/moderate/high)

2. Downside Risk
   - Value at Risk (VaR) at 95% confidence
   - Conditional VaR (expected shortfall)
   - Maximum drawdown

3. Risk-Adjusted Returns
   - Sharpe ratio
   - Sortino ratio
   - Interpretation of risk-adjusted performance

4. Systematic Risk
   - Beta relative to market (SPY)
   - Market sensitivity interpretation

5. Portfolio Analysis
   - Correlation matrix
   - Diversification assessment
   - Concentration risks

Return your analysis as structured JSON with the following schema:
{{
    "symbols": {{
        "<symbol>": {{
            "volatility": {{
                "annualized": number,
                "level": "low|moderate|high",
                "percentile": number
            }},
            "downside_risk": {{
                "var_95_daily": number,
                "cvar": number,
                "max_drawdown": number,
                "worst_day": number
            }},
            "risk_adjusted_returns": {{
                "sharpe_ratio": number,
                "sortino_ratio": number,
                "interpretation": "string"
            }},
            "beta": number,
            "overall_risk_score": number,
            "risk_factors": ["string"]
        }}
    }},
    "portfolio": {{
        "correlation_summary": "string",
        "diversification_score": number,
        "concentration_risks": ["string"],
        "recommendations": ["string"]
    }},
    "summary": "string"
}}"""

        return self.run(task, context={"available_symbols": list(self._price_cache.keys())})
