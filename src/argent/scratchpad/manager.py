"""Scratchpad manager for inter-agent data sharing.

The scratchpad allows agents to:
1. Share fetched data to avoid redundant API calls
2. Store intermediate analysis results
3. Pass structured data between pipeline stages

Data is stored in JSON files, organized by session and data type.
"""

import json
import os
import time
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Default scratchpad directory
SCRATCHPAD_DIR = Path(__file__).parent.parent.parent.parent / "data" / "scratchpad"


def _serialize_for_json(obj: Any) -> Any:
    """Serialize objects for JSON storage."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return {"__dataclass__": type(obj).__name__, "__data__": asdict(obj)}
    elif isinstance(obj, datetime):
        return {"__datetime__": obj.isoformat()}
    elif isinstance(obj, (list, tuple)):
        return [_serialize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    return obj


def _deserialize_from_json(obj: Any) -> Any:
    """Deserialize objects from JSON storage."""
    if isinstance(obj, dict):
        if "__datetime__" in obj:
            return datetime.fromisoformat(obj["__datetime__"])
        elif "__dataclass__" in obj:
            # Return as dict, dataclass reconstruction is caller's responsibility
            return obj["__data__"]
        return {k: _deserialize_from_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deserialize_from_json(item) for item in obj]
    return obj


class Scratchpad:
    """
    Scratchpad for sharing data between agents.

    Usage:
        scratchpad = Scratchpad(session_id="analysis_20240115")

        # Store data (data collector)
        scratchpad.write("market_data", "AAPL", price_data)

        # Read data (analyst agents)
        data = scratchpad.read("market_data", "AAPL")
        if data:
            # Use cached data
            ...
        else:
            # Fetch fresh data
            ...

    Directory structure:
        data/scratchpad/
            {session_id}/
                market_data/
                    AAPL.json
                    MSFT.json
                technical_analysis/
                    AAPL.json
                risk_analysis/
                    AAPL.json
                ...
    """

    def __init__(
        self,
        session_id: str | None = None,
        scratchpad_dir: Path | None = None,
    ):
        """
        Initialize scratchpad.

        Args:
            session_id: Unique identifier for this analysis session.
                       Defaults to timestamp-based ID.
            scratchpad_dir: Override default scratchpad directory.
        """
        self.session_id = session_id or f"session_{int(time.time())}"
        self.base_dir = scratchpad_dir or SCRATCHPAD_DIR
        self.session_dir = self.base_dir / self.session_id
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """Ensure necessary directories exist."""
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, category: str, key: str) -> Path:
        """Get the file path for a data entry."""
        category_dir = self.session_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        # Sanitize key for use as filename
        safe_key = "".join(c if c.isalnum() or c in "._-" else "_" for c in key)
        return category_dir / f"{safe_key}.json"

    def write(
        self,
        category: str,
        key: str,
        data: Any,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Write data to the scratchpad.

        Args:
            category: Data category (e.g., "market_data", "technical_analysis")
            key: Data key (e.g., "AAPL", "BTC")
            data: Data to store
            metadata: Optional metadata (source, timestamp, etc.)
        """
        path = self._get_path(category, key)

        entry = {
            "key": key,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "data": _serialize_for_json(data),
            "metadata": metadata or {},
        }

        with open(path, "w") as f:
            json.dump(entry, f, indent=2, default=str)

    def read(
        self,
        category: str,
        key: str,
        max_age_seconds: int | None = None,
    ) -> Any | None:
        """
        Read data from the scratchpad.

        Args:
            category: Data category
            key: Data key
            max_age_seconds: Maximum age of data in seconds (None = no limit)

        Returns:
            Data if found and not stale, None otherwise
        """
        path = self._get_path(category, key)

        if not path.exists():
            return None

        try:
            with open(path, "r") as f:
                entry = json.load(f)

            # Check age if max_age specified
            if max_age_seconds is not None:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                age = (datetime.now() - timestamp).total_seconds()
                if age > max_age_seconds:
                    return None

            return _deserialize_from_json(entry.get("data"))

        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def read_with_metadata(
        self,
        category: str,
        key: str,
    ) -> tuple[Any | None, dict[str, Any]]:
        """
        Read data with metadata from the scratchpad.

        Returns:
            Tuple of (data, metadata). Data is None if not found.
        """
        path = self._get_path(category, key)

        if not path.exists():
            return None, {}

        try:
            with open(path, "r") as f:
                entry = json.load(f)

            data = _deserialize_from_json(entry.get("data"))
            metadata = entry.get("metadata", {})
            metadata["_timestamp"] = entry.get("timestamp")

            return data, metadata

        except (json.JSONDecodeError, KeyError, ValueError):
            return None, {}

    def exists(self, category: str, key: str) -> bool:
        """Check if data exists in the scratchpad."""
        return self._get_path(category, key).exists()

    def list_keys(self, category: str) -> list[str]:
        """List all keys in a category."""
        category_dir = self.session_dir / category
        if not category_dir.exists():
            return []

        keys = []
        for path in category_dir.glob("*.json"):
            keys.append(path.stem)
        return keys

    def list_categories(self) -> list[str]:
        """List all categories in the session."""
        if not self.session_dir.exists():
            return []

        return [
            d.name
            for d in self.session_dir.iterdir()
            if d.is_dir()
        ]

    def delete(self, category: str, key: str) -> bool:
        """Delete a specific entry."""
        path = self._get_path(category, key)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear_category(self, category: str) -> int:
        """Clear all entries in a category. Returns count deleted."""
        category_dir = self.session_dir / category
        if not category_dir.exists():
            return 0

        count = 0
        for path in category_dir.glob("*.json"):
            path.unlink()
            count += 1
        return count

    def clear_session(self) -> None:
        """Clear all data in this session."""
        import shutil
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)
        self._ensure_dirs()

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of scratchpad contents."""
        summary = {
            "session_id": self.session_id,
            "categories": {},
        }

        for category in self.list_categories():
            keys = self.list_keys(category)
            summary["categories"][category] = {
                "count": len(keys),
                "keys": keys,
            }

        return summary


# Global scratchpad instance (lazy initialization)
_scratchpad_instance: Scratchpad | None = None


def get_scratchpad(session_id: str | None = None) -> Scratchpad:
    """
    Get a scratchpad instance.

    Args:
        session_id: Session ID. If None and no global instance exists,
                   creates one with timestamp-based ID.

    Returns:
        Scratchpad instance
    """
    global _scratchpad_instance

    if session_id:
        # Create new instance with specific session
        return Scratchpad(session_id=session_id)

    if _scratchpad_instance is None:
        _scratchpad_instance = Scratchpad()

    return _scratchpad_instance


def set_global_scratchpad(scratchpad: Scratchpad) -> None:
    """Set the global scratchpad instance."""
    global _scratchpad_instance
    _scratchpad_instance = scratchpad


# Data category constants
class Categories:
    """Standard scratchpad categories."""
    MARKET_DATA = "market_data"
    CRYPTO_DATA = "crypto_data"
    ECONOMIC_DATA = "economic_data"
    NEWS = "news"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    RISK_ANALYSIS = "risk_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    MACRO_ANALYSIS = "macro_analysis"
    REPORT = "report"
