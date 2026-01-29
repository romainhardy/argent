"""CLI entry point for Argent financial advisor."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from argent import __version__
from argent.config import get_settings
from argent.orchestrator import FinancialAdvisorOrchestrator


console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """Argent - Multi-agent Financial Advisor

    A sophisticated multi-agent system for comprehensive financial analysis.
    """
    pass


@cli.command()
@click.option(
    "--symbols", "-s",
    required=True,
    help="Comma-separated list of symbols to analyze (e.g., AAPL,MSFT,BTC)",
)
@click.option(
    "--horizon", "-h",
    type=click.Choice(["short", "medium", "long"]),
    default="medium",
    help="Investment time horizon",
)
@click.option(
    "--type", "-t",
    "analysis_type",
    type=click.Choice(["all", "technical", "fundamental", "risk", "sentiment"]),
    default="all",
    help="Type of analysis to run",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path for the report (optional)",
)
@click.option(
    "--json-output",
    is_flag=True,
    help="Output raw JSON instead of formatted report",
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    help="Suppress progress output",
)
def analyze(symbols: str, horizon: str, analysis_type: str, output: str | None, json_output: bool, quiet: bool):
    """Run comprehensive financial analysis on specified symbols.

    Examples:

        argent analyze --symbols AAPL,MSFT --horizon medium

        argent analyze --symbols BTC,ETH --type technical

        argent analyze --symbols SPY --output report.md
    """
    try:
        settings = get_settings()
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        console.print("Please ensure ANTHROPIC_API_KEY is set in your environment or .env file")
        sys.exit(1)

    symbol_list = [s.strip().upper() for s in symbols.split(",")]

    if not quiet:
        console.print(Panel.fit(
            f"[bold]Argent Financial Advisor[/bold]\n"
            f"Analyzing: {', '.join(symbol_list)}\n"
            f"Horizon: {horizon}\n"
            f"Analysis: {analysis_type}",
            title="Analysis Request",
        ))

    # Initialize orchestrator
    orchestrator = FinancialAdvisorOrchestrator(settings=settings, console=console)

    # Run analysis
    state = orchestrator.run_analysis(
        symbols=symbol_list,
        time_horizon=horizon,
        analysis_types=[analysis_type] if analysis_type != "all" else ["all"],
        show_progress=not quiet,
    )

    # Output results
    if json_output:
        result = {
            "session_id": state.session_id,
            "symbols": state.symbols,
            "macro_analysis": state.macro_analysis,
            "technical_analysis": state.technical_analysis,
            "fundamental_analysis": state.fundamental_analysis,
            "risk_analysis": state.risk_analysis,
            "sentiment_analysis": state.sentiment_analysis,
            "recommendations": state.recommendations,
            "report": state.final_report,
        }
        if output:
            Path(output).write_text(json.dumps(result, indent=2, default=str))
            console.print(f"\n[green]JSON report saved to: {output}[/green]")
        else:
            console.print_json(data=result)
    else:
        # Print formatted report
        if state.report_text:
            console.print("\n")
            console.print(state.report_text)

            if output:
                Path(output).write_text(state.report_text)
                console.print(f"\n[green]Report saved to: {output}[/green]")
        else:
            console.print("[yellow]No report generated. Check errors above.[/yellow]")

    # Print summary
    if not quiet:
        summary = state.get_progress_summary()
        console.print(f"\n[dim]Session: {summary['session_id']} | "
                     f"Tokens: {summary['token_usage']['total']:,}[/dim]")

        if state.errors:
            console.print(f"[yellow]Warnings: {len(state.errors)} issues encountered[/yellow]")


@cli.command()
@click.option(
    "--symbol", "-s",
    required=True,
    help="Symbol to analyze",
)
@click.option(
    "--type", "-t",
    "analysis_type",
    type=click.Choice(["technical", "fundamental", "risk"]),
    default="technical",
    help="Type of quick analysis",
)
def quick(symbol: str, analysis_type: str):
    """Run quick single-symbol analysis.

    Examples:

        argent quick --symbol AAPL --type technical

        argent quick --symbol MSFT --type fundamental
    """
    try:
        settings = get_settings()
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)

    console.print(f"[bold]Quick {analysis_type} analysis for {symbol.upper()}[/bold]\n")

    orchestrator = FinancialAdvisorOrchestrator(settings=settings, console=console)

    with console.status(f"Analyzing {symbol}..."):
        result = orchestrator.run_quick_analysis(symbol.upper(), analysis_type)

    if "error" in result:
        console.print(f"[red]Error: {result['error']}[/red]")
    else:
        console.print_json(data=result)


@cli.command()
def config():
    """Show current configuration."""
    try:
        settings = get_settings()

        table = Table(title="Argent Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")

        # API Keys
        table.add_row(
            "Anthropic API Key",
            "****" + settings.anthropic_api_key[-4:] if settings.anthropic_api_key else "Not set",
            "✓" if settings.anthropic_api_key else "✗ Required",
        )
        table.add_row(
            "Alpha Vantage Key",
            "****" + settings.alpha_vantage_api_key[-4:] if settings.alpha_vantage_api_key else "Not set",
            "✓" if settings.alpha_vantage_api_key else "○ Optional",
        )
        table.add_row(
            "FRED API Key",
            "****" + settings.fred_api_key[-4:] if settings.fred_api_key else "Not set",
            "✓" if settings.fred_api_key else "○ Optional",
        )

        # Model config
        table.add_row("Default Model", settings.model, "")
        table.add_row("Fast Model", settings.fast_model, "")

        # Database
        table.add_row("Database URL", settings.database_url, "")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        console.print("\nMake sure you have a .env file with ANTHROPIC_API_KEY set.")


@cli.command()
@click.argument("symbol")
def price(symbol: str):
    """Get current price for a symbol.

    Example:

        argent price AAPL
    """
    from argent.tools.market_data import MarketDataClient
    from argent.tools.crypto_data import CryptoDataClient

    symbol = symbol.upper()
    crypto_symbols = {"BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE"}

    if symbol in crypto_symbols:
        client = CryptoDataClient()
        prices = client.get_current_price([symbol])
        if symbol in prices:
            p = prices[symbol]
            console.print(f"[bold]{symbol}[/bold]: ${p.price_usd:,.2f}")
            console.print(f"24h Change: {p.price_change_24h:+.2f}%")
            console.print(f"Market Cap: ${p.market_cap:,.0f}")
        else:
            console.print(f"[red]Could not fetch price for {symbol}[/red]")
    else:
        client = MarketDataClient()
        info = client.get_current_price(symbol)
        if info.get("current_price"):
            console.print(f"[bold]{symbol}[/bold]: ${info['current_price']:,.2f}")
            if info.get("previous_close"):
                change = (info["current_price"] / info["previous_close"] - 1) * 100
                console.print(f"Day Change: {change:+.2f}%")
            if info.get("market_cap"):
                console.print(f"Market Cap: ${info['market_cap']:,.0f}")
        else:
            console.print(f"[red]Could not fetch price for {symbol}[/red]")


@cli.command()
def list_indicators():
    """List available economic indicators (FRED series)."""
    from argent.tools.economic_data import FRED_SERIES

    table = Table(title="Available FRED Economic Indicators")
    table.add_column("Series ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Frequency", style="yellow")

    for series_id, info in sorted(FRED_SERIES.items()):
        table.add_row(series_id, info["name"], info["frequency"])

    console.print(table)
    console.print("\n[dim]Note: FRED API key required to fetch economic data[/dim]")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
