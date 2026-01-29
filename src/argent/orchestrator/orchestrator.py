"""Main orchestrator for financial analysis workflow."""

from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from argent.agents.data_collection import DataCollectionAgent
from argent.agents.fundamental_analysis import FundamentalAnalysisAgent
from argent.agents.macro_analysis import MacroAnalysisAgent
from argent.agents.report import ReportAgent
from argent.agents.risk_analysis import RiskAnalysisAgent
from argent.agents.sentiment_analysis import SentimentAnalysisAgent
from argent.agents.technical_analysis import TechnicalAnalysisAgent
from argent.config import Settings, get_settings
from argent.orchestrator.state import AnalysisPhase, FinancialAnalysisState, TimeHorizon
from argent.tools.crypto_data import CryptoDataClient
from argent.tools.economic_data import EconomicDataClient
from argent.tools.market_data import MarketDataClient


@dataclass
class FinancialAdvisorOrchestrator:
    """
    Main coordinator for the multi-agent financial analysis system.

    Manages the workflow:
    1. Data Collection
    2. Parallel Analysis (Macro, Technical, Fundamental, Risk, Sentiment)
    3. Synthesis
    4. Report Generation
    """

    settings: Settings = field(default_factory=get_settings)
    console: Console = field(default_factory=Console)

    # Clients
    _anthropic: Anthropic | None = field(default=None, init=False)
    _market_client: MarketDataClient | None = field(default=None, init=False)
    _crypto_client: CryptoDataClient | None = field(default=None, init=False)
    _economic_client: EconomicDataClient | None = field(default=None, init=False)

    # Agents
    _data_agent: DataCollectionAgent | None = field(default=None, init=False)
    _macro_agent: MacroAnalysisAgent | None = field(default=None, init=False)
    _technical_agent: TechnicalAnalysisAgent | None = field(default=None, init=False)
    _fundamental_agent: FundamentalAnalysisAgent | None = field(default=None, init=False)
    _risk_agent: RiskAnalysisAgent | None = field(default=None, init=False)
    _sentiment_agent: SentimentAnalysisAgent | None = field(default=None, init=False)
    _report_agent: ReportAgent | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize clients and agents."""
        self._initialize_clients()
        self._initialize_agents()

    def _initialize_clients(self) -> None:
        """Initialize data clients."""
        self._anthropic = Anthropic(api_key=self.settings.anthropic_api_key)
        self._market_client = MarketDataClient(
            alpha_vantage_api_key=self.settings.alpha_vantage_api_key
        )
        self._crypto_client = CryptoDataClient()
        if self.settings.fred_api_key:
            self._economic_client = EconomicDataClient(api_key=self.settings.fred_api_key)

    def _initialize_agents(self) -> None:
        """Initialize analysis agents."""
        model = self.settings.model

        self._data_agent = DataCollectionAgent(
            client=self._anthropic,
            model=model,
            market_client=self._market_client,
            crypto_client=self._crypto_client,
            economic_client=self._economic_client,
        )

        self._macro_agent = MacroAnalysisAgent(client=self._anthropic, model=model)
        self._technical_agent = TechnicalAnalysisAgent(client=self._anthropic, model=model)
        self._fundamental_agent = FundamentalAnalysisAgent(
            client=self._anthropic,
            model=model,
            market_client=self._market_client,
        )
        self._risk_agent = RiskAnalysisAgent(client=self._anthropic, model=model)
        self._sentiment_agent = SentimentAnalysisAgent(client=self._anthropic, model=model)
        self._report_agent = ReportAgent(client=self._anthropic, model=model)

    def run_analysis(
        self,
        symbols: list[str],
        request: str = "",
        time_horizon: str = "medium",
        analysis_types: list[str] | None = None,
        show_progress: bool = True,
    ) -> FinancialAnalysisState:
        """
        Run comprehensive financial analysis.

        Args:
            symbols: List of symbols to analyze
            request: Original analysis request
            time_horizon: short, medium, or long
            analysis_types: List of analysis types or ["all"]
            show_progress: Whether to show progress indicators

        Returns:
            FinancialAnalysisState with all results
        """
        # Initialize state
        state = FinancialAnalysisState(
            analysis_request=request or f"Analyze {', '.join(symbols)}",
            symbols=[s.upper() for s in symbols],
            time_horizon=TimeHorizon(time_horizon),
            analysis_types=analysis_types or ["all"],
        )

        self.console.print(f"\n[bold blue]Starting analysis session: {state.session_id}[/bold blue]")
        self.console.print(f"Symbols: {', '.join(state.symbols)}")
        self.console.print(f"Time horizon: {state.time_horizon.value}\n")

        try:
            # Phase 1: Data Collection
            self._run_data_collection(state, show_progress)

            # Phase 2: Parallel Analysis
            self._run_analysis_phases(state, show_progress)

            # Phase 3: Report Generation
            self._run_report_generation(state, show_progress)

            state.current_phase = AnalysisPhase.COMPLETED

        except Exception as e:
            state.current_phase = AnalysisPhase.FAILED
            state.errors.append(str(e))
            self.console.print(f"[bold red]Analysis failed: {e}[/bold red]")

        return state

    def _run_data_collection(self, state: FinancialAnalysisState, show_progress: bool) -> None:
        """Run data collection phase."""
        state.start_phase(AnalysisPhase.DATA_COLLECTION)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            disable=not show_progress,
        ) as progress:
            task = progress.add_task("Collecting market data...", total=None)

            # Collect stock/ETF data
            for symbol in state.get_stock_symbols():
                progress.update(task, description=f"Fetching {symbol} data...")
                try:
                    prices = self._market_client.get_price_history(
                        symbol=symbol,
                        period=self._get_period_for_horizon(state.time_horizon),
                    )
                    state.add_price_data(
                        symbol,
                        [
                            {
                                "timestamp": p.timestamp.isoformat(),
                                "open": p.open,
                                "high": p.high,
                                "low": p.low,
                                "close": p.close,
                                "volume": p.volume,
                            }
                            for p in prices
                        ],
                    )

                    # Get company info
                    info = self._market_client.get_company_info(symbol)
                    state.add_company_data(symbol, {
                        "name": info.name,
                        "sector": info.sector,
                        "industry": info.industry,
                        "market_cap": info.market_cap,
                        "pe_ratio": info.pe_ratio,
                        "beta": info.beta,
                    })
                except Exception as e:
                    state.errors.append(f"Failed to fetch {symbol}: {e}")

            # Collect crypto data
            crypto_symbols = state.get_crypto_symbols()
            if crypto_symbols:
                progress.update(task, description="Fetching crypto data...")
                try:
                    crypto_prices = self._crypto_client.get_current_price(crypto_symbols)
                    state.crypto_data["current_prices"] = {
                        k: {
                            "price_usd": v.price_usd,
                            "market_cap": v.market_cap,
                            "volume_24h": v.volume_24h,
                            "price_change_24h": v.price_change_24h,
                        }
                        for k, v in crypto_prices.items()
                    }

                    # Get historical data for each crypto
                    for symbol in crypto_symbols:
                        history = self._crypto_client.get_price_history(symbol, days=365)
                        if history:
                            state.add_price_data(
                                symbol,
                                [
                                    {
                                        "timestamp": h["timestamp"].isoformat(),
                                        "open": h["price_usd"],
                                        "high": h["price_usd"],
                                        "low": h["price_usd"],
                                        "close": h["price_usd"],
                                        "volume": h.get("volume", 0),
                                    }
                                    for h in history
                                ],
                            )
                except Exception as e:
                    state.errors.append(f"Failed to fetch crypto data: {e}")

            # Collect economic data
            if self._economic_client:
                progress.update(task, description="Fetching economic indicators...")
                try:
                    state.economic_data = self._economic_client.get_macro_snapshot()
                except Exception as e:
                    state.errors.append(f"Failed to fetch economic data: {e}")

            # Collect SPY data for beta calculations if not already included
            if "SPY" not in state.price_data:
                progress.update(task, description="Fetching market benchmark...")
                try:
                    spy_prices = self._market_client.get_price_history("SPY", period="1y")
                    state.add_price_data(
                        "SPY",
                        [
                            {
                                "timestamp": p.timestamp.isoformat(),
                                "open": p.open,
                                "high": p.high,
                                "low": p.low,
                                "close": p.close,
                                "volume": p.volume,
                            }
                            for p in spy_prices
                        ],
                    )
                except Exception:
                    pass

        state.complete_phase(AnalysisPhase.DATA_COLLECTION)
        self.console.print("[green]✓ Data collection complete[/green]")

    def _run_analysis_phases(self, state: FinancialAnalysisState, show_progress: bool) -> None:
        """Run all analysis phases."""
        analyses = [
            (AnalysisPhase.MACRO_ANALYSIS, "Macro analysis", self._run_macro_analysis),
            (AnalysisPhase.TECHNICAL_ANALYSIS, "Technical analysis", self._run_technical_analysis),
            (AnalysisPhase.FUNDAMENTAL_ANALYSIS, "Fundamental analysis", self._run_fundamental_analysis),
            (AnalysisPhase.RISK_ANALYSIS, "Risk analysis", self._run_risk_analysis),
            (AnalysisPhase.SENTIMENT_ANALYSIS, "Sentiment analysis", self._run_sentiment_analysis),
        ]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            disable=not show_progress,
        ) as progress:
            for phase, description, run_fn in analyses:
                task = progress.add_task(f"Running {description}...", total=None)
                state.start_phase(phase)

                try:
                    run_fn(state)
                    state.complete_phase(phase)
                    progress.update(task, description=f"[green]✓ {description} complete[/green]")
                except Exception as e:
                    state.fail_phase(phase, str(e))
                    progress.update(task, description=f"[red]✗ {description} failed[/red]")

    def _run_macro_analysis(self, state: FinancialAnalysisState) -> None:
        """Run macro analysis."""
        result = self._macro_agent.analyze(
            economic_data=state.economic_data,
            symbols=state.symbols,
            time_horizon=state.time_horizon.value,
        )
        state.token_usage.add(result.input_tokens, result.output_tokens)
        if result.success:
            state.macro_analysis = result.data

    def _run_technical_analysis(self, state: FinancialAnalysisState) -> None:
        """Run technical analysis."""
        result = self._technical_agent.analyze(
            price_data=state.price_data,
            symbols=state.symbols,
        )
        state.token_usage.add(result.input_tokens, result.output_tokens)
        if result.success:
            state.technical_analysis = result.data

    def _run_fundamental_analysis(self, state: FinancialAnalysisState) -> None:
        """Run fundamental analysis."""
        stock_symbols = state.get_stock_symbols()
        if not stock_symbols:
            state.fundamental_analysis = {"message": "No stocks to analyze"}
            return

        result = self._fundamental_agent.analyze(
            company_data=state.company_data,
            symbols=stock_symbols,
        )
        state.token_usage.add(result.input_tokens, result.output_tokens)
        if result.success:
            state.fundamental_analysis = result.data

    def _run_risk_analysis(self, state: FinancialAnalysisState) -> None:
        """Run risk analysis."""
        result = self._risk_agent.analyze(
            price_data=state.price_data,
            symbols=state.symbols,
            time_horizon=state.time_horizon.value,
        )
        state.token_usage.add(result.input_tokens, result.output_tokens)
        if result.success:
            state.risk_analysis = result.data

    def _run_sentiment_analysis(self, state: FinancialAnalysisState) -> None:
        """Run sentiment analysis."""
        result = self._sentiment_agent.analyze(
            news_data=state.news_data,
            symbols=state.symbols,
        )
        state.token_usage.add(result.input_tokens, result.output_tokens)
        if result.success:
            state.sentiment_analysis = result.data

    def _run_report_generation(self, state: FinancialAnalysisState, show_progress: bool) -> None:
        """Generate final report."""
        state.start_phase(AnalysisPhase.REPORT)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            disable=not show_progress,
        ) as progress:
            task = progress.add_task("Generating report...", total=None)

            result = self._report_agent.generate_report(
                analysis_results=state.get_all_analysis_results(),
                symbols=state.symbols,
                time_horizon=state.time_horizon.value,
                request=state.analysis_request,
            )

            state.token_usage.add(result.input_tokens, result.output_tokens)

            if result.success:
                state.final_report = result.data
                state.report_text = self._report_agent.generate_text_report(result.data)

                # Extract recommendations
                if "recommendations" in result.data:
                    state.recommendations = result.data["recommendations"]

                progress.update(task, description="[green]✓ Report generated[/green]")
            else:
                progress.update(task, description="[red]✗ Report generation failed[/red]")

        state.complete_phase(AnalysisPhase.REPORT)

    def _get_period_for_horizon(self, horizon: TimeHorizon) -> str:
        """Get data period based on time horizon."""
        return {
            TimeHorizon.SHORT: "6mo",
            TimeHorizon.MEDIUM: "1y",
            TimeHorizon.LONG: "5y",
        }.get(horizon, "1y")

    def run_quick_analysis(
        self,
        symbol: str,
        analysis_type: str = "technical",
    ) -> dict[str, Any]:
        """
        Run a quick single-symbol analysis.

        Args:
            symbol: Symbol to analyze
            analysis_type: Type of analysis (technical, fundamental, risk)

        Returns:
            Analysis result dict
        """
        # Fetch price data
        prices = self._market_client.get_price_history(symbol, period="1y")
        price_data = {
            symbol: [
                {
                    "timestamp": p.timestamp.isoformat(),
                    "open": p.open,
                    "high": p.high,
                    "low": p.low,
                    "close": p.close,
                    "volume": p.volume,
                }
                for p in prices
            ]
        }

        if analysis_type == "technical":
            result = self._technical_agent.analyze(price_data, [symbol])
        elif analysis_type == "fundamental":
            info = self._market_client.get_company_info(symbol)
            result = self._fundamental_agent.analyze(
                {symbol: {"name": info.name, "sector": info.sector}},
                [symbol],
            )
        elif analysis_type == "risk":
            result = self._risk_agent.analyze(price_data, [symbol])
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}

        return result.data if result.success else {"error": result.error}
