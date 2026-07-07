"""
Economic Calendar MCP Server
Exposes TradingEconomics calendar data as MCP tools for AI agents.

Usage:
    uv run econ_calendar_mcp.py
    # or: python econ_calendar_mcp.py

Configure in VS Code: .vscode/mcp.json
"""

import json
import sys
from pathlib import Path

# Ensure sibling import works when run as script or MCP server
sys.path.insert(0, str(Path(__file__).parent))
from econ_calendar import fetch_calendar, IMPACT_MAP

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("MCP SDK not found. Install: uv pip install 'mcp[cli]'", file=sys.stderr)
    sys.exit(1)

# --- MCP Server ---
mcp = FastMCP("economic-calendar", log_level="ERROR")

@mcp.tool(
    name="get_economic_calendar",
    description="Fetch global economic calendar events (NFP, PMI, CPI, central bank rates, etc.) from TradingEconomics. Returns upcoming events by timeframe, country, and impact level."
)
def get_economic_calendar(
    timeframe: str = "week",
    countries: list[str] | None = None,
    impact: list[str] | None = None,
) -> str:
    """
    Args:
        timeframe: 'today', 'tomorrow', 'week', or 'month'
        countries: Filter by ISO country codes, e.g. ['US', 'JP', 'GB']
        impact: Filter by impact level, e.g. ['high', 'medium']
    Returns:
        JSON string of calendar events
    """
    impact_map = {"low": 0, "medium": 1, "high": 2}
    impact_levels = [impact_map[lvl.lower()] for lvl in impact] if impact else None

    events = fetch_calendar(
        timeframe=timeframe,
        countries=countries,
        impact_levels=impact_levels,
    )
    return json.dumps(events, ensure_ascii=False, indent=2)

@mcp.tool(
    name="get_high_impact_events",
    description="Quick tool to get only high-impact economic events for a given timeframe. Useful for trading news analysis."
)
def get_high_impact_events(
    timeframe: str = "week",
    countries: list[str] | None = None,
) -> str:
    """
    Args:
        timeframe: 'today', 'tomorrow', 'week', or 'month'
        countries: Filter by ISO country codes, e.g. ['US', 'JP', 'GB']
    Returns:
        JSON string of high-impact events only
    """
    return get_economic_calendar(timeframe=timeframe, countries=countries, impact=["high"])


def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
