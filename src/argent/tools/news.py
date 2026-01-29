"""Financial news fetching and sentiment analysis."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from argent.tools.rate_limiter import DataSource, get_rate_limiter


@dataclass
class NewsArticle:
    """News article data structure."""

    title: str
    source: str
    url: str
    published_at: datetime | None
    summary: str | None
    symbols: list[str]
    sentiment: str | None = None  # positive, negative, neutral
    relevance_score: float | None = None


class NewsClient:
    """Client for fetching financial news."""

    def __init__(self):
        self._rate_limiter = get_rate_limiter()
        self._client = httpx.Client(timeout=30.0)

    def get_news_for_symbol(
        self,
        symbol: str,
        limit: int = 10,
    ) -> list[NewsArticle]:
        """
        Fetch news articles for a specific symbol using Yahoo Finance.

        Note: This is a simplified implementation. In production,
        you might want to use a dedicated news API like Finnhub or Alpha Vantage News.
        """
        import yfinance as yf

        self._rate_limiter.acquire_sync(DataSource.YAHOO_FINANCE)

        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news or []
        except Exception:
            return []

        articles = []
        for item in news[:limit]:
            published = None
            if "providerPublishTime" in item:
                try:
                    published = datetime.fromtimestamp(item["providerPublishTime"])
                except (ValueError, TypeError):
                    pass

            articles.append(
                NewsArticle(
                    title=item.get("title", ""),
                    source=item.get("publisher", "Unknown"),
                    url=item.get("link", ""),
                    published_at=published,
                    summary=None,  # Yahoo doesn't provide summaries
                    symbols=[symbol],
                    sentiment=None,
                    relevance_score=None,
                )
            )

        return articles

    def get_market_news(self, limit: int = 10) -> list[NewsArticle]:
        """Fetch general market news using SPY as a proxy."""
        return self.get_news_for_symbol("SPY", limit=limit)

    def get_crypto_news(self, limit: int = 10) -> list[NewsArticle]:
        """Fetch cryptocurrency news using BTC-USD as a proxy."""
        return self.get_news_for_symbol("BTC-USD", limit=limit)

    def analyze_sentiment_simple(self, text: str) -> dict[str, Any]:
        """
        Simple keyword-based sentiment analysis.

        Note: This is a basic implementation. The agent can use Claude
        for more sophisticated sentiment analysis.
        """
        text_lower = text.lower()

        positive_words = [
            "surge", "soar", "rally", "gain", "rise", "jump", "bull",
            "growth", "profit", "beat", "exceed", "strong", "upgrade",
            "buy", "outperform", "positive", "optimistic", "boom",
        ]
        negative_words = [
            "crash", "plunge", "fall", "drop", "decline", "loss",
            "bear", "miss", "weak", "downgrade", "sell", "underperform",
            "negative", "pessimistic", "recession", "fear", "crisis",
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            sentiment = "positive"
            score = min(positive_count / (positive_count + negative_count + 1), 1.0)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = -min(negative_count / (positive_count + negative_count + 1), 1.0)
        else:
            sentiment = "neutral"
            score = 0.0

        return {
            "sentiment": sentiment,
            "score": score,
            "positive_signals": positive_count,
            "negative_signals": negative_count,
        }

    def get_news_summary(self, symbols: list[str]) -> dict[str, Any]:
        """Get a summary of news for multiple symbols."""
        all_articles = []
        sentiment_summary = {"positive": 0, "negative": 0, "neutral": 0}

        for symbol in symbols[:5]:  # Limit to avoid rate limits
            articles = self.get_news_for_symbol(symbol, limit=5)

            for article in articles:
                sentiment = self.analyze_sentiment_simple(article.title)
                article.sentiment = sentiment["sentiment"]
                sentiment_summary[sentiment["sentiment"]] += 1

            all_articles.extend(articles)

        # Sort by date, most recent first
        all_articles.sort(
            key=lambda x: x.published_at or datetime.min,
            reverse=True,
        )

        total = sum(sentiment_summary.values())
        if total > 0:
            overall_sentiment = max(sentiment_summary, key=sentiment_summary.get)
            sentiment_score = (sentiment_summary["positive"] - sentiment_summary["negative"]) / total
        else:
            overall_sentiment = "neutral"
            sentiment_score = 0.0

        return {
            "articles": all_articles[:20],
            "total_articles": len(all_articles),
            "sentiment_distribution": sentiment_summary,
            "overall_sentiment": overall_sentiment,
            "sentiment_score": sentiment_score,
        }

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
