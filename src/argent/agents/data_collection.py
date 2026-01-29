"""Data collection agent for gathering market and economic data."""

from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic

from argent.agents.base import AgentResult, BaseAgent, FinancialAgentType, ToolDefinition
from argent.prompts.data_collection import DATA_COLLECTION_SYSTEM_PROMPT
from argent.tools.crypto_data import CryptoDataClient
from argent.tools.economic_data import EconomicDataClient
from argent.tools.market_data import MarketDataClient
from argent.tools.news import NewsClient


@dataclass
class DataCollectionAgent(BaseAgent):
    """Agent responsible for collecting market and economic data."""

    client: Anthropic
    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 15

    # Data clients
    market_client: MarketDataClient = field(default_factory=MarketDataClient)
    crypto_client: CryptoDataClient = field(default_factory=CryptoDataClient)
    economic_client: EconomicDataClient | None = None
    news_client: NewsClient = field(default_factory=NewsClient)

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.DATA_COLLECTION

    @property
    def system_prompt(self) -> str:
        return DATA_COLLECTION_SYSTEM_PROMPT

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="get_stock_prices",
                description="Fetch historical price data for a stock or ETF",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock/ETF ticker symbol (e.g., AAPL, SPY)",
                        },
                        "period": {
                            "type": "string",
                            "description": "Data period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max",
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
            ToolDefinition(
                name="get_current_price",
                description="Get current price and basic market data for a stock/ETF",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock/ETF ticker symbol",
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="get_company_info",
                description="Get detailed company fundamental information",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol",
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="get_crypto_prices",
                description="Fetch cryptocurrency price data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of crypto symbols (e.g., BTC, ETH)",
                        },
                    },
                    "required": ["symbols"],
                },
            ),
            ToolDefinition(
                name="get_crypto_history",
                description="Fetch historical crypto price data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Crypto symbol (e.g., BTC)",
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days of history",
                            "default": 365,
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="get_economic_indicators",
                description="Fetch economic indicators from FRED",
                input_schema={
                    "type": "object",
                    "properties": {
                        "series_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "FRED series IDs (e.g., GDP, UNRATE, FEDFUNDS, DGS10, CPIAUCSL)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of data points per series",
                            "default": 50,
                        },
                    },
                    "required": ["series_ids"],
                },
            ),
            ToolDefinition(
                name="get_macro_snapshot",
                description="Get a snapshot of key macroeconomic indicators",
                input_schema={
                    "type": "object",
                    "properties": {},
                },
            ),
            ToolDefinition(
                name="get_news",
                description="Fetch news articles for symbols",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Symbols to get news for",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max articles per symbol",
                            "default": 5,
                        },
                    },
                    "required": ["symbols"],
                },
            ),
            ToolDefinition(
                name="get_global_crypto_data",
                description="Get global cryptocurrency market data",
                input_schema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    def execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        if tool_name == "get_stock_prices":
            prices = self.market_client.get_price_history(
                symbol=tool_input["symbol"],
                period=tool_input.get("period", "1y"),
                interval=tool_input.get("interval", "1d"),
            )
            return [
                {
                    "timestamp": p.timestamp.isoformat(),
                    "open": p.open,
                    "high": p.high,
                    "low": p.low,
                    "close": p.close,
                    "volume": p.volume,
                }
                for p in prices
            ]

        elif tool_name == "get_current_price":
            return self.market_client.get_current_price(tool_input["symbol"])

        elif tool_name == "get_company_info":
            info = self.market_client.get_company_info(tool_input["symbol"])
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
                "current_ratio": info.current_ratio,
                "revenue_growth": info.revenue_growth,
                "earnings_growth": info.earnings_growth,
                "beta": info.beta,
                "fifty_two_week_high": info.fifty_two_week_high,
                "fifty_two_week_low": info.fifty_two_week_low,
            }

        elif tool_name == "get_crypto_prices":
            return self.crypto_client.get_current_price(tool_input["symbols"])

        elif tool_name == "get_crypto_history":
            return self.crypto_client.get_price_history(
                symbol=tool_input["symbol"],
                days=tool_input.get("days", 365),
            )

        elif tool_name == "get_economic_indicators":
            if not self.economic_client:
                return {"error": "FRED API key not configured"}

            results = {}
            for series_id in tool_input["series_ids"]:
                data = self.economic_client.get_series(
                    series_id=series_id,
                    limit=tool_input.get("limit", 50),
                )
                results[series_id] = [
                    {
                        "date": d.date.isoformat(),
                        "value": d.value,
                        "name": d.name,
                    }
                    for d in data
                ]
            return results

        elif tool_name == "get_macro_snapshot":
            if not self.economic_client:
                return {"error": "FRED API key not configured"}
            return self.economic_client.get_macro_snapshot()

        elif tool_name == "get_news":
            return self.news_client.get_news_summary(tool_input["symbols"])

        elif tool_name == "get_global_crypto_data":
            return self.crypto_client.get_global_market_data()

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def collect_data(
        self,
        symbols: list[str],
        time_horizon: str = "medium",
        include_crypto: bool = True,
        include_economic: bool = True,
    ) -> AgentResult:
        """
        Collect all relevant data for analysis.

        Args:
            symbols: List of symbols to analyze
            time_horizon: short (1-4 weeks), medium (1-6 months), long (6+ months)
            include_crypto: Whether to include crypto data
            include_economic: Whether to include economic indicators

        Returns:
            AgentResult with collected data
        """
        # Categorize symbols
        stock_symbols = [s for s in symbols if not self._is_crypto(s)]
        crypto_symbols = [s for s in symbols if self._is_crypto(s)]

        task = f"""Collect comprehensive market data for analysis.

Symbols to analyze:
- Stocks/ETFs: {stock_symbols if stock_symbols else 'None'}
- Cryptocurrencies: {crypto_symbols if crypto_symbols else 'None'}

Time horizon: {time_horizon}
Include economic indicators: {include_economic}

Instructions:
1. For each stock/ETF symbol:
   - Get historical prices (period based on time horizon)
   - Get current price and market data
   - Get company fundamental info

2. For each crypto symbol:
   - Get current prices
   - Get historical prices

3. If economic indicators are requested:
   - Get macro snapshot with key indicators
   - Focus on: interest rates, inflation, employment, market sentiment

4. Get recent news for all symbols

Return a structured summary of all collected data with key statistics."""

        return self.run(task)

    def _is_crypto(self, symbol: str) -> bool:
        """Check if a symbol is a cryptocurrency."""
        crypto_symbols = {
            "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT",
            "MATIC", "LINK", "AVAX", "UNI", "ATOM", "LTC", "FIL",
        }
        return symbol.upper() in crypto_symbols
