"""Macro analysis agent for economic environment assessment using rule-based analysis."""

from dataclasses import dataclass
from typing import Any

from argent.agents.base import AgentResult, FinancialAgentType


@dataclass
class MacroAnalysisAgent:
    """Agent responsible for macroeconomic analysis using rule-based methods."""

    @property
    def agent_type(self) -> FinancialAgentType:
        return FinancialAgentType.MACRO_ANALYSIS

    def _assess_economic_cycle(self, economic_data: dict[str, Any]) -> dict[str, Any]:
        """Assess current economic cycle phase based on indicators."""
        gdp_growth = economic_data.get("gdp_growth", {}).get("value")
        unemployment = economic_data.get("unemployment", {}).get("value")
        inflation = economic_data.get("inflation", {}).get("value")

        evidence = []
        score = 0

        # GDP growth assessment
        if gdp_growth is not None:
            if gdp_growth > 3:
                evidence.append(f"Strong GDP growth at {gdp_growth:.1f}%")
                score += 2
            elif gdp_growth > 1.5:
                evidence.append(f"Moderate GDP growth at {gdp_growth:.1f}%")
                score += 1
            elif gdp_growth > 0:
                evidence.append(f"Weak GDP growth at {gdp_growth:.1f}%")
            else:
                evidence.append(f"GDP contraction at {gdp_growth:.1f}%")
                score -= 2

        # Unemployment assessment
        if unemployment is not None:
            if unemployment < 4:
                evidence.append(f"Low unemployment at {unemployment:.1f}%")
                score += 1
            elif unemployment < 6:
                evidence.append(f"Moderate unemployment at {unemployment:.1f}%")
            else:
                evidence.append(f"High unemployment at {unemployment:.1f}%")
                score -= 1

        # Determine phase
        if score >= 2:
            phase = "expansion"
            outlook_months = 12
        elif score >= 0:
            phase = "peak" if gdp_growth and gdp_growth > 2 else "trough"
            outlook_months = 6
        else:
            phase = "contraction"
            outlook_months = 9

        confidence = "high" if len(evidence) >= 3 else "medium" if len(evidence) >= 2 else "low"

        return {
            "phase": phase,
            "confidence": confidence,
            "evidence": evidence,
            "outlook_months": outlook_months,
        }

    def _assess_monetary_policy(self, economic_data: dict[str, Any]) -> dict[str, Any]:
        """Assess monetary policy stance based on Fed funds rate and inflation."""
        fed_funds = economic_data.get("fed_funds_rate", {}).get("value")
        inflation = economic_data.get("inflation", {}).get("value")
        treasury_10y = economic_data.get("treasury_10y", {}).get("value")

        if fed_funds is None:
            return {
                "stance": "unknown",
                "rate_outlook": "stable",
                "implications": "Unable to assess without Fed funds rate data",
            }

        # Determine stance based on real rates and inflation
        real_rate = (fed_funds - inflation) if inflation else fed_funds

        if real_rate > 2:
            stance = "hawkish"
            rate_outlook = "stable" if inflation and inflation < 3 else "rising"
            implications = "Tight monetary policy may constrain growth. Favors value over growth stocks."
        elif real_rate > 0:
            stance = "neutral"
            rate_outlook = "stable"
            implications = "Balanced monetary policy. Market-neutral conditions."
        else:
            stance = "dovish"
            rate_outlook = "falling" if inflation and inflation < 2 else "stable"
            implications = "Accommodative policy supports risk assets. Favors growth stocks."

        return {
            "stance": stance,
            "rate_outlook": rate_outlook,
            "fed_funds_rate": fed_funds,
            "real_rate": real_rate,
            "implications": implications,
        }

    def _assess_inflation(self, economic_data: dict[str, Any]) -> dict[str, Any]:
        """Assess inflation environment."""
        inflation = economic_data.get("inflation", {}).get("value")

        if inflation is None:
            return {
                "trend": "unknown",
                "current_rate": None,
                "outlook": "Unable to assess without inflation data",
            }

        if inflation > 4:
            trend = "rising"
            outlook = "High inflation erodes purchasing power. Consider inflation hedges like commodities, TIPS, or real assets."
        elif inflation > 2.5:
            trend = "stable"
            outlook = "Inflation elevated but manageable. Monitor for persistence."
        elif inflation > 1.5:
            trend = "stable"
            outlook = "Inflation near target. Supportive of economic growth."
        else:
            trend = "falling"
            outlook = "Low inflation may indicate weak demand. Watch for deflation risks."

        return {
            "trend": trend,
            "current_rate": inflation,
            "outlook": outlook,
        }

    def _assess_growth(self, economic_data: dict[str, Any]) -> dict[str, Any]:
        """Assess growth and employment conditions."""
        gdp_growth = economic_data.get("gdp_growth", {}).get("value")
        unemployment = economic_data.get("unemployment", {}).get("value")

        # GDP assessment
        if gdp_growth is not None:
            if gdp_growth > 3:
                gdp_trend = "accelerating"
            elif gdp_growth > 1:
                gdp_trend = "stable"
            else:
                gdp_trend = "decelerating"
        else:
            gdp_trend = "unknown"

        # Employment assessment
        if unemployment is not None:
            if unemployment < 4:
                employment = "strong"
                consumer_outlook = "Strong labor market supports consumer spending."
            elif unemployment < 6:
                employment = "moderate"
                consumer_outlook = "Labor market stable but not exceptional."
            else:
                employment = "weak"
                consumer_outlook = "High unemployment may constrain consumer spending."
        else:
            employment = "unknown"
            consumer_outlook = "Unable to assess without unemployment data."

        return {
            "gdp_trend": gdp_trend,
            "gdp_growth": gdp_growth,
            "employment": employment,
            "unemployment": unemployment,
            "consumer_outlook": consumer_outlook,
        }

    def _assess_market_conditions(self, economic_data: dict[str, Any]) -> dict[str, Any]:
        """Assess market risk appetite and conditions."""
        vix = economic_data.get("vix", {}).get("value")
        sp500_pe = economic_data.get("sp500_pe", {}).get("value")

        # VIX assessment
        if vix is not None:
            if vix < 15:
                vix_level = "low"
                risk_appetite = "risk-on"
            elif vix < 20:
                vix_level = "moderate"
                risk_appetite = "neutral"
            elif vix < 30:
                vix_level = "elevated"
                risk_appetite = "risk-off"
            else:
                vix_level = "high"
                risk_appetite = "risk-off"
        else:
            vix_level = "unknown"
            risk_appetite = "neutral"

        # Market valuation sentiment
        if sp500_pe is not None:
            if sp500_pe > 25:
                sentiment = "bullish"  # High valuations indicate optimism
            elif sp500_pe > 18:
                sentiment = "neutral"
            else:
                sentiment = "bearish"  # Low valuations may indicate fear
        else:
            sentiment = "neutral"

        return {
            "risk_appetite": risk_appetite,
            "vix_level": vix_level,
            "vix_value": vix,
            "sentiment": sentiment,
            "sp500_pe": sp500_pe,
        }

    def _assess_asset_implications(
        self,
        cycle: dict[str, Any],
        monetary: dict[str, Any],
        inflation: dict[str, Any],
        growth: dict[str, Any],
        market: dict[str, Any],
    ) -> dict[str, Any]:
        """Determine implications for different asset classes."""
        # Stock outlook
        stock_score = 0
        if cycle["phase"] in ["expansion"]:
            stock_score += 2
        elif cycle["phase"] == "peak":
            stock_score += 1
        elif cycle["phase"] == "contraction":
            stock_score -= 2

        if monetary["stance"] == "dovish":
            stock_score += 1
        elif monetary["stance"] == "hawkish":
            stock_score -= 1

        if market["risk_appetite"] == "risk-on":
            stock_score += 1
        elif market["risk_appetite"] == "risk-off":
            stock_score -= 1

        stock_outlook = (
            "favorable" if stock_score >= 2 else
            "neutral" if stock_score >= 0 else
            "unfavorable"
        )

        # Bond outlook (inverse relationship with rates)
        bond_score = 0
        if monetary["rate_outlook"] == "falling":
            bond_score += 2
        elif monetary["rate_outlook"] == "rising":
            bond_score -= 2

        if inflation["trend"] == "falling":
            bond_score += 1
        elif inflation["trend"] == "rising":
            bond_score -= 1

        bond_outlook = (
            "favorable" if bond_score >= 1 else
            "neutral" if bond_score >= -1 else
            "unfavorable"
        )

        # Crypto outlook (risk asset, correlates with risk appetite)
        crypto_score = 0
        if market["risk_appetite"] == "risk-on":
            crypto_score += 2
        elif market["risk_appetite"] == "risk-off":
            crypto_score -= 2

        if monetary["stance"] == "dovish":
            crypto_score += 1
        elif monetary["stance"] == "hawkish":
            crypto_score -= 1

        crypto_outlook = (
            "favorable" if crypto_score >= 1 else
            "neutral" if crypto_score >= -1 else
            "unfavorable"
        )

        # Sector recommendations based on cycle
        if cycle["phase"] == "expansion":
            recommended_sectors = ["Technology", "Consumer Discretionary", "Industrials"]
        elif cycle["phase"] == "peak":
            recommended_sectors = ["Energy", "Materials", "Financials"]
        elif cycle["phase"] == "contraction":
            recommended_sectors = ["Utilities", "Consumer Staples", "Healthcare"]
        else:  # trough
            recommended_sectors = ["Financials", "Real Estate", "Consumer Discretionary"]

        return {
            "stocks": {"outlook": stock_outlook, "score": stock_score},
            "bonds": {"outlook": bond_outlook, "score": bond_score},
            "crypto": {"outlook": crypto_outlook, "score": crypto_score},
            "recommended_sectors": recommended_sectors,
        }

    def _identify_key_risks(
        self,
        cycle: dict[str, Any],
        monetary: dict[str, Any],
        inflation: dict[str, Any],
        market: dict[str, Any],
    ) -> list[str]:
        """Identify key macroeconomic risks."""
        risks = []

        if cycle["phase"] == "peak":
            risks.append("Economic cycle may be peaking - watch for slowdown signals")

        if cycle["phase"] == "contraction":
            risks.append("Economic contraction underway - recession risk elevated")

        if monetary["stance"] == "hawkish":
            risks.append("Tight monetary policy may constrain growth and valuations")

        if inflation["trend"] == "rising" and inflation.get("current_rate", 0) > 3:
            risks.append(f"Elevated inflation at {inflation['current_rate']:.1f}% may persist")

        if market["vix_level"] in ["elevated", "high"]:
            risks.append("Elevated market volatility indicates uncertainty")

        if market.get("sp500_pe") and market["sp500_pe"] > 25:
            risks.append("High market valuations increase correction risk")

        if not risks:
            risks.append("No significant macro risks identified at this time")

        return risks

    def _generate_summary(
        self,
        cycle: dict[str, Any],
        assets: dict[str, Any],
        risks: list[str],
    ) -> str:
        """Generate a summary of macro conditions."""
        phase = cycle["phase"]
        stock_outlook = assets["stocks"]["outlook"]
        sectors = ", ".join(assets["recommended_sectors"][:3])

        summary = f"Economy is in {phase} phase. "
        summary += f"Stock market outlook is {stock_outlook}. "
        summary += f"Recommended sectors: {sectors}. "
        summary += f"Key risk: {risks[0]}" if risks else ""

        return summary

    def analyze(
        self,
        economic_data: dict[str, Any],
        symbols: list[str],
        time_horizon: str = "medium",
    ) -> AgentResult:
        """
        Analyze macroeconomic environment using rule-based methods.

        Args:
            economic_data: Collected economic indicators
            symbols: Symbols being analyzed
            time_horizon: Investment time horizon

        Returns:
            AgentResult with macro analysis
        """
        # Assess each component
        cycle = self._assess_economic_cycle(economic_data)
        monetary = self._assess_monetary_policy(economic_data)
        inflation = self._assess_inflation(economic_data)
        growth = self._assess_growth(economic_data)
        market = self._assess_market_conditions(economic_data)

        # Determine asset implications
        assets = self._assess_asset_implications(cycle, monetary, inflation, growth, market)

        # Identify risks
        risks = self._identify_key_risks(cycle, monetary, inflation, market)

        # Generate summary
        summary = self._generate_summary(cycle, assets, risks)

        results = {
            "economic_cycle": cycle,
            "monetary_policy": monetary,
            "inflation": inflation,
            "growth": growth,
            "market_conditions": market,
            "asset_implications": assets,
            "key_risks": risks,
            "summary": summary,
            "time_horizon": time_horizon,
            "symbols_analyzed": symbols,
        }

        return AgentResult(
            success=True,
            data=results,
            error=None,
        )
