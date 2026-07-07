# Economic Calendar Data Collector

A Python script that scrapes economic calendar data from TradingEconomics.com and exports it to JSON and CSV formats.

## Features

- Fetch economic events by timeframe (today, tomorrow, week, or month)
- Filter events by country code
- Export data to JSON and CSV formats
- SSL verification disabled for reliable scraping
- User-Agent spoofing to avoid blocking

## Installation

1. Install required dependencies:
```bash
pip install requests beautifulsoup4 urllib3
```

## Usage

### Basic Usage

Fetch this week's economic events:
```bash
python econ_calendar.py
```

### By Timeframe

```bash
# Today's events
python econ_calendar.py -t today

# Tomorrow's events
python econ_calendar.py -t tomorrow

# This week's events (default)
python econ_calendar.py -t week

# This month's events
python econ_calendar.py -t month
```

### Filter by Country Code

Filter for specific countries using their ISO country codes:
```bash
# US events only
python econ_calendar.py -c US

# Multiple countries
python econ_calendar.py -c US JP GB

# US and Japan for this month
python econ_calendar.py -t month -c US JP
```

### Filter by Impact Level

Filter events by their impact level (low, medium, high):
```bash
# High impact events only
python econ_calendar.py -i high

# Multiple impact levels
python econ_calendar.py -i high medium

# US high impact events for this month
python econ_calendar.py -t month -c US -i high

# UK and US high and medium impact events
python econ_calendar.py -c GB US -i high medium
```

### Output Options

```bash
# JSON output only (skip CSV)
python econ_calendar.py --json-only

# Combine with other options
python econ_calendar.py -t month -c US --json-only
```

## Output Files

- `output/economic_calendar.json` - Events in JSON format
- `output/economic_calendar.csv` - Events in CSV format

## Event Data Structure

Each event contains:
- `date` - Event date (YYYY-MM-DD)
- `time` - Event time (HH:MM AM/PM)
- `country_code` - ISO country code (e.g., US, JP, GB)
- `country` - Full country name
- `event` - Event name/description
- `impact` - Impact level (0=Low, 1=Medium, 2=High)
- `impact_label` - Human-readable impact level
- `actual` - Actual value (if released)
- `forecast` - Forecasted value
- `previous` - Previous value
- `category` - Event category

## Example Output

```json
[
  {
    "date": "2026-07-06",
    "time": "01:00 AM",
    "country_code": "AU",
    "country": "Australia",
    "event": "TD-MI Inflation Gauge MoM",
    "impact": 2,
    "impact_label": "High",
    "actual": "",
    "forecast": "0.1%",
    "previous": "0.2%",
    "category": "inflation"
  }
]
```

## Notes

- SSL verification is disabled to ensure reliable data collection
- The script uses a Chrome user agent to avoid being blocked
- Some events may have empty actual values if they haven't been released yet
