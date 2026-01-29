"""Market data client using Yahoo Finance and Alpha Vantage."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd
import yfinance as yf

from argent.tools.cache import cached, get_cache
from argent.tools.rate_limiter import DataSource, get_rate_limiter


@dataclass
class PriceData:
    """Normalized price data structure."""

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    source: str


@dataclass
class CompanyInfo:
    """Company fundamental information."""

    symbol: str
    name: str
    sector: str | None
    industry: str | None
    market_cap: float | None
    pe_ratio: float | None
    forward_pe: float | None
    peg_ratio: float | None
    price_to_book: float | None
    dividend_yield: float | None
    profit_margin: float | None
    operating_margin: float | None
    roe: float | None
    debt_to_equity: float | None
    current_ratio: float | None
    revenue_growth: float | None
    earnings_growth: float | None
    beta: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None


class MarketDataClient:
    """Client for fetching stock and ETF market data."""

    def __init__(self, alpha_vantage_api_key: str | None = None):
        self.alpha_vantage_api_key = alpha_vantage_api_key
        self._rate_limiter = get_rate_limiter()
        # Register dataclasses for cache deserialization
        cache = get_cache()
        cache.register_dataclass(PriceData)
        cache.register_dataclass(CompanyInfo)

    @cached("price_history")
    def get_price_history(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> list[PriceData]:
        """
        Fetch historical price data for a symbol.

        Args:
            symbol: Stock/ETF ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            List of PriceData objects
        """
        self._rate_limiter.acquire_sync(DataSource.YAHOO_FINANCE)

        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            return []

        prices = []
        for timestamp, row in df.iterrows():
            prices.append(
                PriceData(
                    symbol=symbol,
                    timestamp=timestamp.to_pydatetime(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                    source="yahoo_finance",
                )
            )

        return prices

    @cached("current_price")
    def get_current_price(self, symbol: str) -> dict[str, Any]:
        """Get current price and basic info for a symbol."""
        self._rate_limiter.acquire_sync(DataSource.YAHOO_FINANCE)

        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "symbol": symbol,
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "previous_close": info.get("previousClose"),
            "open": info.get("open") or info.get("regularMarketOpen"),
            "day_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
            "day_low": info.get("dayLow") or info.get("regularMarketDayLow"),
            "volume": info.get("volume") or info.get("regularMarketVolume"),
            "market_cap": info.get("marketCap"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }

    @cached("company_info")
    def get_company_info(self, symbol: str) -> CompanyInfo:
        """Get detailed company fundamental information."""
        self._rate_limiter.acquire_sync(DataSource.YAHOO_FINANCE)

        ticker = yf.Ticker(symbol)
        info = ticker.info

        return CompanyInfo(
            symbol=symbol,
            name=info.get("longName") or info.get("shortName", symbol),
            sector=info.get("sector"),
            industry=info.get("industry"),
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            forward_pe=info.get("forwardPE"),
            peg_ratio=info.get("pegRatio"),
            price_to_book=info.get("priceToBook"),
            dividend_yield=info.get("dividendYield"),
            profit_margin=info.get("profitMargins"),
            operating_margin=info.get("operatingMargins"),
            roe=info.get("returnOnEquity"),
            debt_to_equity=info.get("debtToEquity"),
            current_ratio=info.get("currentRatio"),
            revenue_growth=info.get("revenueGrowth"),
            earnings_growth=info.get("earningsGrowth"),
            beta=info.get("beta"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
        )

    @cached("financials")
    def get_financials(self, symbol: str) -> dict[str, Any]:
        """Get company financial statements."""
        self._rate_limiter.acquire_sync(DataSource.YAHOO_FINANCE)

        ticker = yf.Ticker(symbol)

        def df_to_dict(df: pd.DataFrame) -> dict[str, Any]:
            if df.empty:
                return {}
            result = {}
            for col in df.columns:
                col_data = {}
                for idx, val in df[col].items():
                    if pd.notna(val):
                        col_data[str(idx)] = float(val) if isinstance(val, (int, float)) else val
                result[str(col.date())] = col_data
            return result

        return {
            "income_statement": df_to_dict(ticker.income_stmt),
            "balance_sheet": df_to_dict(ticker.balance_sheet),
            "cash_flow": df_to_dict(ticker.cashflow),
        }

    @cached("recommendations")
    def get_recommendations(self, symbol: str) -> list[dict[str, Any]]:
        """Get analyst recommendations for a symbol."""
        self._rate_limiter.acquire_sync(DataSource.YAHOO_FINANCE)

        ticker = yf.Ticker(symbol)
        recs = ticker.recommendations

        if recs is None or recs.empty:
            return []

        result = []
        for timestamp, row in recs.tail(10).iterrows():
            result.append(
                {
                    "date": str(timestamp.date()) if hasattr(timestamp, "date") else str(timestamp),
                    "firm": row.get("Firm", "Unknown"),
                    "to_grade": row.get("To Grade", row.get("toGrade")),
                    "from_grade": row.get("From Grade", row.get("fromGrade")),
                    "action": row.get("Action", row.get("action")),
                }
            )

        return result

    def search_symbols(self, query: str) -> list[dict[str, str]]:
        """Search for symbols matching a query."""
        self._rate_limiter.acquire_sync(DataSource.YAHOO_FINANCE)

        try:
            results = yf.Tickers(query)
            return [{"symbol": query, "name": query}]
        except Exception:
            return []
