"""Economic data client using FRED API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from argent.tools.rate_limiter import DataSource, get_rate_limiter


@dataclass
class EconomicIndicator:
    """Normalized economic indicator data structure."""

    series_id: str
    name: str
    date: datetime
    value: float
    frequency: str
    units: str | None = None
    source: str = "fred"


# Key FRED series for financial analysis
FRED_SERIES: dict[str, dict[str, str]] = {
    # GDP and Growth
    "GDP": {"name": "Gross Domestic Product", "frequency": "quarterly"},
    "GDPC1": {"name": "Real Gross Domestic Product", "frequency": "quarterly"},
    # Inflation
    "CPIAUCSL": {"name": "Consumer Price Index", "frequency": "monthly"},
    "CPILFESL": {"name": "Core CPI (Ex Food & Energy)", "frequency": "monthly"},
    "PCEPI": {"name": "PCE Price Index", "frequency": "monthly"},
    # Employment
    "UNRATE": {"name": "Unemployment Rate", "frequency": "monthly"},
    "PAYEMS": {"name": "Total Nonfarm Payrolls", "frequency": "monthly"},
    "ICSA": {"name": "Initial Jobless Claims", "frequency": "weekly"},
    # Interest Rates
    "FEDFUNDS": {"name": "Federal Funds Rate", "frequency": "monthly"},
    "DFF": {"name": "Federal Funds Effective Rate", "frequency": "daily"},
    "DGS10": {"name": "10-Year Treasury Rate", "frequency": "daily"},
    "DGS2": {"name": "2-Year Treasury Rate", "frequency": "daily"},
    "DGS30": {"name": "30-Year Treasury Rate", "frequency": "daily"},
    "T10Y2Y": {"name": "10Y-2Y Treasury Spread", "frequency": "daily"},
    # Market Indicators
    "VIXCLS": {"name": "CBOE Volatility Index (VIX)", "frequency": "daily"},
    "SP500": {"name": "S&P 500 Index", "frequency": "daily"},
    # Consumer & Business
    "UMCSENT": {"name": "Consumer Sentiment", "frequency": "monthly"},
    "RSXFS": {"name": "Retail Sales Ex Food Services", "frequency": "monthly"},
    "INDPRO": {"name": "Industrial Production Index", "frequency": "monthly"},
    # Housing
    "HOUST": {"name": "Housing Starts", "frequency": "monthly"},
    "CSUSHPINSA": {"name": "Case-Shiller Home Price Index", "frequency": "monthly"},
    # Money Supply
    "M2SL": {"name": "M2 Money Supply", "frequency": "monthly"},
}


class EconomicDataClient:
    """Client for fetching economic data from FRED."""

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key
        self._rate_limiter = get_rate_limiter()
        self._fred = None

        if api_key:
            try:
                from fredapi import Fred

                self._fred = Fred(api_key=api_key)
            except ImportError:
                pass

    def _ensure_fred(self) -> bool:
        """Ensure FRED client is available."""
        return self._fred is not None

    def get_series(
        self,
        series_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> list[EconomicIndicator]:
        """
        Fetch a FRED data series.

        Args:
            series_id: FRED series identifier (e.g., 'GDP', 'UNRATE')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of observations

        Returns:
            List of EconomicIndicator objects
        """
        if not self._ensure_fred():
            return []

        self._rate_limiter.acquire_sync(DataSource.FRED)

        try:
            series = self._fred.get_series(
                series_id,
                observation_start=start_date,
                observation_end=end_date,
            )
        except Exception:
            return []

        series_info = FRED_SERIES.get(series_id, {"name": series_id, "frequency": "unknown"})

        result = []
        for date, value in series.tail(limit).items():
            if value is not None and not (isinstance(value, float) and value != value):  # Check for NaN
                result.append(
                    EconomicIndicator(
                        series_id=series_id,
                        name=series_info["name"],
                        date=date.to_pydatetime(),
                        value=float(value),
                        frequency=series_info["frequency"],
                    )
                )

        return result

    def get_latest_value(self, series_id: str) -> EconomicIndicator | None:
        """Get the most recent value for a series."""
        indicators = self.get_series(series_id, limit=1)
        return indicators[-1] if indicators else None

    def get_series_info(self, series_id: str) -> dict[str, Any] | None:
        """Get metadata about a FRED series."""
        if not self._ensure_fred():
            return None

        self._rate_limiter.acquire_sync(DataSource.FRED)

        try:
            info = self._fred.get_series_info(series_id)
            return {
                "series_id": series_id,
                "title": info.get("title"),
                "frequency": info.get("frequency"),
                "units": info.get("units"),
                "seasonal_adjustment": info.get("seasonal_adjustment"),
                "last_updated": info.get("last_updated"),
                "notes": info.get("notes", "")[:500] if info.get("notes") else None,
            }
        except Exception:
            return None

    def get_macro_snapshot(self) -> dict[str, Any]:
        """Get a snapshot of key macroeconomic indicators."""
        if not self._ensure_fred():
            return {"error": "FRED API key not configured"}

        snapshot = {}

        # Key indicators to fetch
        key_series = [
            "FEDFUNDS",
            "DGS10",
            "DGS2",
            "UNRATE",
            "CPIAUCSL",
            "VIXCLS",
            "UMCSENT",
        ]

        for series_id in key_series:
            indicator = self.get_latest_value(series_id)
            if indicator:
                snapshot[series_id] = {
                    "name": indicator.name,
                    "value": indicator.value,
                    "date": indicator.date.isoformat(),
                }

        # Calculate yield curve spread
        if "DGS10" in snapshot and "DGS2" in snapshot:
            snapshot["yield_curve_spread"] = {
                "name": "10Y-2Y Spread",
                "value": snapshot["DGS10"]["value"] - snapshot["DGS2"]["value"],
                "inverted": snapshot["DGS10"]["value"] < snapshot["DGS2"]["value"],
            }

        return snapshot

    def get_inflation_data(self, periods: int = 24) -> dict[str, Any]:
        """Get inflation-related indicators."""
        if not self._ensure_fred():
            return {}

        cpi = self.get_series("CPIAUCSL", limit=periods)
        core_cpi = self.get_series("CPILFESL", limit=periods)
        pce = self.get_series("PCEPI", limit=periods)

        def calc_yoy_change(data: list[EconomicIndicator]) -> float | None:
            if len(data) >= 13:
                return ((data[-1].value / data[-13].value) - 1) * 100
            return None

        return {
            "cpi": {
                "latest": cpi[-1].value if cpi else None,
                "yoy_change": calc_yoy_change(cpi),
                "date": cpi[-1].date.isoformat() if cpi else None,
            },
            "core_cpi": {
                "latest": core_cpi[-1].value if core_cpi else None,
                "yoy_change": calc_yoy_change(core_cpi),
                "date": core_cpi[-1].date.isoformat() if core_cpi else None,
            },
            "pce": {
                "latest": pce[-1].value if pce else None,
                "yoy_change": calc_yoy_change(pce),
                "date": pce[-1].date.isoformat() if pce else None,
            },
        }

    def get_employment_data(self, periods: int = 24) -> dict[str, Any]:
        """Get employment-related indicators."""
        if not self._ensure_fred():
            return {}

        unemployment = self.get_series("UNRATE", limit=periods)
        payrolls = self.get_series("PAYEMS", limit=periods)
        claims = self.get_series("ICSA", limit=12)

        return {
            "unemployment_rate": {
                "latest": unemployment[-1].value if unemployment else None,
                "change_1y": (unemployment[-1].value - unemployment[-13].value)
                if len(unemployment) >= 13
                else None,
                "date": unemployment[-1].date.isoformat() if unemployment else None,
            },
            "nonfarm_payrolls": {
                "latest": payrolls[-1].value if payrolls else None,
                "monthly_change": (payrolls[-1].value - payrolls[-2].value)
                if len(payrolls) >= 2
                else None,
                "date": payrolls[-1].date.isoformat() if payrolls else None,
            },
            "initial_claims": {
                "latest": claims[-1].value if claims else None,
                "date": claims[-1].date.isoformat() if claims else None,
            },
        }

    def get_interest_rates(self) -> dict[str, Any]:
        """Get current interest rate data."""
        if not self._ensure_fred():
            return {}

        rates = {}
        rate_series = ["FEDFUNDS", "DFF", "DGS2", "DGS10", "DGS30"]

        for series_id in rate_series:
            indicator = self.get_latest_value(series_id)
            if indicator:
                rates[series_id] = {
                    "name": indicator.name,
                    "value": indicator.value,
                    "date": indicator.date.isoformat(),
                }

        return rates

    def search_series(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search for FRED series by keyword."""
        if not self._ensure_fred():
            return []

        self._rate_limiter.acquire_sync(DataSource.FRED)

        try:
            results = self._fred.search(query, limit=limit)
            return [
                {
                    "series_id": row.name,
                    "title": row.get("title"),
                    "frequency": row.get("frequency"),
                    "units": row.get("units"),
                    "popularity": row.get("popularity"),
                }
                for _, row in results.iterrows()
            ]
        except Exception:
            return []
