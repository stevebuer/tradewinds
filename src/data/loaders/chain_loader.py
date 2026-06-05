import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Dict, Any


class ChainLoader:
    """
    Loads normalized option chain rows into PostgreSQL.
    """

    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        self.conn.autocommit = True

    # ---------------------------------------------------------
    # Insert rows
    # ---------------------------------------------------------
    def insert_chain_rows(self, rows: List[Dict[str, Any]]) -> None:
        """
        Insert a list of normalized option chain rows into the database.
        Uses execute_batch for efficiency.
        """

        if not rows:
            return

        sql = """
            INSERT INTO option_chains (
                underlying,
                quote_time,
                expiration,
                strike,
                option_type,
                bid,
                ask,
                last,
                delta,
                gamma,
                theta,
                vega,
                implied_vol,
                open_interest,
                volume
            )
            VALUES (
                %(underlying)s,
                %(quote_time)s,
                %(expiration)s,
                %(strike)s,
                %(option_type)s,
                %(bid)s,
                %(ask)s,
                %(last)s,
                %(delta)s,
                %(gamma)s,
                %(theta)s,
                %(vega)s,
                %(implied_vol)s,
                %(open_interest)s,
                %(volume)s
            );
        """

        with self.conn.cursor() as cur:
            execute_batch(cur, sql, rows, page_size=500)

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------
    def close(self):
        self.conn.close()

