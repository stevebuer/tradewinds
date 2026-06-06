import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
from typing import List, Dict, Any


class PriceQuotesLoader:
    def __init__(self, dbname, user, password, host="localhost", port=None):
        connect_args = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
        }
        if port is not None:
            connect_args["port"] = port

        self.conn = psycopg2.connect(**connect_args)
        self.conn.autocommit = True

    def close(self):
        self.conn.close()

    def upsert_price_quotes(self, rows: List[Dict[str, Any]]):
        """
        rows = [
            {
                "symbol": "KO",
                "price": 61.23,
                "bid": 61.2,
                "ask": 61.3,
                "timestamp": datetime
            },
            ...
        ]
        """
        if not rows:
            return

        # Ensure underlyings exist in the underlyings table
        symbols = {row["symbol"] for row in rows}
        self._ensure_underlyings(symbols)

        sql = """
            INSERT INTO price_quotes (
                symbol,
                price,
                bid,
                ask,
                timestamp
            )
            VALUES (
                %(symbol)s,
                %(price)s,
                %(bid)s,
                %(ask)s,
                %(timestamp)s
            )
            ON CONFLICT (symbol, timestamp) DO UPDATE
            SET
                price = EXCLUDED.price,
                bid = EXCLUDED.bid,
                ask = EXCLUDED.ask;
        """

        with self.conn.cursor() as cur:
            execute_batch(cur, sql, rows, page_size=200)

    def _ensure_underlyings(self, symbols):
        if not symbols:
            return

        sql = """
            INSERT INTO underlyings (symbol)
            VALUES (%(symbol)s)
            ON CONFLICT (symbol) DO NOTHING;
        """

        rows = [{"symbol": symbol} for symbol in symbols]
        with self.conn.cursor() as cur:
            execute_batch(cur, sql, rows, page_size=200)
