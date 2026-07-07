---
name: econ-calendar
description: >-
  Economic calendar data from TradingEconomics.
  Use when: fetching economic events (NFP, CPI, PMI, GDP, central bank rates),
  filtering by country/impact, exporting calendar data to JSON/CSV, trading research.
argument-hint: "e.g., timeframe=week countries=US,JP impact=high"
user-invocable: true
---

# Economic Calendar Skill

Fetches global economic calendar data from TradingEconomics.com. Supports filtering by timeframe, country, and impact level.

## When to Use

- Get upcoming NFP, CPI, PMI, GDP releases
- Filter events by country (US, JP, GB, EU, etc.)
- Filter by impact level (high/medium/low)
- Export calendar data to JSON/CSV
- Research market-moving events

## Quick Start

From the project workspace:

```bash
# This week's events
uv run econ_calendar.py

# Today's high-impact US events
uv run econ_calendar.py -t today -c US -i high

# Monthly calendar, US + Japan, JSON only
uv run econ_calendar.py -t month -c US JP --json-only
```

## Timeframes

| Flag | Scope |
|------|-------|
| `-t today` | Today only |
| `-t tomorrow` | Next day |
| `-t week` | This week (default) |
| `-t month` | This month |

## Filters

- **Country**: `-c US JP GB` (ISO codes, space-separated)
- **Impact**: `-i high medium` (high/medium/low, space-separated)
- **Format**: `--json-only` (skip CSV)

## Output

- `output/economic_calendar.json`
- `output/economic_calendar.csv`

## Script Reference

Main script: [econ_calendar.py](../../econ_calendar.py)
MCP server: [econ_calendar_mcp.py](../../econ_calendar_mcp.py)
