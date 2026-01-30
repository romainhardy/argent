"""Fundamental analysis agent for company financials evaluation using computational methods."""

from dataclasses import dataclass, field
from typing import Any, Optional

from argent.agents.base import AgentResult, FinancialAgentType
from argent.tools.market_data import MarketDataClient


# Sector average benchmarks for comparison
SECTOR_BENCHMARKS = {
    "Technology": {"pe_ratio": 25, "profit_margin": 0.15, "roe": 0.18, "debt_to_equity": 0.5},
    "Healthcare": {"pe_ratio": 20, "profit_margin": 0.12, "roe": 0.15, "debt_to_equity": 0.6},
    "Financial Services": {"pe_ratio": 12, "profit_margin": 0.20, "roe": 0.12, "debt_to_equity": 2.0},
    "Consumer Cyclical": {"pe_ratio": 18, "profit_margin": 0.08, "roe": 0.15, "debt_to_equity": 0.8},
    "Communication Services": {"pe_ratio": 20, "profit_margin": 0.12, "roe": 0.10, "debt_to_equity": 0.7},
    "Industrials": {"pe_ratio": 18, "profit_margin": 0.08, "roe": 0.12, "debt_to_equity": 0.9},
    "Consumer Defensive": {"pe_ratio": 20, "profit_margin": 0.06, "roe": 0.15, "debt_to_equity": 0.7},
    "Energy": {"pe_ratio": 10, "profit_margin": 0.08, "roe": 0.10, "debt_to_equity": 0.5},
    "Utilities": {"pe_ratio": 15, "profit_margin": 0.10, "roe": 0.08, "debt_to_equity": 1.2},
    "Real Estate": {"pe_ratio": 30, "profit_margin": 0.25, "roe": 0.05, "debt_to_equity": 1.0},
    "Basic Materials": {"pe_ratio": 12, "profit_margin": 0.08, "roe": 0.10, "debt_to_equity": 0.6},
}

DEFAULT_BENCHMARK = {"pe_ratio": 18, "profit_margin": 0.10, "roe": 0.12, "debt_to_equity": 0.8}


