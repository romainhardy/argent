#!/usr/bin/env python3
"""PostToolUse hook for error recovery with exponential backoff.

This hook detects API errors (rate limits, timeouts, connection errors)
and implements retry logic with exponential backoff.

Usage in agent .md files:
    hooks:
      PostToolUse:
        - matcher: Bash
          hooks:
            - type: command
              command: python /path/to/validate-and-retry.py
"""

import json
import os
import sys
import time
from pathlib import Path

# Configuration
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds
MAX_DELAY = 30.0  # seconds

# Error patterns that trigger retry
RETRY_PATTERNS = [
    # HTTP errors
    "429",
    "rate limit",
    "too many requests",
    "quota exceeded",
    # Timeout errors
    "timeout",
    "timed out",
    "connection timeout",
    "read timeout",
    # Connection errors
    "connection error",
    "connection refused",
    "connection reset",
    "network error",
    "socket error",
    # API-specific errors
    "temporarily unavailable",
    "service unavailable",
    "internal server error",
    "bad gateway",
    "gateway timeout",
]

# Patterns that indicate success (should not retry)
SUCCESS_PATTERNS = [
    "current_price",
    "symbol",
    "===",  # Common output header pattern
]

# State file for tracking retries
STATE_DIR = Path(__file__).parent.parent / "data" / "retry_state"


def get_state_file(session_id: str) -> Path:
    """Get the state file path for a session."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    return STATE_DIR / f"{session_id}.json"


def load_state(session_id: str) -> dict:
    """Load retry state for a session."""
    state_file = get_state_file(session_id)
    if state_file.exists():
        try:
            with open(state_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"retries": 0, "last_error": None, "last_attempt": 0}


def save_state(session_id: str, state: dict) -> None:
    """Save retry state for a session."""
    state_file = get_state_file(session_id)
    with open(state_file, "w") as f:
        json.dump(state, f)


def clear_state(session_id: str) -> None:
    """Clear retry state (on success)."""
    state_file = get_state_file(session_id)
    if state_file.exists():
        state_file.unlink()


def should_retry(output: str) -> bool:
    """Determine if the output indicates a retriable error."""
    output_lower = output.lower()

    # Check for success patterns first
    for pattern in SUCCESS_PATTERNS:
        if pattern.lower() in output_lower:
            return False

    # Check for error patterns
    for pattern in RETRY_PATTERNS:
        if pattern.lower() in output_lower:
            return True

    return False


def calculate_delay(retry_count: int) -> float:
    """Calculate exponential backoff delay."""
    delay = BASE_DELAY * (2 ** retry_count)
    return min(delay, MAX_DELAY)


def main():
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If we can't parse input, pass through
        sys.exit(0)

    # Extract relevant information
    tool_name = input_data.get("tool_name", "")
    tool_output = input_data.get("tool_output", {})

    # Only handle Bash tool outputs
    if tool_name != "Bash":
        sys.exit(0)

    # Get the command output
    stdout = tool_output.get("stdout", "")
    stderr = tool_output.get("stderr", "")
    exit_code = tool_output.get("exit_code", 0)

    combined_output = f"{stdout}\n{stderr}"

    # Generate a session ID based on the command
    command = input_data.get("tool_input", {}).get("command", "")
    session_id = f"retry_{hash(command) % 1000000}"

    # Check if this looks like an error
    if exit_code != 0 or should_retry(combined_output):
        state = load_state(session_id)

        if state["retries"] < MAX_RETRIES:
            # Calculate delay
            delay = calculate_delay(state["retries"])

            # Update state
            state["retries"] += 1
            state["last_error"] = combined_output[:500]
            state["last_attempt"] = time.time()
            save_state(session_id, state)

            # Log the retry (to stderr so it's visible)
            print(
                f"[Retry Hook] Detected transient error. "
                f"Retry {state['retries']}/{MAX_RETRIES} in {delay:.1f}s",
                file=sys.stderr
            )

            # Wait before retry
            time.sleep(delay)

            # Signal to retry by outputting instruction
            # Note: The actual retry is handled by the agent re-running the command
            print(json.dumps({
                "action": "retry",
                "retry_count": state["retries"],
                "delay": delay,
                "reason": "Transient error detected",
            }))

            # Exit with special code to indicate retry suggestion
            # (0 = allow, non-zero = may indicate retry needed)
            sys.exit(0)
        else:
            # Max retries exceeded
            clear_state(session_id)
            print(
                f"[Retry Hook] Max retries ({MAX_RETRIES}) exceeded. Giving up.",
                file=sys.stderr
            )
            sys.exit(0)
    else:
        # Success - clear any retry state
        clear_state(session_id)
        sys.exit(0)


if __name__ == "__main__":
    main()
