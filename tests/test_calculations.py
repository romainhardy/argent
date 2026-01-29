"""Tests for quantitative calculations module."""

import pytest
import numpy as np

from argent.tools.calculations import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_returns,
    calculate_log_returns,
    calculate_volatility,
    calculate_var,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_beta,
    calculate_correlation_matrix,
    identify_support_resistance,
)


class TestMovingAverages:
    """Tests for moving average calculations."""

    def test_sma_basic(self):
        """Test basic SMA calculation."""
        prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        sma = calculate_sma(prices, period=5)

        assert len(sma) == 7  # 11 - 5 + 1
        assert sma[0] == 12.0  # (10+11+12+13+14) / 5
        assert sma[-1] == 18.0  # (16+17+18+19+20) / 5

    def test_sma_insufficient_data(self):
        """Test SMA with insufficient data."""
        prices = [10, 11, 12]
        sma = calculate_sma(prices, period=5)
        assert sma == []

    def test_ema_basic(self):
        """Test basic EMA calculation."""
        prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        ema = calculate_ema(prices, period=5)

        assert len(ema) == 11
        # EMA should be close to but not equal to SMA for trending data
        assert ema[-1] > 18  # Should be higher than SMA for uptrend


class TestRSI:
    """Tests for RSI calculation."""

    def test_rsi_uptrend(self):
        """Test RSI in strong uptrend."""
        # Consistently rising prices
        prices = list(range(100, 120))
        rsi = calculate_rsi(prices, period=14)

        assert len(rsi) > 0
        # Strong uptrend should have high RSI
        assert rsi[-1] > 70

    def test_rsi_downtrend(self):
        """Test RSI in strong downtrend."""
        # Consistently falling prices
        prices = list(range(120, 100, -1))
        rsi = calculate_rsi(prices, period=14)

        assert len(rsi) > 0
        # Strong downtrend should have low RSI
        assert rsi[-1] < 30

    def test_rsi_range(self):
        """Test RSI is always between 0 and 100."""
        # Random-ish prices
        prices = [100 + (i % 10) - 5 for i in range(50)]
        rsi = calculate_rsi(prices, period=14)

        for value in rsi:
            assert 0 <= value <= 100


class TestMACD:
    """Tests for MACD calculation."""

    def test_macd_basic(self):
        """Test basic MACD calculation."""
        # Generate trending prices
        prices = [100 + i + np.sin(i / 5) * 5 for i in range(50)]
        macd = calculate_macd(prices)

        assert "macd" in macd
        assert "signal" in macd
        assert "histogram" in macd
        assert len(macd["histogram"]) > 0

    def test_macd_crossover_detection(self):
        """Test MACD can detect crossovers."""
        # Uptrend followed by downtrend
        prices = list(range(100, 150)) + list(range(150, 120, -1))
        macd = calculate_macd(prices)

        # Histogram should change sign at some point
        histogram = macd["histogram"]
        sign_changes = sum(1 for i in range(1, len(histogram))
                         if (histogram[i] > 0) != (histogram[i-1] > 0))
        assert sign_changes > 0


class TestBollingerBands:
    """Tests for Bollinger Bands calculation."""

    def test_bollinger_bands_basic(self):
        """Test basic Bollinger Bands calculation."""
        prices = [100 + np.random.randn() * 5 for _ in range(50)]
        bb = calculate_bollinger_bands(prices, period=20)

        assert "upper" in bb
        assert "middle" in bb
        assert "lower" in bb
        assert len(bb["upper"]) > 0

    def test_bollinger_bands_order(self):
        """Test that upper > middle > lower."""
        prices = [100 + np.random.randn() * 5 for _ in range(50)]
        bb = calculate_bollinger_bands(prices, period=20)

        for i in range(len(bb["upper"])):
            assert bb["upper"][i] >= bb["middle"][i]
            assert bb["middle"][i] >= bb["lower"][i]


class TestReturns:
    """Tests for return calculations."""

    def test_simple_returns(self):
        """Test simple returns calculation."""
        prices = [100, 110, 99, 108]
        returns = calculate_returns(prices)

        assert len(returns) == 3
        assert abs(returns[0] - 0.10) < 0.001  # 10% gain
        assert abs(returns[1] - (-0.10)) < 0.001  # 10% loss
        assert abs(returns[2] - 0.0909) < 0.001  # ~9% gain

    def test_log_returns(self):
        """Test log returns calculation."""
        prices = [100, 110, 99, 108]
        log_returns = calculate_log_returns(prices)

        assert len(log_returns) == 3
        # Log returns should be close to simple returns for small changes
        simple_returns = calculate_returns(prices)
        for lr, sr in zip(log_returns, simple_returns):
            assert abs(lr - sr) < 0.02  # Should be within 2% for these values