@dataclass
class FundamentalAnalysisAgent:
    """Agent responsible for fundamental analysis using computational methods."""

    market_client: MarketDataClient = field(default_factory=MarketDataClient)

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.FUNDAMENTAL_ANALYSIS

    def _assess_valuation(
        self, info: Any, sector_avg: dict[str, float]
    ) -> dict[str, Any]:
        """Assess company valuation metrics."""
        pe_ratio = info.pe_ratio
        forward_pe = info.forward_pe
        peg_ratio = info.peg_ratio
        price_to_book = info.price_to_book

        score = 0
        assessment_reasons = []

        # P/E ratio assessment
        if pe_ratio is not None:
            pe_vs_sector = (pe_ratio / sector_avg["pe_ratio"]) if sector_avg["pe_ratio"] else 1
            if pe_vs_sector < 0.8:
                score += 2
                assessment_reasons.append("Trading at discount to sector")
            elif pe_vs_sector < 1.2:
                score += 1
                assessment_reasons.append("P/E in line with sector")
            else:
                score -= 1
                assessment_reasons.append("Premium valuation vs sector")

        # PEG ratio assessment (growth-adjusted)
        if peg_ratio is not None:
            if peg_ratio < 1:
                score += 2
                assessment_reasons.append("Attractive PEG ratio")
            elif peg_ratio < 2:
                score += 1
            else:
                score -= 1
                assessment_reasons.append("High PEG suggests overvaluation")

        # Forward P/E vs trailing (growth expectations)
        if forward_pe and pe_ratio:
            if forward_pe < pe_ratio * 0.85:
                score += 1
                assessment_reasons.append("Earnings expected to grow")
            elif forward_pe > pe_ratio * 1.15:
                score -= 1
                assessment_reasons.append("Earnings expected to decline")

        # Determine overall assessment
        if score >= 3:
            assessment = "undervalued"
        elif score >= 1:
            assessment = "fair"
        else:
            assessment = "overvalued"

        return {
            "pe_ratio": pe_ratio,
            "forward_pe": forward_pe,
            "peg_ratio": peg_ratio,
            "price_to_book": price_to_book,
            "assessment": assessment,
            "score": min(max(score / 3, -1), 1),  # Normalize to -1 to 1
            "reasons": assessment_reasons,
        }

    def _assess_profitability(
        self, info: Any, sector_avg: dict[str, float]
    ) -> dict[str, Any]:
        """Assess company profitability metrics."""
        profit_margin = info.profit_margin
        operating_margin = info.operating_margin
        roe = info.roe

        score = 0
        assessment_reasons = []

        # Profit margin assessment
        if profit_margin is not None:
            if profit_margin > sector_avg["profit_margin"] * 1.3:
                score += 2
                assessment_reasons.append("Strong profit margins")
            elif profit_margin > sector_avg["profit_margin"] * 0.8:
                score += 1
                assessment_reasons.append("Adequate profit margins")
            else:
                score -= 1
                assessment_reasons.append("Below-average profit margins")

        # ROE assessment
        if roe is not None:
            if roe > 0.20:
                score += 2
                assessment_reasons.append("Excellent return on equity")
            elif roe > 0.10:
                score += 1
            elif roe > 0:
                pass
            else:
                score -= 2
                assessment_reasons.append("Negative ROE is concerning")

        # Determine overall assessment
        if score >= 3:
            assessment = "excellent"
        elif score >= 2:
            assessment = "good"
        elif score >= 0:
            assessment = "average"
        else:
            assessment = "poor"

        return {
            "profit_margin": profit_margin,
            "operating_margin": operating_margin,
            "roe": roe,
            "assessment": assessment,
            "score": min(max(score / 3, -1), 1),
            "reasons": assessment_reasons,
        }

    def _assess_growth(self, info: Any) -> dict[str, Any]:
        """Assess company growth metrics."""
        revenue_growth = info.revenue_growth
        earnings_growth = info.earnings_growth

        score = 0
        assessment_reasons = []

        # Revenue growth assessment
        if revenue_growth is not None:
            if revenue_growth > 0.20:
                score += 2
                assessment_reasons.append("Strong revenue growth")
            elif revenue_growth > 0.10:
                score += 1
                assessment_reasons.append("Moderate revenue growth")
            elif revenue_growth > 0:
                pass
            else:
                score -= 1
                assessment_reasons.append("Revenue declining")

        # Earnings growth assessment
        if earnings_growth is not None:
            if earnings_growth > 0.25:
                score += 2
                assessment_reasons.append("Strong earnings growth")
            elif earnings_growth > 0.10:
                score += 1
            elif earnings_growth > 0:
                pass
            else:
                score -= 1
                assessment_reasons.append("Earnings declining")

        # Determine overall assessment
        if score >= 3:
            assessment = "high"
        elif score >= 1:
            assessment = "moderate"
        elif score >= 0:
            assessment = "low"
        else:
            assessment = "negative"

        return {
            "revenue_growth": revenue_growth,
            "earnings_growth": earnings_growth,
            "assessment": assessment,
            "score": min(max(score / 3, -1), 1),
            "reasons": assessment_reasons,
        }

    def _assess_financial_health(
        self, info: Any, sector_avg: dict[str, float]
    ) -> dict[str, Any]:
        """Assess company financial health metrics."""
        debt_to_equity = info.debt_to_equity
        current_ratio = info.current_ratio

        score = 0
        assessment_reasons = []

        # Debt-to-equity assessment
        if debt_to_equity is not None:
            if debt_to_equity < sector_avg["debt_to_equity"] * 0.5:
                score += 2
                assessment_reasons.append("Low debt levels")
            elif debt_to_equity < sector_avg["debt_to_equity"] * 1.5:
                score += 1
                assessment_reasons.append("Manageable debt")
            else:
                score -= 1
                assessment_reasons.append("High debt levels")

        # Current ratio assessment (liquidity)
        if current_ratio is not None:
            if current_ratio > 2:
                score += 2
                assessment_reasons.append("Strong liquidity position")
            elif current_ratio > 1:
                score += 1
                assessment_reasons.append("Adequate liquidity")
            else:
                score -= 2
                assessment_reasons.append("Liquidity concerns")

        # Determine overall assessment
        if score >= 3:
            assessment = "strong"
        elif score >= 1:
            assessment = "adequate"
        else:
            assessment = "weak"

        return {
            "debt_to_equity": debt_to_equity,
            "current_ratio": current_ratio,
            "assessment": assessment,
            "score": min(max(score / 3, -1), 1),
            "reasons": assessment_reasons,
        }

    def _get_analyst_sentiment(self, symbol: str) -> dict[str, Any]:
        """Get analyst recommendations and summarize."""
        try:
            recs = self.market_client.get_recommendations(symbol)
            if not recs:
                return {"consensus": "unknown", "buy_pct": None, "count": 0}

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
                return {"consensus": "unknown", "buy_pct": None, "count": 0}

            if grades["buy"] > grades["hold"] + grades["sell"]:
                consensus = "buy"
            elif grades["sell"] > grades["buy"] + grades["hold"]:
                consensus = "sell"
            else:
                consensus = "hold"

            return {
                "consensus": consensus,
                "buy_pct": grades["buy"] / total * 100,
                "count": total,
            }
        except Exception:
            return {"consensus": "unknown", "buy_pct": None, "count": 0}

    def _identify_strengths_concerns(
        self,
        valuation: dict[str, Any],
        profitability: dict[str, Any],
        growth: dict[str, Any],
        health: dict[str, Any],
    ) -> tuple[list[str], list[str]]:
        """Identify key strengths and concerns."""
        strengths = []
        concerns = []

        # Collect from each assessment
        for data in [valuation, profitability, growth, health]:
            for reason in data.get("reasons", []):
                if any(word in reason.lower() for word in ["strong", "excellent", "attractive", "low debt", "discount"]):
                    strengths.append(reason)
                elif any(word in reason.lower() for word in ["weak", "poor", "concern", "high", "declining", "negative"]):
                    concerns.append(reason)

        # Limit to top items
        return strengths[:5], concerns[:5]

    def _calculate_overall_score(
        self,
        valuation: dict[str, Any],
        profitability: dict[str, Any],
        growth: dict[str, Any],
        health: dict[str, Any],
        sentiment: dict[str, Any],
    ) -> float:
        """Calculate overall fundamental score."""
        weights = {
            "valuation": 0.25,
            "profitability": 0.25,
            "growth": 0.25,
            "health": 0.15,
            "sentiment": 0.10,
        }

        score = 0
        score += valuation.get("score", 0) * weights["valuation"]
        score += profitability.get("score", 0) * weights["profitability"]
        score += growth.get("score", 0) * weights["growth"]
        score += health.get("score", 0) * weights["health"]

        # Sentiment score
        if sentiment.get("consensus") == "buy":
            score += 1 * weights["sentiment"]
        elif sentiment.get("consensus") == "sell":
            score -= 1 * weights["sentiment"]

        return score

    def _generate_fair_value_assessment(
        self, overall_score: float, valuation: dict[str, Any]
    ) -> str:
        """Generate fair value assessment text."""
        if overall_score > 0.5:
            base = "Fundamentals are strong. "
        elif overall_score > 0:
            base = "Fundamentals are adequate. "
        else:
            base = "Fundamentals show weakness. "

        val_assessment = valuation.get("assessment", "fair")
        if val_assessment == "undervalued":
            return base + "Current valuation appears attractive relative to fundamentals."
        elif val_assessment == "overvalued":
            return base + "Current valuation appears stretched relative to fundamentals."
        else:
            return base + "Current valuation appears fair relative to fundamentals."

    def _is_crypto(self, symbol: str) -> bool:
        """Check if a symbol is a cryptocurrency."""
        crypto_symbols = {
            "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT",
            "MATIC", "LINK", "AVAX", "UNI", "ATOM", "LTC", "FIL",
        }
        return symbol.upper() in crypto_symbols

    def analyze(
        self,
        company_data: dict[str, Any],
        symbols: list[str],
    ) -> AgentResult:
        """
        Perform fundamental analysis using computational methods.

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
                error=None,
            )

        results = {"symbols": {}}

        for symbol in stock_symbols:
            try:
                # Get company info
                info = self.market_client.get_company_info(symbol)

                # Get sector benchmark
                sector = info.sector or "Unknown"
                sector_avg = SECTOR_BENCHMARKS.get(sector, DEFAULT_BENCHMARK)

                # Assess each dimension
                valuation = self._assess_valuation(info, sector_avg)
                profitability = self._assess_profitability(info, sector_avg)
                growth = self._assess_growth(info)
                health = self._assess_financial_health(info, sector_avg)
                sentiment = self._get_analyst_sentiment(symbol)

                # Calculate overall score
                overall_score = self._calculate_overall_score(
                    valuation, profitability, growth, health, sentiment
                )

                # Identify strengths and concerns
                strengths, concerns = self._identify_strengths_concerns(
                    valuation, profitability, growth, health
                )

                # Generate fair value assessment
                fair_value = self._generate_fair_value_assessment(overall_score, valuation)

                results["symbols"][symbol] = {
                    "name": info.name,
                    "sector": sector,
                    "industry": info.industry,
                    "valuation": valuation,
                    "profitability": profitability,
                    "growth": growth,
                    "financial_health": health,
                    "analyst_sentiment": sentiment,
                    "overall_score": overall_score,
                    "key_strengths": strengths,
                    "key_concerns": concerns,
                    "fair_value_assessment": fair_value,
                }

            except Exception as e:
                results["symbols"][symbol] = {
                    "error": f"Failed to analyze {symbol}: {str(e)}",
                    "overall_score": 0,
                }

        # Generate summary
        analyzed = [s for s, d in results["symbols"].items() if "error" not in d]
        if analyzed:
            avg_score = sum(results["symbols"][s]["overall_score"] for s in analyzed) / len(analyzed)
            if avg_score > 0.3:
                outlook = "positive"
            elif avg_score > -0.3:
                outlook = "neutral"
            else:
                outlook = "negative"
            results["summary"] = f"Fundamental analysis complete. Overall outlook: {outlook}. Analyzed {len(analyzed)} stocks."
        else:
            results["summary"] = "No stocks successfully analyzed."

        return AgentResult(
            success=True,
            data=results,
            error=None,
        )
