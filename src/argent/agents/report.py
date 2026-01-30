"""Report generation agent for final synthesis using template-based methods."""

from dataclasses import dataclass
from typing import Any

from argent.agents.base import AgentResult, FinancialAgentType


@dataclass
class ReportAgent:
    """Agent responsible for generating the final investment report using templates."""

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.REPORT

    def _determine_market_outlook(self, analysis_results: dict[str, Any]) -> str:
        """Determine overall market outlook from analysis results."""
        signals = []

        # Technical signals
        tech = analysis_results.get("technical_analysis", {})
        if tech:
            for symbol, data in tech.get("symbols", {}).items():
                if isinstance(data, dict):
                    outlook = data.get("signals", {}).get("overall", "neutral")
                    signals.append(1 if outlook == "bullish" else -1 if outlook == "bearish" else 0)

        # Sentiment signals
        sentiment = analysis_results.get("sentiment_analysis", {})
        if sentiment:
            for symbol, data in sentiment.get("symbols", {}).items():
                if isinstance(data, dict):
                    outlook = data.get("overall", "neutral")
                    signals.append(1 if outlook == "bullish" else -1 if outlook == "bearish" else 0)

        # Macro signals
        macro = analysis_results.get("macro_analysis", {})
        if macro:
            asset_impl = macro.get("asset_implications", {})
            stock_outlook = asset_impl.get("stocks", {}).get("outlook", "neutral")
            signals.append(1 if stock_outlook == "favorable" else -1 if stock_outlook == "unfavorable" else 0)

        if not signals:
            return "neutral"

        avg = sum(signals) / len(signals)
        if avg > 0.3:
            return "bullish"
        elif avg < -0.3:
            return "bearish"
        return "neutral"

    def _generate_key_findings(self, analysis_results: dict[str, Any], symbols: list[str]) -> str:
        """Generate key findings summary."""
        findings = []

        # Technical summary
        tech = analysis_results.get("technical_analysis", {})
        if tech.get("summary"):
            findings.append(tech["summary"])

        # Risk summary
        risk = analysis_results.get("risk_analysis", {})
        if risk.get("summary"):
            findings.append(risk["summary"])

        # Sentiment summary
        sentiment = analysis_results.get("sentiment_analysis", {})
        if sentiment.get("summary"):
            findings.append(sentiment["summary"])

        if findings:
            return " ".join(findings[:3])
        return f"Analysis completed for {', '.join(symbols)}."

    def _get_top_recommendation(self, analysis_results: dict[str, Any], symbols: list[str]) -> dict[str, Any]:
        """Identify the top recommendation from analysis."""
        best_symbol = None
        best_score = -float('inf')

        # Score based on technical signals
        tech = analysis_results.get("technical_analysis", {})
        for symbol in symbols:
            score = 0
            if symbol in tech.get("symbols", {}):
                signals = tech["symbols"][symbol].get("signals", {})
                if signals.get("overall") == "bullish":
                    score += 2
                elif signals.get("overall") == "bearish":
                    score -= 2

            # Add fundamental score if available
            fund = analysis_results.get("fundamental_analysis", {})
            if symbol in fund.get("symbols", {}):
                fund_score = fund["symbols"][symbol].get("overall_score", 0)
                score += fund_score * 2

            # Add sentiment
            sent = analysis_results.get("sentiment_analysis", {})
            if symbol in sent.get("symbols", {}):
                sent_overall = sent["symbols"][symbol].get("overall", "neutral")
                if sent_overall == "bullish":
                    score += 1
                elif sent_overall == "bearish":
                    score -= 1

            if score > best_score:
                best_score = score
                best_symbol = symbol

        if best_symbol and best_score > 0:
            action = "BUY" if best_score > 1 else "WATCH"
            return {
                "symbol": best_symbol,
                "action": action,
                "rationale": f"Best overall score based on technical, fundamental, and sentiment analysis.",
            }

        return {
            "symbol": symbols[0] if symbols else "N/A",
            "action": "HOLD",
            "rationale": "No clear directional signals identified.",
        }

    def _generate_macro_summary(self, analysis_results: dict[str, Any]) -> str:
        """Generate macro environment summary."""
        macro = analysis_results.get("macro_analysis", {})
        if macro.get("summary"):
            return macro["summary"]

        cycle = macro.get("economic_cycle", {})
        if cycle.get("phase"):
            return f"Economy in {cycle['phase']} phase."

        return "Macro conditions require monitoring."

    def _build_asset_analysis(self, analysis_results: dict[str, Any], symbols: list[str]) -> dict[str, Any]:
        """Build asset-level analysis summary."""
        asset_analysis = {}

        tech = analysis_results.get("technical_analysis", {})
        fund = analysis_results.get("fundamental_analysis", {})
        risk = analysis_results.get("risk_analysis", {})
        sent = analysis_results.get("sentiment_analysis", {})

        for symbol in symbols:
            asset = {
                "current_price": None,
                "trend": "unknown",
                "technical_outlook": "N/A",
                "fundamental_assessment": "N/A",
                "risk_level": "moderate",
                "sentiment": "neutral",
                "key_levels": {"support": None, "resistance": None},
            }

            # Technical data
            if symbol in tech.get("symbols", {}):
                t = tech["symbols"][symbol]
                asset["current_price"] = t.get("current_price")
                asset["trend"] = t.get("trend", {}).get("direction", "unknown")
                signals = t.get("signals", {})
                asset["technical_outlook"] = f"{signals.get('overall', 'neutral')} ({signals.get('confidence', 'low')} confidence)"
                levels = t.get("levels", {})
                asset["key_levels"] = {
                    "support": levels.get("nearest_support"),
                    "resistance": levels.get("nearest_resistance"),
                }

            # Fundamental data
            if symbol in fund.get("symbols", {}):
                f = fund["symbols"][symbol]
                asset["fundamental_assessment"] = f.get("fair_value_assessment", "N/A")

            # Risk data
            if symbol in risk.get("symbols", {}):
                r = risk["symbols"][symbol]
                asset["risk_level"] = r.get("overall_risk", {}).get("level", "moderate")

            # Sentiment data
            if symbol in sent.get("symbols", {}):
                s = sent["symbols"][symbol]
                asset["sentiment"] = s.get("overall", "neutral")

            asset_analysis[symbol] = asset

        return asset_analysis

    def _generate_recommendations(
        self,
        analysis_results: dict[str, Any],
        symbols: list[str],
        time_horizon: str,
    ) -> list[dict[str, Any]]:
        """Generate recommendations for each symbol."""
        recommendations = []

        tech = analysis_results.get("technical_analysis", {})
        fund = analysis_results.get("fundamental_analysis", {})
        risk = analysis_results.get("risk_analysis", {})
        sent = analysis_results.get("sentiment_analysis", {})

        for symbol in symbols:
            rec = {
                "symbol": symbol,
                "action": "HOLD",
                "conviction": "LOW",
                "target_price": None,
                "stop_loss": None,
                "position_size_pct": 5,
                "rationale": "",
                "time_horizon": time_horizon,
                "risks": [],
                "catalysts": [],
            }

            score = 0
            rationale_parts = []
            risks = []

            # Technical score
            if symbol in tech.get("symbols", {}):
                t = tech["symbols"][symbol]
                signals = t.get("signals", {})
                if signals.get("overall") == "bullish":
                    score += 2
                    rationale_parts.append("Technical indicators bullish")
                elif signals.get("overall") == "bearish":
                    score -= 2
                    rationale_parts.append("Technical indicators bearish")

                # Set price targets from support/resistance
                levels = t.get("levels", {})
                if levels.get("nearest_resistance"):
                    rec["target_price"] = levels["nearest_resistance"]
                if levels.get("nearest_support"):
                    rec["stop_loss"] = levels["nearest_support"]

            # Fundamental score
            if symbol in fund.get("symbols", {}):
                f = fund["symbols"][symbol]
                fund_score = f.get("overall_score", 0)
                if fund_score > 0.3:
                    score += 2
                    rationale_parts.append("Strong fundamentals")
                elif fund_score < -0.3:
                    score -= 2
                    rationale_parts.append("Weak fundamentals")

                # Add concerns as risks
                risks.extend(f.get("key_concerns", [])[:2])

            # Sentiment score
            if symbol in sent.get("symbols", {}):
                s = sent["symbols"][symbol]
                if s.get("overall") == "bullish":
                    score += 1
                    rationale_parts.append("Positive sentiment")
                elif s.get("overall") == "bearish":
                    score -= 1
                    rationale_parts.append("Negative sentiment")

            # Risk assessment
            if symbol in risk.get("symbols", {}):
                r = risk["symbols"][symbol]
                risk_level = r.get("overall_risk", {}).get("level", "moderate")
                if risk_level == "high":
                    score -= 1
                    risks.append("High overall risk level")
                elif risk_level == "low":
                    score += 1

                # Adjust position size based on risk
                if risk_level == "high":
                    rec["position_size_pct"] = 2
                elif risk_level == "low":
                    rec["position_size_pct"] = 8

            # Determine action and conviction
            if score >= 3:
                rec["action"] = "BUY"
                rec["conviction"] = "HIGH"
            elif score >= 1:
                rec["action"] = "BUY"
                rec["conviction"] = "MEDIUM"
            elif score <= -3:
                rec["action"] = "SELL"
                rec["conviction"] = "HIGH"
            elif score <= -1:
                rec["action"] = "SELL"
                rec["conviction"] = "MEDIUM"
            else:
                rec["action"] = "HOLD"
                rec["conviction"] = "LOW"

            rec["rationale"] = ". ".join(rationale_parts) if rationale_parts else "Mixed signals"
            rec["risks"] = risks if risks else ["Market volatility"]

            recommendations.append(rec)

        return recommendations

    def _assess_portfolio(self, analysis_results: dict[str, Any], symbols: list[str]) -> dict[str, Any]:
        """Assess portfolio-level considerations."""
        risk = analysis_results.get("risk_analysis", {})

        # Get diversification assessment
        diversification = risk.get("diversification", "Unable to assess")

        # Calculate average risk score
        risk_scores = []
        for symbol in symbols:
            if symbol in risk.get("symbols", {}):
                r = risk["symbols"][symbol]
                level = r.get("overall_risk", {}).get("level", "moderate")
                risk_scores.append({"low": 1, "moderate": 2, "high": 3}.get(level, 2))

        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 2
        if avg_risk > 2.3:
            risk_allocation = "Portfolio risk is elevated. Consider reducing exposure."
        elif avg_risk < 1.7:
            risk_allocation = "Portfolio risk is low. May have room for higher-risk opportunities."
        else:
            risk_allocation = "Portfolio risk is balanced."

        suggestions = []
        if len(symbols) < 3:
            suggestions.append("Consider adding more positions for diversification")
        if "high" in [risk.get("symbols", {}).get(s, {}).get("overall_risk", {}).get("level") for s in symbols]:
            suggestions.append("Review high-risk positions for potential reduction")

        return {
            "diversification_score": 0.5 if "Well" in diversification else 0.3 if "Moderately" in diversification else 0.2,
            "risk_allocation": risk_allocation,
            "rebalancing_suggestions": suggestions if suggestions else ["Portfolio appears balanced"],
        }

    def _identify_risks(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Identify key risks and scenarios."""
        risks = []

        # Macro risks
        macro = analysis_results.get("macro_analysis", {})
        risks.extend(macro.get("key_risks", [])[:3])

        # Technical risks
        tech = analysis_results.get("technical_analysis", {})
        for symbol, data in tech.get("symbols", {}).items():
            if isinstance(data, dict):
                if data.get("signals", {}).get("overall") == "bearish":
                    risks.append(f"{symbol} showing bearish technical signals")

        scenarios = [
            {
                "scenario": "Market correction",
                "probability": "medium",
                "impact": "Position values could decline 10-20%",
            },
            {
                "scenario": "Interest rate changes",
                "probability": "medium",
                "impact": "Sector rotation may affect holdings",
            },
        ]

        hedging = ["Consider stop-loss orders on positions", "Monitor key support levels"]

        return {
            "key_risks": risks[:5] if risks else ["General market volatility"],
            "scenarios": scenarios,
            "hedging_ideas": hedging,
        }

    def _generate_conclusion(self, recommendations: list[dict[str, Any]], time_horizon: str) -> dict[str, Any]:
        """Generate conclusion with action items."""
        action_items = []

        buy_recs = [r for r in recommendations if r["action"] == "BUY"]
        sell_recs = [r for r in recommendations if r["action"] == "SELL"]

        if buy_recs:
            high_conviction = [r for r in buy_recs if r["conviction"] == "HIGH"]
            if high_conviction:
                action_items.append(f"Consider buying {', '.join(r['symbol'] for r in high_conviction)} (high conviction)")
            else:
                action_items.append(f"Review buy candidates: {', '.join(r['symbol'] for r in buy_recs[:3])}")

        if sell_recs:
            action_items.append(f"Consider reducing exposure to {', '.join(r['symbol'] for r in sell_recs[:3])}")

        action_items.append("Review stop-loss levels on all positions")
        action_items.append("Monitor key technical support levels")

        # Review timeline based on time horizon
        if time_horizon == "short":
            next_review = "1-2 weeks"
        elif time_horizon == "medium":
            next_review = "1 month"
        else:
            next_review = "3 months"

        return {
            "action_items": action_items[:5],
            "key_dates": ["Monitor earnings announcements", "Watch Fed meeting dates"],
            "next_review": next_review,
        }

    def generate_report(
        self,
        analysis_results: dict[str, Any],
        symbols: list[str],
        time_horizon: str = "medium",
        request: str = "",
    ) -> AgentResult:
        """
        Generate the final investment report using template-based synthesis.

        Args:
            analysis_results: Dict containing all analysis results
            symbols: List of symbols analyzed
            time_horizon: Investment time horizon
            request: Original analysis request

        Returns:
            AgentResult with the final report
        """
        # Build report sections
        market_outlook = self._determine_market_outlook(analysis_results)
        key_findings = self._generate_key_findings(analysis_results, symbols)
        top_rec = self._get_top_recommendation(analysis_results, symbols)

        executive_summary = {
            "key_findings": key_findings,
            "market_outlook": market_outlook,
            "top_recommendation": top_rec,
        }

        macro_summary = self._generate_macro_summary(analysis_results)
        macro = analysis_results.get("macro_analysis", {})
        economic_factors = macro.get("key_risks", ["Economic cycle", "Interest rates", "Inflation"])[:4]

        market_environment = {
            "macro_summary": macro_summary,
            "economic_factors": economic_factors,
            "market_regime": macro.get("economic_cycle", {}).get("phase", "unknown"),
        }

        asset_analysis = self._build_asset_analysis(analysis_results, symbols)
        recommendations = self._generate_recommendations(analysis_results, symbols, time_horizon)
        portfolio_considerations = self._assess_portfolio(analysis_results, symbols)
        risk_warnings = self._identify_risks(analysis_results)
        conclusion = self._generate_conclusion(recommendations, time_horizon)

        disclaimer = (
            "This report is for informational purposes only and does not constitute investment advice. "
            "Past performance is not indicative of future results. Always conduct your own research "
            "and consult with a qualified financial advisor before making investment decisions."
        )

        report_data = {
            "executive_summary": executive_summary,
            "market_environment": market_environment,
            "asset_analysis": asset_analysis,
            "recommendations": recommendations,
            "portfolio_considerations": portfolio_considerations,
            "risk_warnings": risk_warnings,
            "conclusion": conclusion,
            "disclaimer": disclaimer,
        }

        return AgentResult(
            success=True,
            data=report_data,
            error=None,
        )

    def generate_text_report(self, report_data: dict[str, Any]) -> str:
        """Convert structured report data to formatted text."""
        lines = []

        lines.append("=" * 60)
        lines.append("INVESTMENT ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append("")

        # Executive Summary
        if "executive_summary" in report_data:
            exec_sum = report_data["executive_summary"]
            lines.append("## EXECUTIVE SUMMARY")
            lines.append("-" * 40)
            lines.append(exec_sum.get("key_findings", ""))
            lines.append(f"\nMarket Outlook: {exec_sum.get('market_outlook', 'N/A').upper()}")
            if "top_recommendation" in exec_sum:
                top = exec_sum["top_recommendation"]
                lines.append(f"\nTop Pick: {top.get('symbol', 'N/A')} - {top.get('action', 'N/A')}")
                lines.append(f"Rationale: {top.get('rationale', 'N/A')}")
            lines.append("")

        # Market Environment
        if "market_environment" in report_data:
            env = report_data["market_environment"]
            lines.append("## MARKET ENVIRONMENT")
            lines.append("-" * 40)
            lines.append(env.get("macro_summary", ""))
            lines.append(f"\nMarket Regime: {env.get('market_regime', 'N/A')}")
            if "economic_factors" in env:
                lines.append("\nKey Factors:")
                for factor in env["economic_factors"]:
                    lines.append(f"  - {factor}")
            lines.append("")

        # Recommendations
        if "recommendations" in report_data:
            lines.append("## RECOMMENDATIONS")
            lines.append("-" * 40)
            for rec in report_data["recommendations"]:
                lines.append(f"\n### {rec.get('symbol', 'N/A')}")
                lines.append(f"Action: {rec.get('action', 'N/A')} | Conviction: {rec.get('conviction', 'N/A')}")
                if rec.get("target_price"):
                    lines.append(f"Target: ${rec['target_price']:.2f} | Stop: ${rec.get('stop_loss', 0):.2f}")
                if rec.get("position_size_pct"):
                    lines.append(f"Position Size: {rec['position_size_pct']}% of portfolio")
                lines.append(f"\nRationale: {rec.get('rationale', 'N/A')}")
                if rec.get("risks"):
                    lines.append("\nRisks:")
                    for risk in rec["risks"]:
                        lines.append(f"  ! {risk}")
            lines.append("")

        # Risk Warnings
        if "risk_warnings" in report_data:
            warnings = report_data["risk_warnings"]
            lines.append("## RISK WARNINGS")
            lines.append("-" * 40)
            if "key_risks" in warnings:
                for risk in warnings["key_risks"]:
                    lines.append(f"  ! {risk}")
            lines.append("")

        # Conclusion
        if "conclusion" in report_data:
            conclusion = report_data["conclusion"]
            lines.append("## CONCLUSION")
            lines.append("-" * 40)
            if "action_items" in conclusion:
                lines.append("\nAction Items:")
                for i, item in enumerate(conclusion["action_items"], 1):
                    lines.append(f"  {i}. {item}")
            if conclusion.get("next_review"):
                lines.append(f"\nNext Review: {conclusion['next_review']}")
            lines.append("")

        # Disclaimer
        lines.append("=" * 60)
        disclaimer = report_data.get(
            "disclaimer",
            "This report is for informational purposes only and does not constitute investment advice."
        )
        lines.append(f"DISCLAIMER: {disclaimer}")
        lines.append("=" * 60)

        return "\n".join(lines)