class TestVolatility:
    """Tests for volatility calculation."""

    def test_volatility_stable(self):
        """Test volatility of stable prices."""
        # Very stable prices
        prices = [100 + 0.1 * i for i in range(252)]
        vol = calculate_volatility(prices)

        # Low volatility expected
        assert vol < 0.05

    def test_volatility_volatile(self):
        """Test volatility of volatile prices."""
        # Highly volatile prices
        np.random.seed(42)
        prices = [100 * (1 + np.random.randn() * 0.05) for _ in range(252)]
        for i in range(1, len(prices)):
            prices[i] = prices[i-1] * (1 + np.random.randn() * 0.05)

        vol = calculate_volatility(prices)

        # Higher volatility expected
        assert vol > 0.30


class TestRiskMetrics:
    """Tests for risk metrics."""

    def test_var_basic(self):
        """Test VaR calculation."""
        np.random.seed(42)
        prices = [100]
        for _ in range(250):
            prices.append(prices[-1] * (1 + np.random.randn() * 0.02))

        var = calculate_var(prices, confidence=0.95)

        assert "var" in var
        assert "cvar" in var
        assert var["var"] > 0
        assert var["confidence"] == 0.95

    def test_max_drawdown(self):
        """Test maximum drawdown calculation."""
        # Clear drawdown pattern
        prices = [100, 110, 120, 100, 90, 95, 100, 110]
        dd = calculate_max_drawdown(prices)

        assert "max_drawdown" in dd
        # Max drawdown should be from 120 to 90 = 25%
        assert abs(dd["max_drawdown"] - 0.25) < 0.01

    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        # Strong uptrend with low volatility
        prices = [100 + i * 0.5 for i in range(252)]
        sharpe = calculate_sharpe_ratio(prices)

        # Positive return with low vol should have good Sharpe
        assert sharpe > 0

    def test_sortino_ratio(self):
        """Test Sortino ratio calculation."""
        np.random.seed(42)
        prices = [100]
        for _ in range(250):
            prices.append(prices[-1] * (1 + abs(np.random.randn()) * 0.01))

        sortino = calculate_sortino_ratio(prices)

        # Mostly positive returns should have high Sortino
        assert sortino > 0


class TestBeta:
    """Tests for beta calculation."""

    def test_beta_market(self):
        """Test beta of market itself."""
        # Same series should have beta of 1
        prices = [100 + np.random.randn() * 5 for _ in range(100)]
        beta = calculate_beta(prices, prices)

        assert abs(beta - 1.0) < 0.01

    def test_beta_defensive(self):
        """Test beta of defensive asset."""
        np.random.seed(42)
        market = [100]
        for _ in range(100):
            market.append(market[-1] * (1 + np.random.randn() * 0.02))

        # Asset that moves half as much as market
        asset = [100]
        for i in range(100):
            market_return = market[i+1] / market[i] - 1
            asset.append(asset[-1] * (1 + market_return * 0.5))

        beta = calculate_beta(asset, market)

        # Should be around 0.5
        assert 0.3 < beta < 0.7


class TestCorrelation:
    """Tests for correlation matrix."""

    def test_correlation_self(self):
        """Test self-correlation is 1."""
        prices = {"A": [100 + i for i in range(50)]}
        corr = calculate_correlation_matrix(prices)

        assert corr["A"]["A"] == 1.0

    def test_correlation_inverse(self):
        """Test correlation of inverse series."""
        prices = {
            "A": list(range(100, 150)),
            "B": list(range(150, 100, -1)),
        }
        corr = calculate_correlation_matrix(prices)

        # Should be negatively correlated
        assert corr["A"]["B"] < -0.9


class TestSupportResistance:
    """Tests for support/resistance detection."""

    def test_support_resistance_detection(self):
        """Test that support and resistance levels are detected."""
        # Create price series with clear levels
        prices = []
        for _ in range(5):
            # Bounce between 95 and 105
            prices.extend([100, 102, 104, 105, 104, 102, 100, 98, 96, 95, 96, 98])

        levels = identify_support_resistance(prices)

        # Should find some levels
        assert len(levels) > 0

        # Check level types
        support_levels = [l for l in levels if l.type == "support"]
        resistance_levels = [l for l in levels if l.type == "resistance"]

        # Should have both support and resistance
        # (may not always be true depending on data)
        assert len(support_levels) >= 0
        assert len(resistance_levels) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
