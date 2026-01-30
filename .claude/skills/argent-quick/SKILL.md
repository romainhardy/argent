---
name: argent-quick
description: Quick single-dimension analysis
user-invocable: true
argument-hint: [SYMBOL] [technical|fundamental|risk|sentiment|macro]
---

# Quick Analysis

<command-name>argent-quick</command-name>

Perform a focused, single-dimension analysis on a symbol.

## Arguments
- `SYMBOL`: The stock ticker or cryptocurrency symbol (e.g., AAPL, BTC)
- `TYPE`: Analysis type - one of:
  - `technical` - Price action, indicators, trends
  - `fundamental` - Valuations, financials (stocks only)
  - `risk` - Volatility, VaR, risk metrics
  - `sentiment` - News sentiment, market mood
  - `macro` - Economic environment (no symbol needed)

## Workflow

Based on the analysis type requested:

### Technical Analysis
Use the **argent-technical-analyst** agent:
```
Perform technical analysis on {SYMBOL}:
- Current trend and strength
- RSI, MACD, Bollinger Bands
- Support and resistance levels
- Trading signal with entry/exit
```

### Fundamental Analysis
Use the **argent-fundamental-analyst** agent:
```
Perform fundamental analysis on {SYMBOL}:
- Valuation metrics (P/E, PEG, P/B)
- Growth rates and margins
- Financial health assessment
- Fair value estimate
```
Note: Skip for cryptocurrencies.

### Risk Analysis
Use the **argent-risk-analyst** agent:
```
Perform risk analysis on {SYMBOL}:
- Annualized volatility
- Value at Risk (95%, 99%)
- Maximum drawdown
- Sharpe and Sortino ratios
- Position sizing recommendation
```

### Sentiment Analysis
Use the **argent-sentiment-analyst** agent:
```
Perform sentiment analysis on {SYMBOL}:
- Recent news headlines and tone
- Aggregate sentiment score
- Sentiment momentum
- Contrarian signals
```

### Macro Analysis
Use the **argent-macro-analyst** agent:
```
Analyze current macroeconomic environment:
- Economic cycle phase
- Fed policy stance
- Key indicators (rates, inflation, employment)
- Impact on stocks, bonds, crypto
```

## Output Format

Present a focused summary:
1. **Analysis Type** and Symbol
2. **Key Findings** (3-5 bullet points)
3. **Signal/Rating**
4. **One-liner Recommendation**

## Example Usage

```
/argent-quick AAPL technical
/argent-quick BTC risk
/argent-quick MSFT fundamental
/argent-quick SPY sentiment
/argent-quick macro
```
