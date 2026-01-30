---
name: argent-analyze
description: Run full investment analysis on a symbol
user-invocable: true
argument-hint: [SYMBOL]
---

# Full Investment Analysis

<command-name>argent-analyze</command-name>

You are orchestrating a comprehensive investment analysis for the requested symbol.

## Arguments
- `SYMBOL`: The stock ticker or cryptocurrency symbol to analyze (e.g., AAPL, BTC, MSFT)

## Workflow

Execute the following analysis pipeline:

### Step 1: Data Collection
Use the **argent-data-collector** agent to gather market data:
```
Collect all available market data for {SYMBOL}:
- Current price and trading metrics
- Historical price data (1 year)
- Company info and fundamentals (if stock)
- Recent news headlines
```

### Step 2: Parallel Analysis
Launch these analysts in parallel using the Task tool:

1. **argent-technical-analyst**: Analyze price action, trends, RSI, MACD, support/resistance
2. **argent-risk-analyst**: Calculate VaR, volatility, Sharpe ratio, max drawdown
3. **argent-sentiment-analyst**: Analyze news sentiment and market mood
4. **argent-macro-analyst**: Assess economic environment impact

If analyzing a **stock** (not crypto), also launch:
5. **argent-fundamental-analyst**: Evaluate P/E, growth, margins, fair value

### Step 3: Report Generation
After all analyses complete, use the **argent-report-generator** agent to synthesize:
```
Generate a comprehensive investment report for {SYMBOL} combining:
- Technical analysis findings
- Risk assessment
- Sentiment analysis
- Macro environment
- Fundamental analysis (if applicable)

Include:
- Executive summary with clear recommendation
- Detailed analysis sections
- Specific entry/exit recommendations
- Position sizing guidance
- Key risks and catalysts
```

## Output Format

Present the final report to the user with:
1. **Executive Summary** (2-3 sentences)
2. **Recommendation** with conviction level (1-5 stars)
3. **Key Findings** by analysis type
4. **Actionable Recommendations** table
5. **Risk Warnings**

## Example Usage

```
/argent-analyze NVDA
/argent-analyze BTC
/argent-analyze MSFT
```
