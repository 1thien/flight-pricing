"""Build the core table: the cheapest fare per route, flight date and search date.

This is what a traveler searching "cheapest A to B on date D" would have seen
each day (decision D5). Basic economy is included. Attributes of the cheapest
option (itinerary, nonstop, basic economy, airline, seats left) come along so
later notebooks can see when the cheapest option switches itinerary.

Usage:
    python scripts/build_cheapest.py
"""

import os
import sys
from pathlib import Path

import duckdb

DATA_DIR = Path(os.environ.get("FLIGHT_DATA_DIR", Path.home() / "data" / "flight-pricing"))
SRC = DATA_DIR / "processed" / "itineraries.parquet"
OUT = DATA_DIR / "processed" / "cheapest_daily.parquet"


def main():
    if not SRC.exists():
        sys.exit(f"{SRC} not found; run scripts/build_parquet.py first")

    con = duckdb.connect()
    con.execute(f"SET temp_directory = '{(DATA_DIR / 'duckdb_tmp').as_posix()}'")
    print(f"Building {OUT}...")
    con.execute(f"""
        COPY (
            SELECT startingAirport AS origin,
                   destinationAirport AS dest,
                   flightDate,
                   searchDate,
                   datediff('day', searchDate, flightDate) AS days_ahead,
                   min(totalFare) AS fare,
                   count(*) AS n_options,
                   arg_min(legId, totalFare) AS legId,
                   arg_min(isNonStop, totalFare) AS isNonStop,
                   arg_min(isBasicEconomy, totalFare) AS isBasicEconomy,
                   arg_min(segmentsAirlineName, totalFare) AS airlines,
                   arg_min(seatsRemaining, totalFare) AS seatsRemaining
            FROM '{SRC.as_posix()}'
            GROUP BY ALL
            ORDER BY origin, dest, flightDate, searchDate
        ) TO '{OUT.as_posix()}' (FORMAT parquet, COMPRESSION zstd)
    """)

    rows, trips = con.execute(
        f"SELECT count(*), count(DISTINCT (origin, dest, flightDate)) FROM '{OUT.as_posix()}'"
    ).fetchone()
    print(f"Done: {rows:,} rows covering {trips:,} route-date trips, "
          f"{OUT.stat().st_size / 1e6:.0f} MB")


if __name__ == "__main__":
    main()
