#!/usr/bin/env python3

import csv
import sys
from datetime import datetime

from universe_loader import UniverseLoader


def ingest_underlyings(universe_file: str):
    print(f"[{datetime.now()}] Starting underlying ingestion from {universe_file}")

    rows = []

    # Expecting CSV with headers:
    # symbol,name,sector,industry,is_wheel_candidate
    with open(universe_file, "r") as f:
        reader = csv.DictReader(f)
        for line in reader:
            rows.append({
                "symbol": line["symbol"].upper(),
                "name": line.get("name"),
                "sector": line.get("sector"),
                "industry": line.get("industry"),
                "is_active": True,
                "is_wheel_candidate": line.get("is_wheel_candidate", "false").lower() == "true",
                "dividend_yield": None,
                "market_cap": None,
                "beta": None,
            })

    loader = UniverseLoader(
        dbname="tradewinds",
        user="tradewinds_user",
        password="YOUR_DB_PASSWORD",
        host="localhost"
    )

    try:
        loader.upsert_universe(rows)
        print(f"[{datetime.now()}] Underlyings ingestion complete. Rows upserted: {len(rows)}")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR during underlying ingestion: {e}")
    finally:
        loader.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ingest_underlyings.py PATH_TO_UNIVERSE_CSV")
        sys.exit(1)

    ingest_underlyings(sys.argv[1])

