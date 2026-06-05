#!/usr/bin/env python3

import argparse
import csv
import getpass
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from data.config import get_db_config


class UniverseLoader:
    """
    Loads/updates universe metadata into the `underlyings` table.

    Can also be run directly as a script to ingest a CSV of universe items.
    """

    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost", port: int | None = None):
        conn_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
        }
        if port is not None:
            conn_params["port"] = port

        self.conn = psycopg2.connect(**conn_params)
        self.conn.autocommit = True

    def upsert_universe(self, rows: List[Dict[str, Any]]) -> None:
        """
        Upsert a list of universe items.

        Expected keys per row:
          symbol, name, sector, industry,
          is_active, is_wheel_candidate,
          dividend_yield, market_cap, beta
        """
        if not rows:
            return

        sql = """
            INSERT INTO underlyings (
                symbol,
                name,
                sector,
                industry,
                is_active,
                is_wheel_candidate,
                dividend_yield,
                market_cap,
                beta,
                last_updated
            )
            VALUES (
                %(symbol)s,
                %(name)s,
                %(sector)s,
                %(industry)s,
                %(is_active)s,
                %(is_wheel_candidate)s,
                %(dividend_yield)s,
                %(market_cap)s,
                %(beta)s,
                NOW()
            )
            ON CONFLICT (symbol) DO UPDATE
            SET
                name = EXCLUDED.name,
                sector = EXCLUDED.sector,
                industry = EXCLUDED.industry,
                is_active = EXCLUDED.is_active,
                is_wheel_candidate = EXCLUDED.is_wheel_candidate,
                dividend_yield = EXCLUDED.dividend_yield,
                market_cap = EXCLUDED.market_cap,
                beta = EXCLUDED.beta,
                last_updated = NOW();
        """

        with self.conn.cursor() as cur:
            execute_batch(cur, sql, rows, page_size=200)

    def close(self) -> None:
        self.conn.close()


def parse_args() -> argparse.Namespace:
    db_config = get_db_config()

    parser = argparse.ArgumentParser(
        description="Load universe metadata into the tradewinds PostgreSQL database.",
        epilog=(
            "CSV format must include at least these headers: "
            "symbol,name,sector,industry,is_wheel_candidate"
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


def load_csv_rows(csv_file: str) -> List[Dict[str, Any]]:
    with open(csv_file, newline="", encoding="utf-8") as f:
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
        print(f"Loaded {len(rows)} universe rows into underlyings table")
    finally:
        loader.close()


if __name__ == "__main__":
    main()

