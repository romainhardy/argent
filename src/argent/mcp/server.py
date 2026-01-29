"""MCP Server exposing Argent financial tools to Claude.

This server provides financial data and calculation tools that can be
used directly by Claude through the Model Context Protocol.

Run the server:
    python -m argent.mcp.server

Or use with Claude Code:
    Configure in .mcp.json
"""

import asyncio
import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from argent.tools.market_data import MarketDataClient, PriceData, CompanyInfo
from argent.tools.crypto_data import CryptoDataClient
from argent.tools.economic_data import EconomicDataClient
from argent.tools.calculations import (
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_var,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_beta,
    calculate_max_drawdown,
)

# Initialize clients (lazy loading)
_market_client: MarketDataClient | None = None
_crypto_client: CryptoDataClient | None = None
_econ_client: EconomicDataClient | None = None


def get_market_client() -> MarketDataClient:
    """Get or create market data client."""
    global _market_client
    if _market_client is None:
        _market_client = MarketDataClient()
    return _market_client


def get_crypto_client() -> CryptoDataClient:
    """Get or create crypto data client."""
    global _crypto_client
    if _crypto_client is None:
        _crypto_client = CryptoDataClient()
    return _crypto_client


def get_econ_client() -> EconomicDataClient:
    """Get or create economic data client."""
    global _econ_client
    if _econ_client is None:
        api_key = os.environ.get("FRED_API_KEY")
        _econ_client = EconomicDataClient(api_key=api_key)
    return _econ_client


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("argent-tools")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return [
            Tool(
                name="get_stock_price",
                description="Get current stock price and basic metrics for a symbol",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol (e.g., AAPL, MSFT)",
                        }
                    },
                    "required": ["symbol"],
                },
            ),
            Tool(
                name="get_stock_history",
                description="Get historical OHLCV price data for a stock",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol",
                        },
                        "period": {
                            "type": "string",
                            "description": "Data period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max",
                            "default": "1y",
                        },
                        "interval": {
                            "type": "string",
                            "description": "Data interval: 1d, 1wk, 1mo",
                            "default": "1d",
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            Tool(
                name="get_company_info",
                description="Get company fundamental information including P/E, margins, growth metrics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol",
                        }
                    },
                    "required": ["symbol"],
                },
            ),
            Tool(
                name="get_crypto_price",
                description="Get current cryptocurrency prices",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of crypto symbols (e.g., ['BTC', 'ETH'])",
                        }
                    },
                    "required": ["symbols"],
                },
            ),
            Tool(
                name="get_economic_data",
                description="Get FRED economic indicator data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "series_id": {
                            "type": "string",
                            "description": "FRED series ID (e.g., FEDFUNDS, DGS10, UNRATE, CPIAUCSL)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of observations",
                            "default": 12,
                        },
                    },
                    "required": ["series_id"],
                },
            ),
            Tool(
                name="get_macro_snapshot",
                description="Get snapshot of key macroeconomic indicators",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="calculate_rsi",
                description="Calculate Relative Strength Index for price data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prices": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "List of closing prices",
                        },
                        "period": {
                            "type": "integer",
                            "description": "RSI period (default 14)",
                            "default": 14,
                        },
                    },
                    "required": ["prices"],
                },
            ),
            Tool(
                name="calculate_macd",
                description="Calculate MACD indicator for price data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prices": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "List of closing prices",
                        },
                        "fast_period": {
                            "type": "integer",
                            "default": 12,
                        },
                        "slow_period": {
                            "type": "integer",
                            "default": 26,
                        },
                        "signal_period": {
                            "type": "integer",
                            "default": 9,
                        },
                    },
                    "required": ["prices"],
                },
            ),
            Tool(
                name="calculate_var",
                description="Calculate Value at Risk for price data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prices": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "List of prices",
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level (e.g., 0.95)",
                            "default": 0.95,
                        },
                        "horizon": {
                            "type": "integer",
                            "description": "Time horizon in days",
                            "default": 1,
                        },
                    },
                    "required": ["prices"],
                },
            ),
            Tool(
                name="calculate_volatility",
                description="Calculate annualized volatility for price data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prices": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "List of prices",
                        },
                        "period": {
                            "type": "integer",
                            "description": "Trading days per year",
                            "default": 252,
                        },
                    },
                    "required": ["prices"],
                },
            ),
            Tool(
                name="calculate_sharpe",
                description="Calculate Sharpe ratio for price data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prices": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "List of prices",
                        },
                        "risk_free_rate": {
                            "type": "number",
                            "description": "Annual risk-free rate",
                            "default": 0.05,
                        },
                    },
                    "required": ["prices"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        try:
            result = await _execute_tool(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, default=str, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    return server


async def _execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Execute a tool and return the result."""

    if name == "get_stock_price":
        client = get_market_client()
        return client.get_current_price(arguments["symbol"])

    elif name == "get_stock_history":
        client = get_market_client()
        period = arguments.get("period", "1y")
        interval = arguments.get("interval", "1d")
        prices = client.get_price_history(arguments["symbol"], period=period, interval=interval)
        # Convert dataclasses to dicts
        return [
            {
                "timestamp": p.timestamp.isoformat(),
                "open": p.open,
                "high": p.high,
                "low": p.low,
                "close": p.close,
                "volume": p.volume,
            }
            for p in prices[-100:]  # Limit to last 100 for response size
        ]

    elif name == "get_company_info":
        client = get_market_client()
        info = client.get_company_info(arguments["symbol"])
        # Convert dataclass to dict
        return {
            "symbol": info.symbol,
            "name": info.name,
            "sector": info.sector,
            "industry": info.industry,
            "market_cap": info.market_cap,
            "pe_ratio": info.pe_ratio,
            "forward_pe": info.forward_pe,
            "peg_ratio": info.peg_ratio,
            "price_to_book": info.price_to_book,
            "dividend_yield": info.dividend_yield,
            "profit_margin": info.profit_margin,
            "operating_margin": info.operating_margin,
            "roe": info.roe,
            "debt_to_equity": info.debt_to_equity,
            "revenue_growth": info.revenue_growth,
            "earnings_growth": info.earnings_growth,
            "beta": info.beta,
        }

    elif name == "get_crypto_price":
        client = get_crypto_client()
        symbols = arguments["symbols"]
        if isinstance(symbols, str):
            symbols = [symbols]
        prices = client.get_current_price(symbols)
        # Convert dataclasses to dicts
        return {
            symbol: {
                "price_usd": p.price_usd,
                "market_cap": p.market_cap,
                "volume_24h": p.volume_24h,
                "price_change_24h": p.price_change_24h,
                "price_change_7d": p.price_change_7d,
            }
            for symbol, p in prices.items()
        }

    elif name == "get_economic_data":
        client = get_econ_client()
        series_id = arguments["series_id"]
        limit = arguments.get("limit", 12)
        data = client.get_series(series_id, limit=limit)
        return [
            {
                "date": d.date.isoformat(),
                "value": d.value,
                "name": d.name,
            }
            for d in data
        ]

    elif name == "get_macro_snapshot":
        client = get_econ_client()
        return client.get_macro_snapshot()

    elif name == "calculate_rsi":
        prices = arguments["prices"]
        period = arguments.get("period", 14)
        rsi = calculate_rsi(prices, period=period)
        return {
            "rsi_values": rsi[-10:] if len(rsi) > 10 else rsi,
            "current_rsi": rsi[-1] if rsi else None,
            "interpretation": _interpret_rsi(rsi[-1]) if rsi else "Insufficient data",
        }

    elif name == "calculate_macd":
        prices = arguments["prices"]
        result = calculate_macd(
            prices,
            fast_period=arguments.get("fast_period", 12),
            slow_period=arguments.get("slow_period", 26),
            signal_period=arguments.get("signal_period", 9),
        )
        return {
            "macd": result["macd"][-1] if result["macd"] else None,
            "signal": result["signal"][-1] if result["signal"] else None,
            "histogram": result["histogram"][-1] if result["histogram"] else None,
            "interpretation": _interpret_macd(result) if result["histogram"] else "Insufficient data",
        }

    elif name == "calculate_var":
        prices = arguments["prices"]
        confidence = arguments.get("confidence", 0.95)
        horizon = arguments.get("horizon", 1)
        return calculate_var(prices, confidence=confidence, horizon=horizon)

    elif name == "calculate_volatility":
        prices = arguments["prices"]
        period = arguments.get("period", 252)
        vol = calculate_volatility(prices, period=period)
        return {
            "annualized_volatility": vol,
            "annualized_volatility_pct": vol * 100,
            "interpretation": _interpret_volatility(vol),
        }

    elif name == "calculate_sharpe":
        prices = arguments["prices"]
        risk_free_rate = arguments.get("risk_free_rate", 0.05)
        sharpe = calculate_sharpe_ratio(prices, risk_free_rate=risk_free_rate)
        return {
            "sharpe_ratio": sharpe,
            "interpretation": _interpret_sharpe(sharpe),
        }

    else:
        raise ValueError(f"Unknown tool: {name}")


def _interpret_rsi(rsi: float) -> str:
    """Interpret RSI value."""
    if rsi < 30:
        return "Oversold - potential buying opportunity"
    elif rsi > 70:
        return "Overbought - potential selling opportunity"
    elif rsi < 40:
        return "Approaching oversold territory"
    elif rsi > 60:
        return "Approaching overbought territory"
    else:
        return "Neutral"


def _interpret_macd(result: dict) -> str:
    """Interpret MACD values."""
    if not result["histogram"]:
        return "Insufficient data"
    hist = result["histogram"][-1]
    prev_hist = result["histogram"][-2] if len(result["histogram"]) > 1 else 0

    if hist > 0 and hist > prev_hist:
        return "Bullish - MACD above signal and strengthening"
    elif hist > 0:
        return "Bullish but momentum weakening"
    elif hist < 0 and hist < prev_hist:
        return "Bearish - MACD below signal and weakening"
    else:
        return "Bearish but momentum may be turning"


def _interpret_volatility(vol: float) -> str:
    """Interpret volatility value."""
    if vol < 0.15:
        return "Low volatility"
    elif vol < 0.25:
        return "Moderate volatility"
    elif vol < 0.40:
        return "High volatility"
    else:
        return "Very high volatility"


def _interpret_sharpe(sharpe: float) -> str:
    """Interpret Sharpe ratio."""
    if sharpe < 0:
        return "Poor - negative risk-adjusted returns"
    elif sharpe < 0.5:
        return "Below average risk-adjusted returns"
    elif sharpe < 1.0:
        return "Acceptable risk-adjusted returns"
    elif sharpe < 2.0:
        return "Good risk-adjusted returns"
    else:
        return "Excellent risk-adjusted returns"


async def main():
    """Run the MCP server."""
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
