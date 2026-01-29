#!/bin/bash
# Validates that Bash commands are allowed Argent operations
# Exit codes: 0 = allow, 2 = block

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Allowed patterns for Argent financial tools
ALLOWED_PATTERNS=(
    "source .argent-env/bin/activate && python -c"
    "source .argent-env/bin/activate && python -m argent"
    "cd /Users/romainhardy/code/argent && python -c"
    "cd /Users/romainhardy/code/argent && python -m argent"
    ".argent-env/bin/python"
)

for pattern in "${ALLOWED_PATTERNS[@]}"; do
    if [[ "$COMMAND" == *"$pattern"* ]]; then
        exit 0  # Allow
    fi
done

# Block anything else
echo "Blocked: Only Argent Python commands are allowed" >&2
exit 2
