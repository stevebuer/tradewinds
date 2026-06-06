import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class VolRegimeHeatmap:
    """
    Creates a heatmap of volatility regimes over time vs expiration.
    """

    def __init__(self):
        sns.set(style="whitegrid")

    def prepare_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Expects df with: timestamp, expiration, regime
        Returns pivot table: rows = timestamp, columns = expiration, values = regime
        """
        pivot = df.pivot_table(
            index="timestamp",
            columns="expiration",
            values="regime",
            aggfunc="first"
        )
        return pivot.sort_index()

    def plot(self, matrix: pd.DataFrame, symbol: str):
        plt.figure(figsize=(14, 6))
        sns.heatmap(
            matrix.T,
            cmap="viridis",
            cbar=True,
            linewidths=0.3,
            linecolor="gray"
        )
        plt.title(f"{symbol} – Volatility Regime Heatmap")
        plt.xlabel("Timestamp")
        plt.ylabel("Expiration")
        plt.tight_layout()
        plt.show()

