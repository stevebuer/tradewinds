#!/usr/bin/env python3

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.clients.yahoo_api import YahooFinanceApi as YahooClient
from data.config import get_db_config
from data.loaders.price_quotes_loader import PriceQuotesLoader


def parse_args() -> argparse.Namespace:
    db_config = get_db_config()
    parser = argparse.ArgumentParser(
        description="Fetch live price quotes from Yahoo and load into price_quotes table.",
    )
    parser.add_argument("--symbol", required=True, help="Ticker symbol to fetch")
    parser.add_argument("--dbname", default=db_config["dbname"], help="Postgres database name")
    parser.add_argument("--user", default=db_config["user"], help="Postgres user")
    parser.add_argument(
        "--password",
        default=db_config["password"],
        required=not bool(db_config["password"]),
        help="Postgres password",
    )
    parser.add_argument("--host", default=db_config["host"], help="Postgres host")
    parser.add_argument("--port", default=db_config["port"], help="Postgres port")
    return parser.parse_args()


def quote_to_row(symbol: str, quote: dict) -> dict:
    ts = quote.get("regularMarketTime") or quote.get("postMarketTime") or quote.get("preMarketTime")
    timestamp = datetime.fromtimestamp(ts) if ts is not None else datetime.utcnow()

    return {
        "symbol": symbol.upper(),
        "price": quote.get("regularMarketPrice") or quote.get("lastPrice"),
        "bid": quote.get("bid"),
        "ask": quote.get("ask"),
        "timestamp": timestamp,
    }


def main() -> None:
    args = parse_args()
    client = YahooClient()
    loader = PriceQuotesLoader(
        dbname=args.dbname,
        user=args.user,
        password=args.password,
        host=args.host,
        port=int(args.port) if args.port else None,
    )

    try:
        print(f"Fetching quote for {args.symbol}")
        data = client.get_quote(args.symbol)
        result = data.get("result") or data.get("quoteResponse", {}).get("result")
        quote = result[0] if isinstance(result, list) and result else {}

        row = quote_to_row(args.symbol, quote)
        loader.upsert_price_quotes([row])
        print(f"Inserted quote for {args.symbol} at {row['timestamp']}")
    except Exception as e:
        print(f"ERROR fetching or loading quote: {e}")
    finally:
        loader.close()


if __name__ == "__main__":
    main()
