"""Cryptocurrency data client using CoinGecko API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pycoingecko import CoinGeckoAPI

from argent.tools.cache import cached, get_cache
from argent.tools.rate_limiter import DataSource, get_rate_limiter


@dataclass
class CryptoPriceData:
    """Normalized crypto price data structure."""

    symbol: str
    coin_id: str
    timestamp: datetime
    price_usd: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    price_change_7d: float | None
    price_change_30d: float | None
    source: str = "coingecko"


# Common crypto symbol to CoinGecko ID mapping
SYMBOL_TO_ID: dict[str, str] = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "AVAX": "avalanche-2",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "LTC": "litecoin",
    "FIL": "filecoin",
}


class CryptoDataClient:
    """Client for fetching cryptocurrency data from CoinGecko."""

    def __init__(self):
        self._cg = CoinGeckoAPI()
        self._rate_limiter = get_rate_limiter()
        self._id_cache: dict[str, str] = SYMBOL_TO_ID.copy()
        # Register dataclasses for cache deserialization
        cache = get_cache()
        cache.register_dataclass(CryptoPriceData)

    def _get_coin_id(self, symbol: str) -> str | None:
        """Convert a symbol to CoinGecko coin ID."""
        symbol_upper = symbol.upper()
        if symbol_upper in self._id_cache:
            return self._id_cache[symbol_upper]

        # Try to find the coin by searching
        self._rate_limiter.acquire_sync(DataSource.COINGECKO)
        try:
            coins = self._cg.get_coins_list()
            for coin in coins:
                if coin["symbol"].upper() == symbol_upper:
                    self._id_cache[symbol_upper] = coin["id"]
                    return coin["id"]
        except Exception:
            pass

        return None

    @cached("crypto_price")
    def get_current_price(self, symbols: list[str]) -> dict[str, CryptoPriceData]:
        """Get current prices for multiple cryptocurrencies."""
        self._rate_limiter.acquire_sync(DataSource.COINGECKO)

        # Convert symbols to coin IDs
        coin_ids = []
        symbol_to_id_map = {}
        for symbol in symbols:
            coin_id = self._get_coin_id(symbol)
            if coin_id:
                coin_ids.append(coin_id)
                symbol_to_id_map[coin_id] = symbol.upper()

        if not coin_ids:
            return {}

        try:
            data = self._cg.get_coins_markets(
                vs_currency="usd",
                ids=",".join(coin_ids),
                price_change_percentage="24h,7d,30d",
            )
        except Exception:
            return {}

        result = {}
        for coin in data:
            symbol = symbol_to_id_map.get(coin["id"], coin["symbol"].upper())
            result[symbol] = CryptoPriceData(
                symbol=symbol,
                coin_id=coin["id"],
                timestamp=datetime.now(),
                price_usd=coin.get("current_price", 0),
                market_cap=coin.get("market_cap", 0),
                volume_24h=coin.get("total_volume", 0),
                price_change_24h=coin.get("price_change_percentage_24h", 0),
                price_change_7d=coin.get("price_change_percentage_7d_in_currency"),
                price_change_30d=coin.get("price_change_percentage_30d_in_currency"),
            )

        return result

    @cached("crypto_history")
    def get_price_history(
        self,
        symbol: str,
        days: int = 365,
    ) -> list[dict[str, Any]]:
        """
        Fetch historical price data for a cryptocurrency.

        Args:
            symbol: Crypto symbol (e.g., BTC, ETH)
            days: Number of days of history (1, 7, 14, 30, 90, 180, 365, max)

        Returns:
            List of price data dictionaries
        """
        coin_id = self._get_coin_id(symbol)
        if not coin_id:
            return []

        self._rate_limiter.acquire_sync(DataSource.COINGECKO)

        try:
            data = self._cg.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency="usd",
                days=days,
            )
        except Exception:
            return []

        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        market_caps = data.get("market_caps", [])

        result = []
        for i, (timestamp_ms, price) in enumerate(prices):
            result.append(
                {
                    "symbol": symbol.upper(),
                    "timestamp": datetime.fromtimestamp(timestamp_ms / 1000),
                    "price_usd": price,
                    "volume": volumes[i][1] if i < len(volumes) else None,
                    "market_cap": market_caps[i][1] if i < len(market_caps) else None,
                    "source": "coingecko",
                }
            )

        return result

    @cached("crypto_info")
    def get_coin_info(self, symbol: str) -> dict[str, Any] | None:
        """Get detailed information about a cryptocurrency."""
        coin_id = self._get_coin_id(symbol)
        if not coin_id:
            return None

        self._rate_limiter.acquire_sync(DataSource.COINGECKO)

        try:
            data = self._cg.get_coin_by_id(
                id=coin_id,
                localization=False,
                tickers=False,
                community_data=False,
                developer_data=False,
            )
        except Exception:
            return None

        market_data = data.get("market_data", {})

        return {
            "symbol": symbol.upper(),
            "name": data.get("name"),
            "description": data.get("description", {}).get("en", "")[:500],
            "market_cap_rank": data.get("market_cap_rank"),
            "current_price": market_data.get("current_price", {}).get("usd"),
            "market_cap": market_data.get("market_cap", {}).get("usd"),
            "total_volume": market_data.get("total_volume", {}).get("usd"),
            "circulating_supply": market_data.get("circulating_supply"),
            "total_supply": market_data.get("total_supply"),
            "max_supply": market_data.get("max_supply"),
            "ath": market_data.get("ath", {}).get("usd"),
            "ath_date": market_data.get("ath_date", {}).get("usd"),
            "atl": market_data.get("atl", {}).get("usd"),
            "atl_date": market_data.get("atl_date", {}).get("usd"),
            "price_change_24h": market_data.get("price_change_percentage_24h"),
            "price_change_7d": market_data.get("price_change_percentage_7d"),
            "price_change_30d": market_data.get("price_change_percentage_30d"),
            "price_change_1y": market_data.get("price_change_percentage_1y"),
        }

    @cached("crypto_price", ttl=300)  # 5 minutes for global data
    def get_global_market_data(self) -> dict[str, Any]:
        """Get global cryptocurrency market data."""
        self._rate_limiter.acquire_sync(DataSource.COINGECKO)

        try:
            data = self._cg.get_global()
        except Exception:
            return {}

        return {
            "total_market_cap_usd": data.get("data", {}).get("total_market_cap", {}).get("usd"),
            "total_volume_24h_usd": data.get("data", {}).get("total_volume", {}).get("usd"),
            "btc_dominance": data.get("data", {}).get("market_cap_percentage", {}).get("btc"),
            "eth_dominance": data.get("data", {}).get("market_cap_percentage", {}).get("eth"),
            "active_cryptocurrencies": data.get("data", {}).get("active_cryptocurrencies"),
            "markets": data.get("data", {}).get("markets"),
            "market_cap_change_24h": data.get("data", {}).get("market_cap_change_percentage_24h_usd"),
        }

    @cached("crypto_price", ttl=900)  # 15 minutes for trending
    def get_trending(self) -> list[dict[str, Any]]:
        """Get trending cryptocurrencies."""
        self._rate_limiter.acquire_sync(DataSource.COINGECKO)

        try:
            data = self._cg.get_search_trending()
        except Exception:
            return []

        result = []
        for coin in data.get("coins", [])[:10]:
            item = coin.get("item", {})
            result.append(
                {
                    "symbol": item.get("symbol", "").upper(),
                    "name": item.get("name"),
                    "market_cap_rank": item.get("market_cap_rank"),
                    "score": item.get("score"),
                }
            )

        return result
