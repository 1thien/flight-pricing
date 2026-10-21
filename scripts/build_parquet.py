"""Convert itineraries.csv to Parquet so it can be queried without loading 31 GB into memory.

Rows are sorted by searchDate so walk-forward splits by search date read
contiguous data.

Usage:
    python scripts/build_parquet.py
"""

import os
import sys
from pathlib import Path

import duckdb

DATA_DIR = Path(os.environ.get("FLIGHT_DATA_DIR", Path.home() / "data" / "flight-pricing"))
CSV = DATA_DIR / "raw" / "itineraries.csv"
OUT = DATA_DIR / "processed" / "itineraries.parquet"


def main():
    if not CSV.exists():
        sys.exit(f"{CSV} not found; run scripts/download_data.py first")
    OUT.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    # Spill to disk next to the data instead of the default temp location.
    con.execute(f"SET temp_directory = '{(DATA_DIR / 'duckdb_tmp').as_posix()}'")
    print(f"Converting {CSV} -> {OUT} (takes a while)...")
    con.execute(f"""
        COPY (
            SELECT *
            FROM read_csv('{CSV.as_posix()}', header = true, delim = ',', quote = '"')
            ORDER BY searchDate
        ) TO '{OUT.as_posix()}' (FORMAT parquet, COMPRESSION zstd)
    """)

    rows, start, end = con.execute(
        f"SELECT count(*), min(searchDate), max(searchDate) FROM '{OUT.as_posix()}'"
    ).fetchone()
    print(f"Done: {rows:,} rows, search dates {start} to {end}, "
          f"{OUT.stat().st_size / 1e9:.1f} GB")


if __name__ == "__main__":
    main()
