#!/usr/bin/env python3

import argparse
import getpass
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.clients.yahoo_api import YahooFinanceApi as YahooClient
from data.config import get_db_config
from data.loaders.price_history_loader import PriceHistoryLoader


def parse_args() -> argparse.Namespace:
    db_config = get_db_config()

    parser = argparse.ArgumentParser(
        description="Ingest historical price data into the tradewinds database from Yahoo Finance.",
        epilog=(
            "Example: ./price_history_ingest.py --symbol KO --range 5y --interval 1d "
            "--dbname tradewinds --user your_user --password secret"
        ),
    )
    parser.add_argument("--symbol", required=True, help="Ticker symbol to ingest")
    parser.add_argument("--range", default="5y", help="Yahoo Finance range: 1d, 5d, 1mo, 6mo, 1y, 5y, etc.")
    parser.add_argument("--interval", default="1d", help="Yahoo Finance interval: 1d, 1wk, 1mo")
    parser.add_argument("--dbname", default=db_config["dbname"], help="Postgres database name")
    parser.add_argument("--user", default=db_config["user"], help="Postgres user")
    parser.add_argument("--password", default=db_config["password"], required=not bool(db_config["password"]),
                        help="Postgres password")
    parser.add_argument("--host", default=db_config["host"], help="Postgres host")
    parser.add_argument("--port", default=db_config["port"], help="Postgres port")
    return parser.parse_args()


def chart_to_rows(symbol: str, chart_data: dict) -> list[dict]:
    result = chart_data.get("chart", {}).get("result")
    if not result:
        return []

    quote = result[0]
    timestamps = quote.get("timestamp", [])
    indicators = quote.get("indicators", {}).get("quote", [])
    if not indicators:
        return []

    quote_values = indicators[0]
    rows = []
    for i, ts in enumerate(timestamps):
        open_price = quote_values.get("open", [])[i]
        high_price = quote_values.get("high", [])[i]
        low_price = quote_values.get("low", [])[i]
        close_price = quote_values.get("close", [])[i]
        volume = quote_values.get("volume", [])[i]

        if None in (open_price, high_price, low_price, close_price, volume):
            continue

        rows.append({
            "symbol": symbol.upper(),
            "date": datetime.fromtimestamp(ts).date(),
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume,
        })

    return rows


def main() -> None:
    args = parse_args()
    loader = PriceHistoryLoader(
        dbname=args.dbname,
        user=args.user,
        password=args.password,
        host=args.host,
        port=int(args.port) if args.port else None,
    )

    client = YahooClient()
    chart_data = client.get_chart(args.symbol, interval=args.interval, range=args.range)
    rows = chart_to_rows(args.symbol, chart_data)

    if not rows:
        print(f"No price history found for {args.symbol}.")
        return

    loader.upsert_price_history(rows)
    print(f"Loaded {len(rows)} rows for {args.symbol} into price_history")
    loader.close()


if __name__ == "__main__":
    main()

