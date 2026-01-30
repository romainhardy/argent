"""Technical analysis agent for price action and indicator analysis."""

from dataclasses import dataclass, field
from typing import Any, Optional

from argent.agents.base import AgentResult, FinancialAgentType
from argent.tools import calculations


@dataclass
class TechnicalAnalysisAgent:
    """Agent responsible for technical analysis using computational methods."""

    _price_cache: dict[str, list[float]] = field(default_factory=dict)

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.TECHNICAL_ANALYSIS

    def _calculate_moving_averages(self, symbol: str, prices: list[float]) -> dict[str, Any]:
        """Calculate moving averages for a symbol."""
        result = {"current_price": prices[-1]}

        for period in [20, 50, 200]:
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

    def _calculate_rsi(self, prices: list[float], period: int = 14) -> dict[str, Any]:
        """Calculate RSI indicator."""
        rsi = calculations.calculate_rsi(prices, period)
        if not rsi:
            return {"rsi": None, "signal": "unknown"}

        current_rsi = rsi[-1]
        return {
            "rsi": current_rsi,
            "signal": "oversold" if current_rsi < 30 else "overbought" if current_rsi > 70 else "neutral",
        }

    def _calculate_macd(self, prices: list[float]) -> dict[str, Any]:
        """Calculate MACD indicator."""
        macd = calculations.calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9)

        if not macd["macd"]:
            return {"macd": None, "trend": "unknown", "crossover": None}

        histogram = macd["histogram"]
        signal = "bullish" if histogram[-1] > 0 else "bearish"

        crossover = None
        if len(histogram) >= 2:
            if histogram[-2] < 0 and histogram[-1] > 0:
                crossover = "bullish_crossover"
            elif histogram[-2] > 0 and histogram[-1] < 0:
                crossover = "bearish_crossover"

        return {
            "macd": macd["macd"][-1],
            "signal_line": macd["signal"][-1],
            "histogram": histogram[-1],
            "trend": signal,
            "crossover": crossover,
        }

    def _calculate_bollinger_bands(self, prices: list[float]) -> dict[str, Any]:
        """Calculate Bollinger Bands."""
        bb = calculations.calculate_bollinger_bands(prices, period=20, std_dev=2.0)

        if not bb["upper"]:
            return {"bb_position": None, "signal": "unknown", "band_width": None}

        current_price = prices[-1]
        upper = bb["upper"][-1]
        lower = bb["lower"][-1]
        middle = bb["middle"][-1]

        bb_position = (current_price - lower) / (upper - lower) if upper != lower else 0.5
        band_width = (upper - lower) / middle * 100

        return {
            "upper_band": upper,
            "middle_band": middle,
            "lower_band": lower,
            "bb_position": bb_position,
            "signal": "oversold" if bb_position < 0.2 else "overbought" if bb_position > 0.8 else "neutral",
            "band_width": band_width,
            "volatility_level": "low" if band_width < 5 else "high" if band_width > 15 else "moderate",
        }

    def _identify_support_resistance(self, prices: list[float]) -> dict[str, Any]:
        """Identify support and resistance levels."""
        levels = calculations.identify_support_resistance(prices)
        current_price = prices[-1]

        support_levels = [l for l in levels if l.type == "support"]
        resistance_levels = [l for l in levels if l.type == "resistance"]

        nearest_support = None
        nearest_resistance = None

        for level in support_levels:
            if level.level < current_price:
                if nearest_support is None or level.level > nearest_support:
                    nearest_support = level.level

        for level in resistance_levels:
            if level.level > current_price:
                if nearest_resistance is None or level.level < nearest_resistance:
                    nearest_resistance = level.level

        support_distance_pct = ((current_price - nearest_support) / current_price * 100) if nearest_support else None
        resistance_distance_pct = ((nearest_resistance - current_price) / current_price * 100) if nearest_resistance else None

        return {
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance,
            "support_distance_pct": support_distance_pct,
            "resistance_distance_pct": resistance_distance_pct,
        }

    def _calculate_trend(self, prices: list[float]) -> dict[str, Any]:
        """Calculate trend direction and strength."""
        trend = calculations.calculate_trend_strength(prices, 20)

        direction = "bullish" if trend["direction"] > 0 else "bearish" if trend["direction"] < 0 else "neutral"

        return {
            "direction": direction,
            "strength": abs(trend["trend_strength"]),
            "period_return": trend["total_return"] * 100,
        }

    def _aggregate_signals(self, rsi_signal: str, macd_trend: str, bb_signal: str, trend_direction: str) -> dict[str, Any]:
        """Aggregate multiple signals into overall assessment."""
        signals = [rsi_signal, macd_trend, bb_signal, trend_direction]

        bullish = sum(1 for s in signals if s in ["bullish", "oversold"])  # oversold is bullish signal
        bearish = sum(1 for s in signals if s in ["bearish", "overbought"])  # overbought is bearish signal
        total = len(signals)

        score = (bullish - bearish) / total if total > 0 else 0

        if score > 0.25:
            overall = "bullish"
        elif score < -0.25:
            overall = "bearish"
        else:
            overall = "neutral"

        confidence = "high" if abs(score) > 0.5 else "medium" if abs(score) > 0.25 else "low"

        return {
            "overall": overall,
            "score": score,
            "confidence": confidence,
        }

    def _generate_interpretation(self, symbol: str, trend: dict, momentum: dict, volatility: dict, signals: dict) -> str:
        """Generate human-readable interpretation."""
        parts = []

        # Trend interpretation
        if trend["direction"] == "bullish":
            parts.append(f"{symbol} is in an uptrend with {trend['strength']:.1%} strength")
        elif trend["direction"] == "bearish":
            parts.append(f"{symbol} is in a downtrend with {trend['strength']:.1%} strength")
        else:
            parts.append(f"{symbol} is trading sideways")

        # Momentum
        if momentum.get("rsi"):
            if momentum["rsi_signal"] == "oversold":
                parts.append("RSI indicates oversold conditions (potential bounce)")
            elif momentum["rsi_signal"] == "overbought":
                parts.append("RSI indicates overbought conditions (potential pullback)")

        if momentum.get("macd_crossover"):
            if momentum["macd_crossover"] == "bullish_crossover":
                parts.append("MACD just crossed bullish")
            elif momentum["macd_crossover"] == "bearish_crossover":
                parts.append("MACD just crossed bearish")

        # Volatility
        if volatility.get("volatility_level") == "high":
            parts.append("Volatility is elevated")
        elif volatility.get("volatility_level") == "low":
            parts.append("Volatility is compressed (potential breakout setup)")

        # Overall signal
        if signals["overall"] == "bullish":
            parts.append(f"Overall technical outlook is bullish ({signals['confidence']} confidence)")
        elif signals["overall"] == "bearish":
            parts.append(f"Overall technical outlook is bearish ({signals['confidence']} confidence)")
        else:
            parts.append("Technical signals are mixed")

        return ". ".join(parts) + "."

    def analyze(
        self,
        price_data: dict[str, list[dict[str, Any]]],
        symbols: list[str],
    ) -> AgentResult:
        """
        Perform technical analysis on price data using computational methods.

        Args:
            price_data: Dict mapping symbol to list of OHLCV data
            symbols: List of symbols to analyze

        Returns:
            AgentResult with technical analysis
        """
        # Extract closing prices
        self._price_cache = {}
        for symbol in symbols:
            if symbol in price_data:
                self._price_cache[symbol] = [p["close"] for p in price_data[symbol]]

        results = {"symbols": {}}
        interpretations = []

        for symbol in symbols:
            prices = self._price_cache.get(symbol, [])
            if not prices or len(prices) < 50:
                continue

            current_price = prices[-1]

            # Calculate all indicators
            ma_data = self._calculate_moving_averages(symbol, prices)
            rsi_data = self._calculate_rsi(prices)
            macd_data = self._calculate_macd(prices)
            bb_data = self._calculate_bollinger_bands(prices)
            levels_data = self._identify_support_resistance(prices)
            trend_data = self._calculate_trend(prices)

            # Determine MA alignment
            ma_alignment = "bullish" if ma_data.get("golden_cross") else "bearish"
            if ma_data.get("price_vs_sma_20", 0) > 0 and ma_data.get("price_vs_sma_50", 0) > 0:
                ma_alignment = "strongly bullish"
            elif ma_data.get("price_vs_sma_20", 0) < 0 and ma_data.get("price_vs_sma_50", 0) < 0:
                ma_alignment = "strongly bearish"

            # Aggregate signals
            signals = self._aggregate_signals(
                rsi_data.get("signal", "neutral"),
                macd_data.get("trend", "neutral"),
                bb_data.get("signal", "neutral"),
                trend_data.get("direction", "neutral"),
            )

            # Build symbol result
            symbol_result = {
                "current_price": current_price,
                "trend": {
                    "direction": trend_data["direction"],
                    "strength": trend_data["strength"],
                    "ma_alignment": ma_alignment,
                },
                "momentum": {
                    "rsi": rsi_data.get("rsi"),
                    "rsi_signal": rsi_data.get("signal"),
                    "macd_trend": macd_data.get("trend"),
                    "macd_crossover": macd_data.get("crossover"),
                },
                "volatility": {
                    "bb_position": bb_data.get("bb_position"),
                    "bb_signal": bb_data.get("signal"),
                    "volatility_level": bb_data.get("volatility_level"),
                },
                "levels": {
                    "nearest_support": levels_data.get("nearest_support"),
                    "nearest_resistance": levels_data.get("nearest_resistance"),
                    "support_distance_pct": levels_data.get("support_distance_pct"),
                    "resistance_distance_pct": levels_data.get("resistance_distance_pct"),
                },
                "signals": signals,
                "interpretation": self._generate_interpretation(symbol, trend_data,
                    {"rsi": rsi_data.get("rsi"), "rsi_signal": rsi_data.get("signal"),
                     "macd_crossover": macd_data.get("crossover")},
                    bb_data, signals),
            }

            results["symbols"][symbol] = symbol_result
            interpretations.append(f"{symbol}: {signals['overall']} ({signals['confidence']} confidence)")

        # Overall summary
        results["summary"] = "Technical analysis complete. " + "; ".join(interpretations) if interpretations else "No symbols analyzed."

        return AgentResult(
            success=True,
            data=results,
            error=None,
        )
