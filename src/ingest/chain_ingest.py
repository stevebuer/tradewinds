#!/usr/bin/env python3

import argparse
import getpass
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.clients.yahoo_api import YahooFinanceApi as YahooClient
from data.config import get_db_config
from data.loaders.chain_loader import ChainLoader


def parse_args() -> argparse.Namespace:
    db_config = get_db_config()
    parser = argparse.ArgumentParser(
        description="Ingest Yahoo Finance option chain data into the tradewinds database.",
        epilog=(
            "Example: ./chain_ingest.py --symbol AAPL --all-expirations "
            "--dbname tradewinds --user your_user --password secret"
        ),
    )
    parser.add_argument("--symbol", required=True, help="Ticker symbol to ingest")
    expiration_group = parser.add_mutually_exclusive_group()
    expiration_group.add_argument(
        "--expiration",
        help=(
            "Expiration date to ingest, either YYYY-MM-DD or Unix timestamp. "
            "If not provided, all available expirations are loaded."
        ),
    )
    expiration_group.add_argument(
        "--all-expirations",
        action="store_true",
        help="Force ingestion of all available expirations for the symbol.",
    )
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


def parse_expiration(expiration: str) -> int:
    if expiration.isdigit():
        return int(expiration)

    try:
        parsed = datetime.fromisoformat(expiration)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid expiration format: {expiration}. Use YYYY-MM-DD or Unix timestamp."
        ) from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return int(parsed.timestamp())


def _timestamp_to_datetime(timestamp: Optional[int]) -> Optional[datetime]:
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def normalize_option_chain(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = raw.get("optionChain", {}).get("result")
    if not result:
        return []

    chain = result[0]
    quote = chain.get("quote", {}) or {}
    underlying = quote.get("symbol") or chain.get("symbol")
    quote_time = _timestamp_to_datetime(quote.get("regularMarketTime"))
    if quote_time is None:
        quote_time = datetime.now(tz=timezone.utc)

    options = chain.get("options", [])
    if not options:
        return []

    rows: List[Dict[str, Any]] = []
    option_block = options[0]

    for side in ("calls", "puts"):
        for contract in option_block.get(side, []):
            expiration_ts = contract.get("expiration")
            if expiration_ts is None:
                continue

            rows.append({
                "underlying": underlying,
                "quote_time": quote_time,
                "expiration": datetime.fromtimestamp(expiration_ts, tz=timezone.utc).date(),
                "strike": contract.get("strike"),
                "option_type": side[:-1],
                "bid": contract.get("bid"),
                "ask": contract.get("ask"),
                "last": contract.get("lastPrice"),
                "delta": contract.get("delta"),
                "gamma": contract.get("gamma"),
                "theta": contract.get("theta"),
                "vega": contract.get("vega"),
                "implied_vol": contract.get("impliedVol"),
                "open_interest": contract.get("openInterest"),
                "volume": contract.get("volume"),
            })

    return rows


def fetch_expiration_timestamps(client: YahooClient, symbol: str, expiration: Optional[str]) -> List[Optional[int]]:
    if expiration:
        return [parse_expiration(expiration)]

    expirations = client.get_option_expirations(symbol)
    return expirations or [None]


def main() -> None:
    args = parse_args()
    symbol = args.symbol.upper()
    client = YahooClient()
    if args.all_expirations:
        expiration_timestamps = client.get_option_expirations(symbol)
    else:
        expiration_timestamps = fetch_expiration_timestamps(client, symbol, args.expiration)

    if not expiration_timestamps:
        print(f"No option expirations found for {symbol}.")
        return

    loader = ChainLoader(
        dbname=args.dbname,
        user=args.user,
        password=args.password,
        host=args.host,
        port=int(args.port) if args.port else None,
    )

    all_rows: List[Dict[str, Any]] = []
    for expiration_ts in expiration_timestamps:
        print(f"Fetching option chain for {symbol} expiration={expiration_ts}")
        raw_chain = client.get_option_chain(symbol, date=expiration_ts)
        rows = normalize_option_chain(raw_chain)
        all_rows.extend(rows)

    if not all_rows:
        print(f"No option chain rows could be normalized for {symbol}.")
        loader.close()
        return

    loader.insert_chain_rows(all_rows)
    print(f"Loaded {len(all_rows)} option chain rows for {symbol}.")
    loader.close()


if __name__ == "__main__":
    main()
