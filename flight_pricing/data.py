"""Where the data lives and how to query it.

The dataset is too big for pandas (82M rows), so queries run in DuckDB against
the Parquet file and only the (small) results come back as DataFrames.
"""

import os
from pathlib import Path

import duckdb

DATA_DIR = Path(os.environ.get("FLIGHT_DATA_DIR", Path.home() / "data" / "flight-pricing"))
PARQUET = DATA_DIR / "processed" / "itineraries.parquet"
CHEAPEST = DATA_DIR / "processed" / "cheapest_daily.parquet"


def connect():
    """Return a DuckDB connection with views `itin` (every option) and, once
    built, `cheapest` (cheapest fare per route, flight date and search date)."""
    if not PARQUET.exists():
        raise FileNotFoundError(
            f"{PARQUET} not found; run scripts/download_data.py and scripts/build_parquet.py"
        )
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    con.execute(f"CREATE VIEW itin AS SELECT * FROM '{PARQUET.as_posix()}'")
    if CHEAPEST.exists():
        con.execute(f"CREATE VIEW cheapest AS SELECT * FROM '{CHEAPEST.as_posix()}'")
    return con
