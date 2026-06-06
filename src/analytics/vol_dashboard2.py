import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


class VolDashboard:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)

    def load(self, symbol: str) -> pd.DataFrame:
        query = """
            SELECT symbol, expiration, timestamp, atm_iv, skew, curvature
            FROM vol_metrics
            WHERE symbol = %(symbol)s
            ORDER BY timestamp, expiration;
        """
        return pd.read_sql(query, self.engine, params={"symbol": symbol})

    def plot_atm_iv(self, df: pd.DataFrame, symbol: str):
        series = (
            df.sort_values("expiration")
              .groupby("timestamp")
              .first()
              .reset_index()
        )

        plt.figure(figsize=(10, 4))
        plt.plot(series["timestamp"], series["atm_iv"], label="ATM IV")
        plt.title(f"{symbol} – ATM IV over time")
        plt.xlabel("Time")
        plt.ylabel("ATM IV")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_skew(self, df: pd.DataFrame, symbol: str):
        series = (
            df.sort_values("expiration")
              .groupby("timestamp")
              .first()
              .reset_index()
        )

        plt.figure(figsize=(10, 4))
        plt.plot(series["timestamp"], series["skew"], label="Skew", color="orange")
        plt.title(f"{symbol} – Skew over time")
        plt.xlabel("Time")
        plt.ylabel("Skew (dIV/dMoneyness)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_term_structure(self, df: pd.DataFrame, symbol: str, as_of: pd.Timestamp):
        snap = (
            df[df["timestamp"] == as_of]
            .sort_values("expiration")
        )

        if snap.empty:
            print(f"No vol metrics for {symbol} at {as_of}")
            return

        plt.figure(figsize=(8, 4))
        plt.plot(snap["expiration"], snap["atm_iv"], marker="o")
        plt.title(f"{symbol} – ATM IV term structure @ {as_of}")
        plt.xlabel("Expiration")
        plt.ylabel("ATM IV")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

