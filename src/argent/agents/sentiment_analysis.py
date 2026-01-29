"""Sentiment analysis agent for news and market sentiment."""

from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic

from argent.agents.base import AgentResult, BaseAgent, FinancialAgentType, ToolDefinition
from argent.prompts.sentiment_analysis import SENTIMENT_ANALYSIS_SYSTEM_PROMPT
from argent.tools.news import NewsClient


@dataclass
class SentimentAnalysisAgent(BaseAgent):
    """Agent responsible for sentiment analysis."""

    client: Anthropic
    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 8
    news_client: NewsClient = field(default_factory=NewsClient)

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.SENTIMENT_ANALYSIS

    @property
    def system_prompt(self) -> str:
        return SENTIMENT_ANALYSIS_SYSTEM_PROMPT

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="get_symbol_news",
                description="Get recent news articles for a symbol",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbol to get news for"},
                        "limit": {"type": "integer", "description": "Max articles", "default": 10},
                    },
                    "required": ["symbol"],
                },
            ),
            ToolDefinition(
                name="get_market_news",
                description="Get general market news",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max articles", "default": 10},
                    },
                },
            ),
            ToolDefinition(
                name="analyze_headline_sentiment",
                description="Analyze sentiment of a news headline",
                input_schema={
                    "type": "object",
                    "properties": {
                        "headline": {"type": "string", "description": "News headline to analyze"},
                    },
                    "required": ["headline"],
                },
            ),
        ]

    def execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        if tool_name == "get_symbol_news":
            articles = self.news_client.get_news_for_symbol(
                symbol=tool_input["symbol"],
                limit=tool_input.get("limit", 10),
            )
            return [
                {
                    "title": a.title,
                    "source": a.source,
                    "published_at": a.published_at.isoformat() if a.published_at else None,
                    "url": a.url,
                }
                for a in articles
            ]

        elif tool_name == "get_market_news":
            articles = self.news_client.get_market_news(limit=tool_input.get("limit", 10))
            return [
                {
                    "title": a.title,
                    "source": a.source,
                    "published_at": a.published_at.isoformat() if a.published_at else None,
                    "url": a.url,
                }
                for a in articles
            ]

        elif tool_name == "analyze_headline_sentiment":
            return self.news_client.analyze_sentiment_simple(tool_input["headline"])

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def analyze(
        self,
        news_data: dict[str, Any],
        symbols: list[str],
    ) -> AgentResult:
        """
        Perform sentiment analysis on news and market data.

        Args:
            news_data: Previously collected news data
            symbols: List of symbols being analyzed

        Returns:
            AgentResult with sentiment analysis
        """
        task = f"""Perform comprehensive sentiment analysis for the following symbols: {symbols}

Analyze:
1. News Sentiment
   - Analyze headlines for each symbol
   - Identify key themes and topics
   - Assess overall news tone

2. Market Sentiment Indicators
   - Fear/greed assessment
   - Institutional vs retail sentiment signals
   - Options market sentiment (if available)

3. Social/Media Buzz
   - Notable mentions or trends
   - Viral news or events
   - Influencer opinions

4. Sentiment Impact Assessment
   - How sentiment may affect price
   - Contrarian indicators
   - Sentiment extremes to watch

For each symbol, provide:
- News sentiment score (-1 to 1)
- Key positive catalysts
- Key negative concerns
- Overall sentiment assessment

Return your analysis as structured JSON with the following schema:
{{
    "symbols": {{
        "<symbol>": {{
            "news_sentiment": {{
                "score": number,
                "assessment": "bullish|neutral|bearish",
                "article_count": number,
                "key_themes": ["string"]
            }},
            "positive_catalysts": ["string"],
            "negative_concerns": ["string"],
            "notable_events": ["string"],
            "sentiment_trend": "improving|stable|deteriorating"
        }}
    }},
    "market_sentiment": {{
        "overall": "bullish|neutral|bearish",
        "fear_greed_estimate": "extreme_fear|fear|neutral|greed|extreme_greed",
        "key_market_themes": ["string"]
    }},
    "contrarian_signals": ["string"],
    "summary": "string"
}}"""

        return self.run(task, context={"news_data": news_data, "symbols": symbols})
