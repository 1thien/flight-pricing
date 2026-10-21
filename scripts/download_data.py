"""Download the Kaggle "Flight Prices" dataset (Expedia, ~82M one-way US fares, 2022).

Needs Kaggle credentials: run `kaggle auth login` once, or put an API token in
~/.kaggle/access_token.

The data is ~31 GB unzipped, so it lives outside the repo (and outside OneDrive)
by default. Set FLIGHT_DATA_DIR to put it somewhere else.

Usage:
    python scripts/download_data.py
"""

import os
import sys
from pathlib import Path

DATASET = "dilwong/flightprices"
DATA_DIR = Path(os.environ.get("FLIGHT_DATA_DIR", Path.home() / "data" / "flight-pricing"))
RAW_DIR = DATA_DIR / "raw"


def main():
    if (RAW_DIR / "itineraries.csv").exists():
        print(f"Already downloaded: {RAW_DIR / 'itineraries.csv'}")
        return

    # Imported here because importing kaggle tries to authenticate immediately.
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {DATASET} to {RAW_DIR} (~5.6 GB zipped, ~31 GB unzipped)...")
    api.dataset_download_files(DATASET, path=RAW_DIR, unzip=True, quiet=False)

    csv = RAW_DIR / "itineraries.csv"
    if not csv.exists():
        sys.exit(f"Download finished but {csv} is missing; check {RAW_DIR}")
    print(f"Done: {csv} ({csv.stat().st_size / 1e9:.1f} GB)")


if __name__ == "__main__":
    main()
