---
name: argent-compare
description: Compare two assets side-by-side
user-invocable: true
argument-hint: [SYMBOL1] [SYMBOL2]
---

# Asset Comparison

<command-name>argent-compare</command-name>

Compare two assets side-by-side across multiple dimensions.

## Arguments
- `SYMBOL1`: First asset (e.g., AAPL)
- `SYMBOL2`: Second asset (e.g., MSFT)

## Workflow

### Step 1: Parallel Data Collection
Use the **argent-data-collector** agent for both symbols simultaneously:

Launch in parallel:
```
Collect market data for {SYMBOL1}:
- Current price and metrics
- 1-year price history
- Company info (if stock)
```

```
Collect market data for {SYMBOL2}:
- Current price and metrics
- 1-year price history
- Company info (if stock)
```

### Step 2: Parallel Analysis
For each symbol, run the following agents in parallel:

For **{SYMBOL1}**:
- argent-technical-analyst
- argent-risk-analyst
- argent-fundamental-analyst (if stock)

For **{SYMBOL2}**:
- argent-technical-analyst
- argent-risk-analyst
- argent-fundamental-analyst (if stock)

### Step 3: Comparison Report
After all analyses complete, synthesize a comparison:

## Output Format

Present a side-by-side comparison table:

### Price & Performance
| Metric | {SYMBOL1} | {SYMBOL2} | Winner |
|--------|-----------|-----------|--------|
| Current Price | $ | $ | |
| 1Y Return | % | % | |
| YTD Return | % | % | |

### Technical Indicators
| Indicator | {SYMBOL1} | {SYMBOL2} | Winner |
|-----------|-----------|-----------|--------|
| Trend | | | |
| RSI | | | |
| Signal | | | |

### Risk Metrics
| Metric | {SYMBOL1} | {SYMBOL2} | Winner |
|--------|-----------|-----------|--------|
| Volatility | % | % | |
| Max Drawdown | % | % | |
| Sharpe Ratio | | | |
| VaR (95%) | % | % | |

### Fundamentals (Stocks Only)
| Metric | {SYMBOL1} | {SYMBOL2} | Winner |
|--------|-----------|-----------|--------|
| P/E Ratio | | | |
| PEG Ratio | | | |
| Profit Margin | % | % | |
| ROE | % | % | |

### Summary
- **Better Value**: {SYMBOL}
- **Lower Risk**: {SYMBOL}
- **Stronger Momentum**: {SYMBOL}
- **Overall Preference**: {SYMBOL}

### Recommendation
Provide a clear recommendation on which asset is preferable based on:
- Investment goals (growth vs. value vs. income)
- Risk tolerance
- Time horizon

## Example Usage

```
/argent-compare AAPL MSFT
/argent-compare BTC ETH
/argent-compare NVDA AMD
/argent-compare GOOGL META
```
