"""Sentiment analysis agent using rule-based analysis."""

from dataclasses import dataclass
from typing import Any

from argent.agents.base import AgentResult, FinancialAgentType


# Simple sentiment keywords for rule-based analysis
POSITIVE_KEYWORDS = [
    "beat", "beats", "exceeds", "exceeded", "surpass", "surpassed", "strong", "growth",
    "profit", "profitable", "gain", "gains", "up", "rise", "rises", "rising", "rally",
    "bullish", "upgrade", "upgraded", "buy", "outperform", "positive", "record", "high",
    "surge", "surges", "jump", "jumps", "soar", "soars", "boom", "breakthrough", "success"
]

NEGATIVE_KEYWORDS = [
    "miss", "misses", "missed", "below", "decline", "declines", "declining", "fall",
    "falls", "falling", "drop", "drops", "loss", "losses", "down", "weak", "weakness",
    "bearish", "downgrade", "downgraded", "sell", "underperform", "negative", "low",
    "plunge", "plunges", "crash", "crashes", "slump", "slumps", "fail", "fails", "concern"
]


@dataclass
class SentimentAnalysisAgent:
    """Agent responsible for sentiment analysis using rule-based methods."""

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.SENTIMENT_ANALYSIS

    def _analyze_headline(self, headline: str) -> dict[str, Any]:
        """Analyze sentiment of a single headline using keyword matching."""
        headline_lower = headline.lower()

        positive_count = sum(1 for word in POSITIVE_KEYWORDS if word in headline_lower)
        negative_count = sum(1 for word in NEGATIVE_KEYWORDS if word in headline_lower)

        if positive_count > negative_count:
            sentiment = "positive"
            score = min(positive_count / 3, 1.0)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = -min(negative_count / 3, 1.0)
        else:
            sentiment = "neutral"
            score = 0.0

        return {"sentiment": sentiment, "score": score}

    def analyze(
        self,
        news_data: dict[str, list[dict[str, Any]]],
        symbols: list[str],
    ) -> AgentResult:
        """
        Perform sentiment analysis on news data using rule-based methods.

        Args:
            news_data: Dict mapping symbol to list of news articles
            symbols: List of symbols to analyze

        Returns:
            AgentResult with sentiment analysis
        """
        results = {"symbols": {}}

        for symbol in symbols:
            articles = news_data.get(symbol, [])

            if not articles:
                results["symbols"][symbol] = {
                    "overall": "neutral",
                    "score": 0.0,
                    "news_count": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "recent_headlines": [],
                    "interpretation": f"No news data available for {symbol}",
                }
                continue

            # Analyze each article
            sentiments = []
            analyzed_headlines = []

            for article in articles[:20]:  # Limit to most recent 20
                headline = article.get("title", article.get("headline", ""))
                if not headline:
                    continue

                analysis = self._analyze_headline(headline)
                sentiments.append(analysis)
                analyzed_headlines.append({
                    "title": headline,
                    "sentiment": analysis["sentiment"],
                    "source": article.get("source", "Unknown"),
                    "date": article.get("published_at", article.get("date", "")),
                })

            if not sentiments:
                results["symbols"][symbol] = {
                    "overall": "neutral",
                    "score": 0.0,
                    "news_count": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "recent_headlines": [],
                    "interpretation": f"No analyzable headlines for {symbol}",
                }
                continue

            # Aggregate sentiment
            positive_count = sum(1 for s in sentiments if s["sentiment"] == "positive")
            negative_count = sum(1 for s in sentiments if s["sentiment"] == "negative")
            neutral_count = sum(1 for s in sentiments if s["sentiment"] == "neutral")
            total = len(sentiments)

            avg_score = sum(s["score"] for s in sentiments) / total

            if avg_score > 0.2:
                overall = "bullish"
            elif avg_score < -0.2:
                overall = "bearish"
            else:
                overall = "neutral"

            # Generate interpretation
            if overall == "bullish":
                interpretation = f"News sentiment for {symbol} is positive with {positive_count} bullish headlines out of {total}. Market sentiment appears favorable."
            elif overall == "bearish":
                interpretation = f"News sentiment for {symbol} is negative with {negative_count} bearish headlines out of {total}. Caution advised."
            else:
                interpretation = f"News sentiment for {symbol} is mixed with no clear directional bias."

            results["symbols"][symbol] = {
                "overall": overall,
                "score": avg_score,
                "news_count": total,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "recent_headlines": analyzed_headlines[:5],
                "interpretation": interpretation,
            }

        # Overall summary
        sentiments_summary = []
        for sym, data in results["symbols"].items():
            sentiments_summary.append(f"{sym}: {data['overall']}")

        results["summary"] = "Sentiment analysis complete. " + "; ".join(sentiments_summary) if sentiments_summary else "No symbols analyzed."

        return AgentResult(
            success=True,
            data=results,
            error=None,
        )
