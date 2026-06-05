#!/usr/bin/env python3

import argparse
import csv
import getpass
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.config import get_db_config
from data.loaders.universe_loader import UniverseLoader


def parse_args() -> argparse.Namespace:
    db_config = get_db_config()

    parser = argparse.ArgumentParser(
        description="Load universe metadata into the tradewinds database from a CSV file.",
        epilog=(
            "CSV headers must include: symbol,name,sector,industry,is_wheel_candidate"
        ),
    )
    parser.add_argument("csv_file", help="Path to the input universe CSV file")
    parser.add_argument("--dbname", default=db_config["dbname"], help="Postgres database name")
    parser.add_argument("--user", default=db_config["user"], help="Postgres user")
    parser.add_argument("--password", default=db_config["password"], required=not bool(db_config["password"]),
                        help="Postgres password")
    parser.add_argument("--host", default=db_config["host"], help="Postgres host")
    parser.add_argument("--port", default=db_config["port"], help="Postgres port")
    return parser.parse_args()


def load_csv_rows(csv_file: str) -> list[dict]:
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            {
                "symbol": line["symbol"].upper(),
                "name": line.get("name"),
                "sector": line.get("sector"),
                "industry": line.get("industry"),
                "is_active": True,
                "is_wheel_candidate": line.get("is_wheel_candidate", "false").lower() == "true",
                "dividend_yield": None,
                "market_cap": None,
                "beta": None,
            }
            for line in reader
        ]
    return rows


def main() -> None:
    args = parse_args()
    print(f"[{datetime.now()}] Starting universe ingestion from {args.csv_file}")

    rows = load_csv_rows(args.csv_file)
    loader = UniverseLoader(
        dbname=args.dbname,
        user=args.user,
        password=args.password,
        host=args.host,
        port=int(args.port) if args.port else None,
    )

    try:
        loader.upsert_universe(rows)
        print(f"[{datetime.now()}] Universe ingestion complete. Rows upserted: {len(rows)}")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR during universe ingestion: {e}")
    finally:
        loader.close()


if __name__ == "__main__":
    main()

