"""Fundamental analysis agent for company financials evaluation."""

from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic

from argent.agents.base import AgentResult, BaseAgent, FinancialAgentType, ToolDefinition
from argent.prompts.fundamental_analysis import FUNDAMENTAL_ANALYSIS_SYSTEM_PROMPT
from argent.tools.market_data import MarketDataClient


@dataclass
class FundamentalAnalysisAgent(BaseAgent):
    """Agent responsible for fundamental analysis."""

    client: Anthropic
    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 10
    market_client: MarketDataClient = field(default_factory=MarketDataClient)

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.FUNDAMENTAL_ANALYSIS

    @property
    def system_prompt(self) -> str:
        return FUNDAMENTAL_ANALYSIS_SYSTEM_PROMPT

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="get_financial_ratios",
                description="Get key financial ratios for a company",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="get_financial_statements",
                description="Get income statement, balance sheet, and cash flow data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="get_analyst_recommendations",
                description="Get analyst recommendations and ratings",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="compare_to_sector",
                description="Compare company metrics to sector averages",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"},
                    },
                    "required": ["symbol"],
                },
            ),
        ]

    def execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        symbol = tool_input.get("symbol", "")

        if tool_name == "get_financial_ratios":
            info = self.market_client.get_company_info(symbol)
            return {
                "symbol": info.symbol,
                "name": info.name,
                "sector": info.sector,
                "industry": info.industry,
                "valuation": {
                    "market_cap": info.market_cap,
                    "pe_ratio": info.pe_ratio,
                    "forward_pe": info.forward_pe,
                    "peg_ratio": info.peg_ratio,
                    "price_to_book": info.price_to_book,
                },
                "profitability": {
                    "profit_margin": info.profit_margin,
                    "operating_margin": info.operating_margin,
                    "roe": info.roe,
                },
                "growth": {
                    "revenue_growth": info.revenue_growth,
                    "earnings_growth": info.earnings_growth,
                },
                "financial_health": {
                    "debt_to_equity": info.debt_to_equity,
                    "current_ratio": info.current_ratio,
                },
                "dividends": {
                    "dividend_yield": info.dividend_yield,
                },
                "risk": {
                    "beta": info.beta,
                },
                "price_range": {
                    "fifty_two_week_high": info.fifty_two_week_high,
                    "fifty_two_week_low": info.fifty_two_week_low,
                },
            }

        elif tool_name == "get_financial_statements":
            return self.market_client.get_financials(symbol)

        elif tool_name == "get_analyst_recommendations":
            recs = self.market_client.get_recommendations(symbol)
            return {
                "symbol": symbol,
                "recent_recommendations": recs,
                "summary": self._summarize_recommendations(recs),
            }

        elif tool_name == "compare_to_sector":
            # Get company info
            info = self.market_client.get_company_info(symbol)

            # Define typical sector averages (simplified)
            sector_averages = {
                "Technology": {"pe_ratio": 25, "profit_margin": 0.15, "roe": 0.18},
                "Healthcare": {"pe_ratio": 20, "profit_margin": 0.12, "roe": 0.15},
                "Financial Services": {"pe_ratio": 12, "profit_margin": 0.20, "roe": 0.12},
                "Consumer Cyclical": {"pe_ratio": 18, "profit_margin": 0.08, "roe": 0.15},
                "Communication Services": {"pe_ratio": 20, "profit_margin": 0.12, "roe": 0.10},
                "Industrials": {"pe_ratio": 18, "profit_margin": 0.08, "roe": 0.12},
                "Consumer Defensive": {"pe_ratio": 20, "profit_margin": 0.06, "roe": 0.15},
                "Energy": {"pe_ratio": 10, "profit_margin": 0.08, "roe": 0.10},
                "Utilities": {"pe_ratio": 15, "profit_margin": 0.10, "roe": 0.08},
                "Real Estate": {"pe_ratio": 30, "profit_margin": 0.25, "roe": 0.05},
                "Basic Materials": {"pe_ratio": 12, "profit_margin": 0.08, "roe": 0.10},
            }

            sector = info.sector or "Unknown"
            avg = sector_averages.get(sector, {"pe_ratio": 18, "profit_margin": 0.10, "roe": 0.12})

            comparison = {
                "symbol": symbol,
                "sector": sector,
                "company_metrics": {
                    "pe_ratio": info.pe_ratio,
                    "profit_margin": info.profit_margin,
                    "roe": info.roe,
                },
                "sector_averages": avg,
                "comparison": {},
            }

            # Compare each metric
            if info.pe_ratio and avg["pe_ratio"]:
                pe_diff = (info.pe_ratio - avg["pe_ratio"]) / avg["pe_ratio"] * 100
                comparison["comparison"]["pe_ratio"] = {
                    "diff_pct": pe_diff,
                    "assessment": "expensive" if pe_diff > 20 else "cheap" if pe_diff < -20 else "fair",
                }

            if info.profit_margin and avg["profit_margin"]:
                margin_diff = (info.profit_margin - avg["profit_margin"]) / avg["profit_margin"] * 100
                comparison["comparison"]["profit_margin"] = {
                    "diff_pct": margin_diff,
                    "assessment": "above average" if margin_diff > 20 else "below average" if margin_diff < -20 else "average",
                }

            if info.roe and avg["roe"]:
                roe_diff = (info.roe - avg["roe"]) / avg["roe"] * 100
                comparison["comparison"]["roe"] = {
                    "diff_pct": roe_diff,
                    "assessment": "above average" if roe_diff > 20 else "below average" if roe_diff < -20 else "average",
                }

            return comparison

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _summarize_recommendations(self, recs: list[dict]) -> dict[str, Any]:
        """Summarize analyst recommendations."""
        if not recs:
            return {"count": 0, "consensus": "unknown"}

        grades = {"buy": 0, "hold": 0, "sell": 0}

        for rec in recs:
            grade = (rec.get("to_grade") or "").lower()
            if any(x in grade for x in ["buy", "outperform", "overweight"]):
                grades["buy"] += 1
            elif any(x in grade for x in ["sell", "underperform", "underweight"]):
                grades["sell"] += 1
            else:
                grades["hold"] += 1

        total = sum(grades.values())
        if total == 0:
            return {"count": 0, "consensus": "unknown"}

        # Determine consensus
        if grades["buy"] > grades["hold"] + grades["sell"]:
            consensus = "buy"
        elif grades["sell"] > grades["buy"] + grades["hold"]:
            consensus = "sell"
        else:
            consensus = "hold"

        return {
            "count": total,
            "buy": grades["buy"],
            "hold": grades["hold"],
            "sell": grades["sell"],
            "consensus": consensus,
            "buy_pct": grades["buy"] / total * 100,
        }

    def analyze(
        self,
        company_data: dict[str, Any],
        symbols: list[str],
    ) -> AgentResult:
        """
        Perform fundamental analysis on companies.

        Args:
            company_data: Previously collected company data
            symbols: List of stock symbols to analyze (excludes crypto)

        Returns:
            AgentResult with fundamental analysis
        """
        # Filter to only stock/ETF symbols
        stock_symbols = [s for s in symbols if not self._is_crypto(s)]

        if not stock_symbols:
            return AgentResult(
                success=True,
                data={"message": "No stocks to analyze for fundamentals", "symbols": {}},
            )

        task = f"""Perform comprehensive fundamental analysis on the following stocks: {stock_symbols}

For each stock, analyze:
1. Valuation Assessment
   - P/E ratio analysis (trailing and forward)
   - PEG ratio (growth-adjusted valuation)
   - Price-to-book value
   - Compare to historical and sector averages

2. Profitability Analysis
   - Profit margins (gross, operating, net)
   - Return on equity (ROE)
   - Return on assets (ROA)
   - Margin trends

3. Growth Prospects
   - Revenue growth rate
   - Earnings growth rate
   - Growth sustainability

4. Financial Health
   - Debt-to-equity ratio
   - Current ratio
   - Interest coverage
   - Cash position

5. Competitive Position
   - Market position in sector
   - Competitive advantages (moats)
   - Industry dynamics

6. Analyst Sentiment
   - Consensus recommendations
   - Recent rating changes

Return your analysis as structured JSON with the following schema:
{{
    "symbols": {{
        "<symbol>": {{
            "name": "string",
            "sector": "string",
            "valuation": {{
                "pe_ratio": number,
                "forward_pe": number,
                "peg_ratio": number,
                "price_to_book": number,
                "assessment": "undervalued|fair|overvalued",
                "score": number
            }},
            "profitability": {{
                "profit_margin": number,
                "operating_margin": number,
                "roe": number,
                "assessment": "excellent|good|average|poor",
                "score": number
            }},
            "growth": {{
                "revenue_growth": number,
                "earnings_growth": number,
                "assessment": "high|moderate|low|negative",
                "score": number
            }},
            "financial_health": {{
                "debt_to_equity": number,
                "current_ratio": number,
                "assessment": "strong|adequate|weak",
                "score": number
            }},
            "analyst_sentiment": {{
                "consensus": "buy|hold|sell",
                "buy_pct": number
            }},
            "overall_score": number,
            "key_strengths": ["string"],
            "key_concerns": ["string"],
            "fair_value_assessment": "string"
        }}
    }},
    "summary": "string"
}}"""

        return self.run(task, context={"company_data": company_data, "stock_symbols": stock_symbols})

    def _is_crypto(self, symbol: str) -> bool:
        """Check if a symbol is a cryptocurrency."""
        crypto_symbols = {
            "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT",
            "MATIC", "LINK", "AVAX", "UNI", "ATOM", "LTC", "FIL",
        }
        return symbol.upper() in crypto_symbols
