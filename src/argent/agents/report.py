"""Report generation agent for final synthesis."""

from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic

from argent.agents.base import AgentResult, BaseAgent, FinancialAgentType, ToolDefinition
from argent.prompts.report import REPORT_SYSTEM_PROMPT


@dataclass
class ReportAgent(BaseAgent):
    """Agent responsible for generating the final investment report."""

    client: Anthropic
    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 5

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.REPORT

    @property
    def system_prompt(self) -> str:
        return REPORT_SYSTEM_PROMPT

    def get_tools(self) -> list[ToolDefinition]:
        # Report generation is purely analytical - no tools needed
        return []

    def execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        raise ValueError(f"Unknown tool: {tool_name}")

    def generate_report(
        self,
        analysis_results: dict[str, Any],
        symbols: list[str],
        time_horizon: str = "medium",
        request: str = "",
    ) -> AgentResult:
        """
        Generate the final investment report.

        Args:
            analysis_results: Dict containing all analysis results
            symbols: List of symbols analyzed
            time_horizon: Investment time horizon
            request: Original analysis request

        Returns:
            AgentResult with the final report
        """
        task = f"""Generate a comprehensive investment report based on the analysis results provided.

Original Request: {request}
Symbols Analyzed: {symbols}
Time Horizon: {time_horizon}

Using the analysis data provided, create a professional investment report that includes:

1. Executive Summary
   - Key findings in 2-3 sentences
   - Overall market outlook
   - Top recommendation

2. Market Environment
   - Macro conditions summary
   - Key economic factors
   - Market regime assessment

3. Individual Asset Analysis
   For each symbol:
   - Current price and trend
   - Technical outlook
   - Fundamental assessment (for stocks)
   - Risk profile
   - Sentiment reading

4. Recommendations
   For each symbol provide:
   - Action: BUY / HOLD / SELL / WATCH
   - Conviction: HIGH / MEDIUM / LOW
   - Target price (if applicable)
   - Stop loss level
   - Position sizing suggestion (% of portfolio)
   - Key rationale
   - Primary risks

5. Portfolio Considerations
   - Diversification assessment
   - Risk allocation
   - Rebalancing suggestions

6. Risk Warnings
   - Key risks to monitor
   - Scenario analysis
   - Hedging considerations

7. Conclusion
   - Action items prioritized
   - Key dates/events to watch
   - Review timeline

Return your report as structured JSON with the following schema:
{{
    "executive_summary": {{
        "key_findings": "string",
        "market_outlook": "bullish|neutral|bearish",
        "top_recommendation": {{
            "symbol": "string",
            "action": "string",
            "rationale": "string"
        }}
    }},
    "market_environment": {{
        "macro_summary": "string",
        "economic_factors": ["string"],
        "market_regime": "string"
    }},
    "asset_analysis": {{
        "<symbol>": {{
            "current_price": number,
            "trend": "string",
            "technical_outlook": "string",
            "fundamental_assessment": "string",
            "risk_level": "low|moderate|high",
            "sentiment": "string",
            "key_levels": {{
                "support": number,
                "resistance": number
            }}
        }}
    }},
    "recommendations": [
        {{
            "symbol": "string",
            "action": "BUY|HOLD|SELL|WATCH",
            "conviction": "HIGH|MEDIUM|LOW",
            "target_price": number,
            "stop_loss": number,
            "position_size_pct": number,
            "rationale": "string",
            "time_horizon": "string",
            "risks": ["string"],
            "catalysts": ["string"]
        }}
    ],
    "portfolio_considerations": {{
        "diversification_score": number,
        "risk_allocation": "string",
        "rebalancing_suggestions": ["string"]
    }},
    "risk_warnings": {{
        "key_risks": ["string"],
        "scenarios": [
            {{
                "scenario": "string",
                "probability": "high|medium|low",
                "impact": "string"
            }}
        ],
        "hedging_ideas": ["string"]
    }},
    "conclusion": {{
        "action_items": ["string"],
        "key_dates": ["string"],
        "next_review": "string"
    }},
    "disclaimer": "string"
}}"""

        return self.run(task, context=analysis_results)

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
                    lines.append(f"  • {factor}")
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
                        lines.append(f"  ⚠ {risk}")
            lines.append("")

        # Risk Warnings
        if "risk_warnings" in report_data:
            warnings = report_data["risk_warnings"]
            lines.append("## RISK WARNINGS")
            lines.append("-" * 40)
            if "key_risks" in warnings:
                for risk in warnings["key_risks"]:
                    lines.append(f"  ⚠ {risk}")
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
            "This report is for informational purposes only and does not constitute investment advice. "
            "Past performance is not indicative of future results. Always conduct your own research "
            "and consult with a qualified financial advisor before making investment decisions."
        )
        lines.append(f"DISCLAIMER: {disclaimer}")
        lines.append("=" * 60)

        return "\n".join(lines)
