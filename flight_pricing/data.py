"""Where the data lives and how to query it.

The dataset is too big for pandas (82M rows), so queries run in DuckDB against
the Parquet file and only the (small) results come back as DataFrames.
"""

import os
from pathlib import Path

import duckdb

DATA_DIR = Path(os.environ.get("FLIGHT_DATA_DIR", Path.home() / "data" / "flight-pricing"))
PARQUET = DATA_DIR / "processed" / "itineraries.parquet"


def connect():
    """Return a DuckDB connection with the full dataset available as the view `itin`."""
    if not PARQUET.exists():
        raise FileNotFoundError(
            f"{PARQUET} not found; run scripts/download_data.py and scripts/build_parquet.py"
        )
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    con.execute(f"CREATE VIEW itin AS SELECT * FROM '{PARQUET.as_posix()}'")
    return con
