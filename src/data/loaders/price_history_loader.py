import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime


class PriceHistoryLoader:
    def __init__(self, dbname, user, password, host="localhost"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        self.conn.autocommit = True

    def close(self):
        self.conn.close()

    def upsert_price_history(self, rows):
        """
        rows = [
            {
                "symbol": "KO",
                "date": datetime.date,
                "open": float,
                "high": float,
                "low": float,
                "close": float,
                "volume": int
            },
            ...
        ]
        """

        sql = """
            INSERT INTO price_history (
                symbol,
                date,
                open,
                high,
                low,
                close,
                volume
            )
            VALUES (
                %(symbol)s,
                %(date)s,
                %(open)s,
                %(high)s,
                %(low)s,
                %(close)s,
                %(volume)s
            )
            ON CONFLICT (symbol, date) DO UPDATE
            SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume;
        """

        with self.conn.cursor() as cur:
            execute_batch(cur, sql, rows, page_size=200)

