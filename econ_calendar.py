"""
Economic Calendar Data Collector
Tarik data kalender ekonomi (NFP, PMI, CPI, dll) dari TradingEconomics.com
Output: JSON + CSV

Penggunaan:
    python econ_calendar.py                # minggu ini
    python econ_calendar.py -t today       # hari ini
    python econ_calendar.py -t month       # bulan ini
    python econ_calendar.py --json-only    # output JSON saja
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
}

# URL mapping per timeframe
URL_MAP = {
    "today": "https://tradingeconomics.com/calendar",
    "tomorrow": "https://tradingeconomics.com/calendar",
    "week": "https://tradingeconomics.com/calendar",
    "month": "https://tradingeconomics.com/calendar#monthly",
}

# Impact label dari class event-N
IMPACT_MAP = {0: "Low", 1: "Medium", 2: "High"}


def fetch_calendar(timeframe: str = "week", countries: list[str] | None = None, impact_levels: list[int] | None = None) -> list[dict]:
    """Fetch ekonomi kalender dari TradingEconomics."""
    url = URL_MAP.get(timeframe, URL_MAP["week"])
    resp = requests.get(url, headers=HEADERS, timeout=20, verify=False)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    cal = soup.select_one("table#calendar")
    if not cal:
        return []

    events = []
    current_date = ""

    for row in cal.select("tr"):
        tds = row.select("td")
        if not tds:
            continue

        # Baris tanggal (0 tds, pakai th)
        ths = row.select("th")
        if ths and not tds:
            text = ths[0].get_text(strip=True)
            # Bisa berupa tanggal atau header
            if re.match(r"\w+,\s+\w+\s+\d+", text):
                current_date = text
            continue

        if len(tds) < 5:
            continue

        event = _parse_row(row, current_date)
        if event:
            if countries:
                if event["country_code"].upper() not in [c.upper() for c in countries]:
                    continue
            if impact_levels is not None:
                if event["impact"] not in impact_levels:
                    continue
            events.append(event)

    return events


def _parse_row(row, current_date: str) -> dict | None:
    """Parse satu baris event dari HTML table TradingEconomics.

    Direct td layout (10 children, recursive=False):
      [0]=datetime  [1]=country  [2]=event  [3]=actual
      [4]=previous  [5]=forecast [6]=prev_revised
    """
    try:
        tds = row.find_all("td", recursive=False)
        if len(tds) < 7:
            return None

        # data-* attributes dari tr
        data_attr = {
            k.replace("data-", ""): v
            for k, v in row.attrs.items()
            if k.startswith("data-")
        }

        # --- [0] Tanggal & waktu ---
        date_td = tds[0]
        date_class = " ".join(date_td.get("class", []))
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", date_class)
        event_date = date_match.group(1) if date_match else current_date

        time_span = date_td.select_one("span")
        time_str = time_span.get_text(strip=True) if time_span else ""

        # Impact dari span class
        impact = 1  # default Low
        if time_span:
            span_classes = " ".join(time_span.get("class", []))
            m = re.search(r"event-(\d)", span_classes)
            if m:
                impact = int(m.group(1))

        # --- [1] Country ---
        country_td = tds[1]
        iso_el = country_td.select_one("td.calendar-iso")
        country_code = iso_el.get_text(strip=True) if iso_el else ""
        flag_el = country_td.select_one("div.flag")
        country = flag_el.get("title", "") if flag_el else ""

        # --- [2] Event name ---
        event_link = tds[2].select_one("a.calendar-event")
        event_name = (
            event_link.get_text(strip=True)
            if event_link
            else tds[2].get_text(strip=True)
        )

        # Actual / Forecast / Previous (direct tds[3]=actual, [4]=prev, [5]=forecast)
        def _val(idx):
            return tds[idx].get_text(strip=True) if idx < len(tds) else ""

        actual = _val(3)
        previous = _val(4)
        forecast = _val(5)

        return {
            "date": event_date,
            "time": time_str,
            "country_code": country_code,
            "country": country,
            "event": event_name,
            "impact": impact,
            "impact_label": IMPACT_MAP.get(impact, "Low"),
            "actual": actual,
            "forecast": forecast,
            "previous": previous,
            "category": data_attr.get("category", ""),
        }
    except Exception:
        return None


def save_json(events: list[dict], filepath: str = "output/economic_calendar.json"):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"[ok] JSON -> {filepath} ({len(events)} events)")


def save_csv(events: list[dict], filepath: str = "output/economic_calendar.csv"):
    if not events:
        return
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    keys = events[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(events)
    print(f"[ok] CSV  -> {filepath} ({len(events)} events)")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Tarik data ekonomi kalender")
    parser.add_argument(
        "-t", "--timeframe",
        choices=["today", "tomorrow", "week", "month"],
        default="week",
        help="Timeframe (default: week)",
    )
    parser.add_argument(
        "-c", "--countries",
        nargs="+",
        default=None,
        help="Filter by country code(s), e.g., US JP GB (default: all countries)",
    )
    parser.add_argument(
        "-i", "--impact",
        nargs="+",
        choices=["low", "medium", "high"],
        default=None,
        help="Filter by impact level(s), e.g., high medium (default: all impacts)",
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Output JSON only (skip CSV)",
    )
    args = parser.parse_args()

    # Convert impact level names to numbers (0=Low, 1=Medium, 2=High)
    impact_map = {"low": 0, "medium": 1, "high": 2}
    impact_levels = None
    if args.impact:
        impact_levels = [impact_map[level.lower()] for level in args.impact]

    filter_info = ""
    if args.countries:
        filter_info += f" | Countries: {', '.join(args.countries)}"
    if args.impact:
        filter_info += f" | Impact: {', '.join([level.capitalize() for level in args.impact])}"
    
    print(f"[...] Fetching economic calendar ({args.timeframe}){filter_info}...")
    events = fetch_calendar(args.timeframe, args.countries, impact_levels)

    if not events:
        print("[!] No data found. Try running with VPN or wait a few minutes.")
        return

    print(f"[ok] Found {len(events)} events\n")

    # Preview 10 event pertama
    print("--- Preview ---")
    for e in events[:10]:
        print(
            "  %s %s | %s %-3s | %-6s | %s"
            % (e["date"], e["time"], e["country_code"], "", e["impact_label"], e["event"])
        )
    print()

    save_json(events)
    if not args.json_only:
        save_csv(events)


if __name__ == "__main__":
    main()
