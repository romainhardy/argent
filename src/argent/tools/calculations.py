"""Quantitative analysis calculations for financial data."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class TechnicalSignal:
    """Technical analysis signal."""

    indicator: str
    value: float
    signal: str  # bullish, bearish, neutral
    strength: float  # 0-1


@dataclass
class SupportResistance:
    """Support/resistance level."""

    level: float
    type: str  # support, resistance
    strength: int  # number of touches
    last_touch: int  # index of last touch


def calculate_sma(prices: list[float], period: int) -> list[float]:
    """Calculate Simple Moving Average."""
    if len(prices) < period:
        return []

    series = pd.Series(prices)
    sma = series.rolling(window=period).mean()
    return sma.dropna().tolist()


def calculate_ema(prices: list[float], period: int) -> list[float]:
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return []

    series = pd.Series(prices)
    ema = series.ewm(span=period, adjust=False).mean()
    return ema.tolist()


def calculate_rsi(prices: list[float], period: int = 14) -> list[float]:
    """
    Calculate Relative Strength Index.

    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss
    """
    if len(prices) < period + 1:
        return []

    series = pd.Series(prices)
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.dropna().tolist()


def calculate_macd(
    prices: list[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> dict[str, list[float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Returns:
        dict with 'macd', 'signal', and 'histogram' lists
    """
    if len(prices) < slow_period + signal_period:
        return {"macd": [], "signal": [], "histogram": []}

    series = pd.Series(prices)
    ema_fast = series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = series.ewm(span=slow_period, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line

    return {
        "macd": macd_line.dropna().tolist(),
        "signal": signal_line.dropna().tolist(),
        "histogram": histogram.dropna().tolist(),
    }


def calculate_bollinger_bands(
    prices: list[float],
    period: int = 20,
    std_dev: float = 2.0,
) -> dict[str, list[float]]:
    """
    Calculate Bollinger Bands.

    Returns:
        dict with 'upper', 'middle', 'lower' bands
    """
    if len(prices) < period:
        return {"upper": [], "middle": [], "lower": []}

    series = pd.Series(prices)
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return {
        "upper": upper.dropna().tolist(),
        "middle": middle.dropna().tolist(),
        "lower": lower.dropna().tolist(),
    }


def calculate_atr(
    high: list[float],
    low: list[float],
    close: list[float],
    period: int = 14,
) -> list[float]:
    """
    Calculate Average True Range.

    ATR = Average of True Range over period
    True Range = max(high-low, |high-prev_close|, |low-prev_close|)
    """
    if len(high) < period + 1:
        return []

    high_arr = np.array(high)
    low_arr = np.array(low)
    close_arr = np.array(close)

    prev_close = np.roll(close_arr, 1)
    prev_close[0] = close_arr[0]

    tr1 = high_arr - low_arr
    tr2 = np.abs(high_arr - prev_close)
    tr3 = np.abs(low_arr - prev_close)

    true_range = np.maximum(tr1, np.maximum(tr2, tr3))

    atr = pd.Series(true_range).rolling(window=period).mean()
    return atr.dropna().tolist()


def calculate_returns(prices: list[float]) -> list[float]:
    """Calculate simple returns."""
    if len(prices) < 2:
        return []

    series = pd.Series(prices)
    returns = series.pct_change()
    return returns.dropna().tolist()


def calculate_log_returns(prices: list[float]) -> list[float]:
    """Calculate logarithmic returns."""
    if len(prices) < 2:
        return []

    series = pd.Series(prices)
    log_returns = np.log(series / series.shift(1))
    return log_returns.dropna().tolist()


def calculate_volatility(prices: list[float], period: int = 252, annualize: bool = True) -> float:
    """
    Calculate annualized volatility.

    Args:
        prices: Price series
        period: Trading days for annualization (252 for daily, 52 for weekly)
        annualize: Whether to annualize the result

    Returns:
        Volatility as a decimal (e.g., 0.20 for 20%)
    """
    returns = calculate_log_returns(prices)
    if not returns:
        return 0.0

    std = np.std(returns)
    if annualize:
        return float(std * np.sqrt(period))
    return float(std)


def calculate_beta(
    asset_prices: list[float],
    market_prices: list[float],
) -> float:
    """
    Calculate beta (systematic risk) relative to market.

    Beta = Cov(asset, market) / Var(market)
    """
    asset_returns = calculate_log_returns(asset_prices)
    market_returns = calculate_log_returns(market_prices)

    if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
        return 1.0

    covariance = np.cov(asset_returns, market_returns)[0][1]
    market_variance = np.var(market_returns)

    if market_variance == 0:
        return 1.0

    return float(covariance / market_variance)


def calculate_correlation_matrix(
    price_series: dict[str, list[float]],
) -> dict[str, dict[str, float]]:
    """
    Calculate correlation matrix for multiple assets.

    Args:
        price_series: Dict mapping symbol to price list

    Returns:
        Nested dict of correlations
    """
    returns_dict = {}
    min_length = float("inf")

    for symbol, prices in price_series.items():
        returns = calculate_log_returns(prices)
        if returns:
            returns_dict[symbol] = returns
            min_length = min(min_length, len(returns))

    if not returns_dict or min_length < 2:
        return {}

    # Truncate to same length
    symbols = list(returns_dict.keys())
    data = np.array([returns_dict[s][-int(min_length) :] for s in symbols])

    corr_matrix = np.corrcoef(data)

    result = {}
    for i, sym1 in enumerate(symbols):
        result[sym1] = {}
        for j, sym2 in enumerate(symbols):
            result[sym1][sym2] = float(corr_matrix[i][j])

    return result


def calculate_var(
    prices: list[float],
    confidence: float = 0.95,
    horizon: int = 1,
) -> dict[str, float]:
    """
    Calculate Value at Risk using historical method.

    Args:
        prices: Price series
        confidence: Confidence level (e.g., 0.95 for 95%)
        horizon: Time horizon in days

    Returns:
        dict with VaR metrics
    """
    returns = calculate_log_returns(prices)
    if len(returns) < 30:
        return {"var": 0.0, "confidence": confidence, "horizon": horizon}

    returns_arr = np.array(returns)

    # Historical VaR
    var_percentile = np.percentile(returns_arr, (1 - confidence) * 100)

    # Scale for horizon (square root of time)
    var_scaled = var_percentile * np.sqrt(horizon)

    # Expected Shortfall (CVaR) - average of losses beyond VaR
    cvar = returns_arr[returns_arr <= var_percentile].mean()

    return {
        "var": float(abs(var_scaled)),
        "cvar": float(abs(cvar)) if not np.isnan(cvar) else 0.0,
        "confidence": confidence,
        "horizon": horizon,
        "worst_day": float(returns_arr.min()),
        "best_day": float(returns_arr.max()),
    }


def calculate_max_drawdown(prices: list[float]) -> dict[str, float]:
    """
    Calculate maximum drawdown.

    Returns:
        dict with max_drawdown, peak_date_idx, trough_date_idx
    """
    if len(prices) < 2:
        return {"max_drawdown": 0.0, "peak_idx": 0, "trough_idx": 0}

    prices_arr = np.array(prices)
    cummax = np.maximum.accumulate(prices_arr)
    drawdown = (prices_arr - cummax) / cummax

    max_dd_idx = np.argmin(drawdown)
    max_dd = drawdown[max_dd_idx]

    peak_idx = np.argmax(prices_arr[: max_dd_idx + 1]) if max_dd_idx > 0 else 0

    return {
        "max_drawdown": float(abs(max_dd)),
        "peak_idx": int(peak_idx),
        "trough_idx": int(max_dd_idx),
        "recovery_idx": None,  # Would need to track when price returns to peak
    }


def calculate_sharpe_ratio(
    prices: list[float],
    risk_free_rate: float = 0.05,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate Sharpe Ratio.

    Sharpe = (Return - Risk Free Rate) / Volatility
    """
    returns = calculate_log_returns(prices)
    if len(returns) < 2:
        return 0.0

    mean_return = np.mean(returns) * periods_per_year
    volatility = np.std(returns) * np.sqrt(periods_per_year)

    if volatility == 0:
        return 0.0

    return float((mean_return - risk_free_rate) / volatility)


def calculate_sortino_ratio(
    prices: list[float],
    risk_free_rate: float = 0.05,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate Sortino Ratio (uses downside deviation instead of total volatility).

    Sortino = (Return - Risk Free Rate) / Downside Deviation
    """
    returns = calculate_log_returns(prices)
    if len(returns) < 2:
        return 0.0

    returns_arr = np.array(returns)
    mean_return = np.mean(returns_arr) * periods_per_year

    # Downside deviation - only consider negative returns
    downside_returns = returns_arr[returns_arr < 0]
    if len(downside_returns) == 0:
        return float("inf") if mean_return > risk_free_rate else 0.0

    downside_std = np.std(downside_returns) * np.sqrt(periods_per_year)

    if downside_std == 0:
        return 0.0

    return float((mean_return - risk_free_rate) / downside_std)


def identify_support_resistance(
    prices: list[float],
    window: int = 10,
    threshold: float = 0.02,
) -> list[SupportResistance]:
    """
    Identify support and resistance levels.

    Args:
        prices: Price series
        window: Window size for local min/max detection
        threshold: Percentage threshold for level clustering

    Returns:
        List of SupportResistance objects
    """
    if len(prices) < window * 2:
        return []

    prices_arr = np.array(prices)
    levels = []

    # Find local minima (support) and maxima (resistance)
    for i in range(window, len(prices_arr) - window):
        window_before = prices_arr[i - window : i]
        window_after = prices_arr[i + 1 : i + window + 1]

        # Local minimum (potential support)
        if prices_arr[i] <= window_before.min() and prices_arr[i] <= window_after.min():
            levels.append({"level": prices_arr[i], "type": "support", "idx": i})

        # Local maximum (potential resistance)
        if prices_arr[i] >= window_before.max() and prices_arr[i] >= window_after.max():
            levels.append({"level": prices_arr[i], "type": "resistance", "idx": i})

    # Cluster nearby levels
    clustered = []
    for level in levels:
        merged = False
        for cluster in clustered:
            if abs(level["level"] - cluster["level"]) / cluster["level"] < threshold:
                # Merge into existing cluster
                cluster["touches"].append(level["idx"])
                cluster["level"] = (cluster["level"] + level["level"]) / 2
                merged = True
                break
        if not merged:
            clustered.append(
                {
                    "level": level["level"],
                    "type": level["type"],
                    "touches": [level["idx"]],
                }
            )

    # Convert to SupportResistance objects
    result = []
    for cluster in clustered:
        if len(cluster["touches"]) >= 2:  # Only include levels with multiple touches
            result.append(
                SupportResistance(
                    level=cluster["level"],
                    type=cluster["type"],
                    strength=len(cluster["touches"]),
                    last_touch=max(cluster["touches"]),
                )
            )

    # Sort by strength
    result.sort(key=lambda x: x.strength, reverse=True)
    return result[:10]  # Return top 10 levels


def calculate_technical_signals(prices: list[float]) -> list[TechnicalSignal]:
    """Calculate multiple technical signals and their interpretations."""
    if len(prices) < 50:
        return []

    signals = []
    current_price = prices[-1]

    # RSI Signal
    rsi = calculate_rsi(prices)
    if rsi:
        rsi_val = rsi[-1]
        if rsi_val < 30:
            signal = "bullish"
            strength = (30 - rsi_val) / 30
        elif rsi_val > 70:
            signal = "bearish"
            strength = (rsi_val - 70) / 30
        else:
            signal = "neutral"
            strength = 0.5
        signals.append(TechnicalSignal("RSI", rsi_val, signal, min(strength, 1.0)))

    # MACD Signal
    macd = calculate_macd(prices)
    if macd["histogram"]:
        hist = macd["histogram"][-1]
        prev_hist = macd["histogram"][-2] if len(macd["histogram"]) > 1 else 0
        if hist > 0 and hist > prev_hist:
            signal = "bullish"
            strength = 0.7
        elif hist < 0 and hist < prev_hist:
            signal = "bearish"
            strength = 0.7
        else:
            signal = "neutral"
            strength = 0.3
        signals.append(TechnicalSignal("MACD", hist, signal, strength))

    # Moving Average Signal
    sma_50 = calculate_sma(prices, 50)
    sma_200 = calculate_sma(prices, 200)
    if sma_50 and sma_200:
        if sma_50[-1] > sma_200[-1]:
            signal = "bullish"
            strength = min((sma_50[-1] - sma_200[-1]) / sma_200[-1] * 10, 1.0)
        else:
            signal = "bearish"
            strength = min((sma_200[-1] - sma_50[-1]) / sma_200[-1] * 10, 1.0)
        signals.append(TechnicalSignal("MA_Cross", sma_50[-1], signal, strength))

    # Bollinger Band Signal
    bb = calculate_bollinger_bands(prices)
    if bb["upper"] and bb["lower"]:
        bb_position = (current_price - bb["lower"][-1]) / (bb["upper"][-1] - bb["lower"][-1])
        if bb_position < 0.2:
            signal = "bullish"
            strength = 1 - bb_position * 5
        elif bb_position > 0.8:
            signal = "bearish"
            strength = (bb_position - 0.8) * 5
        else:
            signal = "neutral"
            strength = 0.5
        signals.append(TechnicalSignal("Bollinger", bb_position, signal, min(strength, 1.0)))

    return signals


def calculate_trend_strength(prices: list[float], period: int = 20) -> dict[str, float]:
    """Calculate trend strength using ADX-like methodology."""
    if len(prices) < period * 2:
        return {"trend_strength": 0.0, "direction": 0.0}

    returns = calculate_returns(prices[-period:])
    if not returns:
        return {"trend_strength": 0.0, "direction": 0.0}

    # Simple trend strength: consistency of direction
    positive_returns = sum(1 for r in returns if r > 0)
    trend_consistency = abs(positive_returns / len(returns) - 0.5) * 2

    # Direction: positive = uptrend, negative = downtrend
    total_return = (prices[-1] / prices[-period] - 1)
    direction = 1.0 if total_return > 0 else -1.0

    return {
        "trend_strength": trend_consistency,
        "direction": direction,
        "total_return": total_return,
    }
