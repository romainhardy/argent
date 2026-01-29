"""Macro analysis agent for economic environment assessment."""

from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic

from argent.agents.base import AgentResult, BaseAgent, FinancialAgentType, ToolDefinition
from argent.prompts.macro_analysis import MACRO_ANALYSIS_SYSTEM_PROMPT


@dataclass
class MacroAnalysisAgent(BaseAgent):
    """Agent responsible for macroeconomic analysis."""

    client: Anthropic
    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 5

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.MACRO_ANALYSIS

    @property
    def system_prompt(self) -> str:
        return MACRO_ANALYSIS_SYSTEM_PROMPT

    def get_tools(self) -> list[ToolDefinition]:
        # Macro analysis is primarily analytical - uses data already collected
        return []

    def execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        raise ValueError(f"Unknown tool: {tool_name}")

    def analyze(
        self,
        economic_data: dict[str, Any],
        symbols: list[str],
        time_horizon: str = "medium",
    ) -> AgentResult:
        """
        Analyze macroeconomic environment and implications for investments.

        Args:
            economic_data: Collected economic indicators
            symbols: Symbols being analyzed
            time_horizon: Investment time horizon

        Returns:
            AgentResult with macro analysis
        """
        task = f"""Analyze the current macroeconomic environment and its implications for the following investments.

Symbols under analysis: {symbols}
Investment time horizon: {time_horizon}

Provide analysis covering:
1. Economic Cycle Assessment
   - Current phase (expansion, peak, contraction, trough)
   - Key evidence supporting this assessment
   - Expected duration

2. Monetary Policy Analysis
   - Current Fed stance (hawkish, neutral, dovish)
   - Interest rate outlook
   - Implications for asset classes

3. Inflation Assessment
   - Current inflation trend
   - Real vs nominal return considerations
   - Sector implications

4. Employment & Growth
   - Labor market conditions
   - GDP growth trajectory
   - Consumer spending outlook

5. Market Conditions
   - Risk appetite indicators (VIX, credit spreads)
   - Market sentiment
   - Liquidity conditions

6. Asset Class Implications
   - Stocks: favorable/unfavorable conditions
   - Bonds: interest rate sensitivity
   - Crypto: risk asset correlation
   - Sector rotation recommendations

Output your analysis as structured JSON with the following schema:
{{
    "economic_cycle": {{
        "phase": "string",
        "confidence": "high|medium|low",
        "evidence": ["string"],
        "outlook_months": number
    }},
    "monetary_policy": {{
        "stance": "hawkish|neutral|dovish",
        "rate_outlook": "rising|stable|falling",
        "implications": "string"
    }},
    "inflation": {{
        "trend": "rising|stable|falling",
        "current_rate": number,
        "outlook": "string"
    }},
    "growth": {{
        "gdp_trend": "accelerating|stable|decelerating",
        "employment": "strong|moderate|weak",
        "consumer_outlook": "string"
    }},
    "market_conditions": {{
        "risk_appetite": "risk-on|neutral|risk-off",
        "vix_level": "low|moderate|elevated|high",
        "sentiment": "bullish|neutral|bearish"
    }},
    "asset_implications": {{
        "stocks": {{ "outlook": "string", "score": number }},
        "bonds": {{ "outlook": "string", "score": number }},
        "crypto": {{ "outlook": "string", "score": number }},
        "recommended_sectors": ["string"]
    }},
    "key_risks": ["string"],
    "summary": "string"
}}"""

        return self.run(task, context={"economic_data": economic_data})
