"""Check whether Google Flights (via SerpApi) can supply fresh fare paths.

Each Google Flights result has `price_insights.price_history`. If that is a
daily series of the cheapest fare going back weeks, one search per trip,
made just before departure, recovers the whole path that the 2022 data
needed 60 daily scrapes for. This script runs a few one-way searches, saves
the raw JSON, and reports what the history actually contains.

Needs a SerpApi key (free plan: 250 searches/month) in SERPAPI_KEY. Each
(route, days out) pair below costs one search.

Usage:
    python scripts/probe_serpapi.py
    python scripts/probe_serpapi.py --routes JFK-LAX ATL-BOS --days 3 30
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

DATA_DIR = Path(os.environ.get("FLIGHT_DATA_DIR", Path.home() / "data" / "flight-pricing"))
OUT_DIR = DATA_DIR / "serpapi" / "probe"
URL = "https://serpapi.com/search.json"


def search(key, origin, dest, flight_date):
    params = dict(engine="google_flights", type=2, departure_id=origin, arrival_id=dest,
                  outbound_date=flight_date.isoformat(), currency="USD", hl="en", api_key=key)
    r = requests.get(URL, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def describe(res):
    """Summarize price_history next to the cheapest fare currently listed."""
    flights = res.get("best_flights", []) + res.get("other_flights", [])
    prices = [f["price"] for f in flights if "price" in f]
    hist = res.get("price_insights", {}).get("price_history", [])
    out = {"listed_min": min(prices) if prices else None, "n_flights": len(flights),
           "lowest_price": res.get("price_insights", {}).get("lowest_price"),
           "history_points": len(hist)}
    if hist and all(len(h) == 2 for h in hist):
        days = [datetime.fromtimestamp(t, timezone.utc).date() for t, _ in hist]
        gaps = [(b - a).days for a, b in zip(days, days[1:])]
        out |= {"history_from": days[0].isoformat(), "history_to": days[-1].isoformat(),
                "max_gap_days": max(gaps) if gaps else None,
                "last_history_price": hist[-1][1], "distinct_prices": len({p for _, p in hist})}
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--routes", nargs="+", default=["JFK-LAX", "ATL-BOS", "JFK-LHR"])
    p.add_argument("--days", nargs="+", type=int, default=[3, 45])
    args = p.parse_args()

    key = os.environ.get("SERPAPI_KEY")
    if not key:
        sys.exit("Set SERPAPI_KEY (free key at https://serpapi.com/users/sign_up)")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"{len(args.routes) * len(args.days)} searches; raw JSON goes to {OUT_DIR}")
    for route in args.routes:
        origin, dest = route.split("-")
        for d in args.days:
            flight_date = date.today() + timedelta(days=d)
            res = search(key, origin, dest, flight_date)
            name = f"{origin}-{dest}_{flight_date}_searched-{date.today()}.json"
            (OUT_DIR / name).write_text(json.dumps(res, indent=1), encoding="utf-8")
            print(f"{route} {d:>3}d out ({flight_date}):", describe(res))


if __name__ == "__main__":
    main()
