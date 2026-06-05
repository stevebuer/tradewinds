#!/usr/bin/env python3

import argparse
import csv
import getpass
import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Dict, Any


class DividendsLoader:
    """
    Loads dividend CSV rows into PostgreSQL dividend tables.

    Supported tables:
      - dividend_aristocrats
      - dividend_kings
      - dividend_compounders
    """

    VALID_TABLES = {
        "dividend_aristocrats",
        "dividend_kings",
        "dividend_compounders",
    }

    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
        )
        self.conn.autocommit = True

    def insert_dividends(self, rows: List[Dict[str, Any]], table: str) -> None:
        """
        Insert or update dividend rows into the specified dividend table.

        Each row is expected to contain the following keys:
          ticker, quarterly_dividend, years_of_payment, years_of_growth
        """
        if table not in self.VALID_TABLES:
            raise ValueError(
                f"Unsupported table '{table}'. Valid tables: {', '.join(sorted(self.VALID_TABLES))}"
            )

        if not rows:
            return

        sql = f"""
            INSERT INTO {table} (
                ticker,
                quarterly_dividend,
                years_of_payment,
                years_of_growth
            )
            VALUES (
                %(ticker)s,
                %(quarterly_dividend)s,
                %(years_of_payment)s,
                %(years_of_growth)s
            )
            ON CONFLICT (ticker) DO UPDATE
            SET
                quarterly_dividend = EXCLUDED.quarterly_dividend,
                years_of_payment = EXCLUDED.years_of_payment,
                years_of_growth = EXCLUDED.years_of_growth;
        """

        with self.conn.cursor() as cur:
            execute_batch(cur, sql, rows, page_size=200)

    def insert_aristocrats(self, rows: List[Dict[str, Any]]) -> None:
        self.insert_dividends(rows, "dividend_aristocrats")

    def insert_kings(self, rows: List[Dict[str, Any]]) -> None:
        self.insert_dividends(rows, "dividend_kings")

    def insert_compounders(self, rows: List[Dict[str, Any]]) -> None:
        self.insert_dividends(rows, "dividend_compounders")

    def close(self) -> None:
        self.conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load dividend CSV files into PostgreSQL dividend tables."
    )
    parser.add_argument("table", choices=DividendsLoader.VALID_TABLES,
                        help="Destination dividend table")
    parser.add_argument("csv_file", help="Path to the input CSV file")
    parser.add_argument("--dbname", default="tradewinds", help="Postgres database name")
    parser.add_argument("--user", default=getpass.getuser(), help="Postgres user")
    parser.add_argument("--password", required=True, help="Postgres password")
    parser.add_argument("--host", default="localhost", help="Postgres host")
    return parser.parse_args()


def load_csv_rows(csv_file: str) -> List[Dict[str, Any]]:
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            {
                "ticker": row["ticker"].strip().upper(),
                "quarterly_dividend": float(row["quarterly_dividend"]),
                "years_of_payment": int(row["years_of_payment"]),
                "years_of_growth": int(row["years_of_growth"]),
            }
            for row in reader
        ]
    return rows


def main() -> None:
    args = parse_args()
    rows = load_csv_rows(args.csv_file)

    loader = DividendsLoader(
        dbname=args.dbname,
        user=args.user,
        password=args.password,
        host=args.host,
    )

    try:
        loader.insert_dividends(rows, args.table)
        print(f"Loaded {len(rows)} rows into {args.table}")
    finally:
        loader.close()


if __name__ == "__main__":
    main()
