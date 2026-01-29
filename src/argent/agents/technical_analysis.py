"""Technical analysis agent for price action and indicator analysis."""

from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic

from argent.agents.base import AgentResult, BaseAgent, FinancialAgentType, ToolDefinition
from argent.prompts.technical_analysis import TECHNICAL_ANALYSIS_SYSTEM_PROMPT
from argent.tools import calculations


@dataclass
class TechnicalAnalysisAgent(BaseAgent):
    """Agent responsible for technical analysis."""

    client: Anthropic
    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 10
    _price_cache: dict[str, list[float]] = field(default_factory=dict)

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.TECHNICAL_ANALYSIS

    @property
    def system_prompt(self) -> str:
        return TECHNICAL_ANALYSIS_SYSTEM_PROMPT

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="calculate_moving_averages",
                description="Calculate SMA and EMA for given periods",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                        "periods": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Periods for moving averages (e.g., [20, 50, 200])",
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_rsi",
                description="Calculate Relative Strength Index",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                        "period": {
                            "type": "integer",
                            "description": "RSI period (default: 14)",
                            "default": 14,
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_macd",
                description="Calculate MACD indicator",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                        "fast_period": {"type": "integer", "default": 12},
                        "slow_period": {"type": "integer", "default": 26},
                        "signal_period": {"type": "integer", "default": 9},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_bollinger_bands",
                description="Calculate Bollinger Bands",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                        "period": {"type": "integer", "default": 20},
                        "std_dev": {"type": "number", "default": 2.0},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="identify_support_resistance",
                description="Identify key support and resistance levels",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="calculate_trend_strength",
                description="Calculate trend direction and strength",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to analyze"},
                        "period": {"type": "integer", "default": 20},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="get_all_signals",
                description="Get comprehensive technical signals for a symbol",
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

        if not prices:
            return {"error": f"No price data available for {symbol}"}

        if tool_name == "calculate_moving_averages":
            periods = tool_input.get("periods", [20, 50, 200])
            result = {"symbol": symbol, "current_price": prices[-1]}

            for period in periods:
                sma = calculations.calculate_sma(prices, period)
                ema = calculations.calculate_ema(prices, period)
                if sma:
                    result[f"sma_{period}"] = sma[-1]
                    result[f"price_vs_sma_{period}"] = (prices[-1] / sma[-1] - 1) * 100
                if ema:
                    result[f"ema_{period}"] = ema[-1]

            # Golden/Death cross detection
            sma_50 = calculations.calculate_sma(prices, 50)
            sma_200 = calculations.calculate_sma(prices, 200)
            if sma_50 and sma_200:
                result["golden_cross"] = sma_50[-1] > sma_200[-1]
                result["ma_spread"] = (sma_50[-1] / sma_200[-1] - 1) * 100

            return result

        elif tool_name == "calculate_rsi":
            period = tool_input.get("period", 14)
            rsi = calculations.calculate_rsi(prices, period)
            if not rsi:
                return {"error": "Insufficient data for RSI calculation"}

            current_rsi = rsi[-1]
            return {
                "symbol": symbol,
                "rsi": current_rsi,
                "signal": "oversold" if current_rsi < 30 else "overbought" if current_rsi > 70 else "neutral",
                "rsi_history_5d": rsi[-5:] if len(rsi) >= 5 else rsi,
            }

        elif tool_name == "calculate_macd":
            macd = calculations.calculate_macd(
                prices,
                fast_period=tool_input.get("fast_period", 12),
                slow_period=tool_input.get("slow_period", 26),
                signal_period=tool_input.get("signal_period", 9),
            )

            if not macd["macd"]:
                return {"error": "Insufficient data for MACD calculation"}

            histogram = macd["histogram"]
            signal = "bullish" if histogram[-1] > 0 else "bearish"

            # Check for crossover
            crossover = None
            if len(histogram) >= 2:
                if histogram[-2] < 0 and histogram[-1] > 0:
                    crossover = "bullish_crossover"
                elif histogram[-2] > 0 and histogram[-1] < 0:
                    crossover = "bearish_crossover"

            return {
                "symbol": symbol,
                "macd": macd["macd"][-1],
                "signal_line": macd["signal"][-1],
                "histogram": histogram[-1],
                "trend": signal,
                "crossover": crossover,
            }

        elif tool_name == "calculate_bollinger_bands":
            bb = calculations.calculate_bollinger_bands(
                prices,
                period=tool_input.get("period", 20),
                std_dev=tool_input.get("std_dev", 2.0),
            )

            if not bb["upper"]:
                return {"error": "Insufficient data for Bollinger Bands"}

            current_price = prices[-1]
            upper = bb["upper"][-1]
            lower = bb["lower"][-1]
            middle = bb["middle"][-1]

            # Position within bands (0 = lower, 1 = upper)
            bb_position = (current_price - lower) / (upper - lower) if upper != lower else 0.5

            return {
                "symbol": symbol,
                "upper_band": upper,
                "middle_band": middle,
                "lower_band": lower,
                "current_price": current_price,
                "bb_position": bb_position,
                "signal": "oversold" if bb_position < 0.2 else "overbought" if bb_position > 0.8 else "neutral",
                "band_width": (upper - lower) / middle * 100,  # Volatility indicator
            }

        elif tool_name == "identify_support_resistance":
            levels = calculations.identify_support_resistance(prices)
            current_price = prices[-1]

            support_levels = [l for l in levels if l.type == "support"]
            resistance_levels = [l for l in levels if l.type == "resistance"]

            # Find nearest levels
            nearest_support = None
            nearest_resistance = None

            for level in support_levels:
                if level.level < current_price:
                    if nearest_support is None or level.level > nearest_support["level"]:
                        nearest_support = {"level": level.level, "strength": level.strength}

            for level in resistance_levels:
                if level.level > current_price:
                    if nearest_resistance is None or level.level < nearest_resistance["level"]:
                        nearest_resistance = {"level": level.level, "strength": level.strength}

            return {
                "symbol": symbol,
                "current_price": current_price,
                "nearest_support": nearest_support,
                "nearest_resistance": nearest_resistance,
                "support_levels": [{"level": l.level, "strength": l.strength} for l in support_levels[:5]],
                "resistance_levels": [{"level": l.level, "strength": l.strength} for l in resistance_levels[:5]],
            }

        elif tool_name == "calculate_trend_strength":
            period = tool_input.get("period", 20)
            trend = calculations.calculate_trend_strength(prices, period)

            return {
                "symbol": symbol,
                "trend_strength": trend["trend_strength"],
                "direction": "uptrend" if trend["direction"] > 0 else "downtrend",
                "period_return": trend["total_return"] * 100,
            }

        elif tool_name == "get_all_signals":
            signals = calculations.calculate_technical_signals(prices)

            return {
                "symbol": symbol,
                "current_price": prices[-1],
                "signals": [
                    {
                        "indicator": s.indicator,
                        "value": s.value,
                        "signal": s.signal,
                        "strength": s.strength,
                    }
                    for s in signals
                ],
                "overall_signal": self._aggregate_signals(signals),
            }

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _aggregate_signals(self, signals: list) -> dict[str, Any]:
        """Aggregate multiple signals into overall assessment."""
        if not signals:
            return {"signal": "neutral", "score": 0}

        bullish = sum(1 for s in signals if s.signal == "bullish")
        bearish = sum(1 for s in signals if s.signal == "bearish")
        total = len(signals)

        score = (bullish - bearish) / total if total > 0 else 0

        if score > 0.3:
            signal = "bullish"
        elif score < -0.3:
            signal = "bearish"
        else:
            signal = "neutral"

        return {
            "signal": signal,
            "score": score,
            "bullish_count": bullish,
            "bearish_count": bearish,
            "neutral_count": total - bullish - bearish,
        }

    def analyze(
        self,
        price_data: dict[str, list[dict[str, Any]]],
        symbols: list[str],
    ) -> AgentResult:
        """
        Perform technical analysis on price data.

        Args:
            price_data: Dict mapping symbol to list of OHLCV data
            symbols: List of symbols to analyze

        Returns:
            AgentResult with technical analysis
        """
        # Cache prices for tool execution
        self._price_cache = {}
        for symbol in symbols:
            if symbol in price_data:
                self._price_cache[symbol] = [p["close"] for p in price_data[symbol]]

        task = f"""Perform comprehensive technical analysis on the following symbols: {symbols}

For each symbol, analyze:
1. Trend Analysis
   - Moving average alignment (20, 50, 200)
   - Golden/death cross status
   - Overall trend direction and strength

2. Momentum Indicators
   - RSI with overbought/oversold assessment
   - MACD trend and crossover signals

3. Volatility Analysis
   - Bollinger Band position
   - Band width (volatility assessment)

4. Key Levels
   - Support and resistance levels
   - Distance to key levels

5. Signal Summary
   - Aggregate all signals
   - Provide actionable interpretation

Return your analysis as structured JSON with the following schema:
{{
    "symbols": {{
        "<symbol>": {{
            "current_price": number,
            "trend": {{
                "direction": "bullish|bearish|neutral",
                "strength": number,
                "ma_alignment": "string"
            }},
            "momentum": {{
                "rsi": number,
                "rsi_signal": "string",
                "macd_trend": "string",
                "macd_crossover": "string|null"
            }},
            "volatility": {{
                "bb_position": number,
                "bb_signal": "string",
                "volatility_level": "low|moderate|high"
            }},
            "levels": {{
                "nearest_support": number,
                "nearest_resistance": number,
                "support_distance_pct": number,
                "resistance_distance_pct": number
            }},
            "signals": {{
                "overall": "bullish|bearish|neutral",
                "score": number,
                "confidence": "high|medium|low"
            }},
            "interpretation": "string"
        }}
    }},
    "summary": "string"
}}"""

        return self.run(task, context={"available_symbols": list(self._price_cache.keys())})
