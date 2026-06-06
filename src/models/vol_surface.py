from dataclasses import dataclass
from typing import Optional, Iterable
import pandas as pd
import numpy as np


@dataclass
class VolMetrics:
    symbol: str
    expiration: pd.Timestamp
    timestamp: pd.Timestamp
    atm_iv: float
    skew: float
    curvature: float


class VolSurface:
    """
    Expects a DataFrame with at least:
      symbol, expiration, timestamp, strike, iv, spot
    One row per option contract.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._normalize()

    def _normalize(self):
        self.df["expiration"] = pd.to_datetime(self.df["expiration"])
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        # moneyness: strike / spot
        self.df["moneyness"] = self.df["strike"] / self.df["spot"]

    def compute_metrics(self) -> list[VolMetrics]:
        metrics: list[VolMetrics] = []

        grouped = self.df.groupby(["symbol", "expiration", "timestamp"])
        for (symbol, exp, ts), g in grouped:
            g = g.sort_values("moneyness")

            # ATM = closest to moneyness 1.0
            atm_row = g.iloc[(g["moneyness"] - 1.0).abs().argmin()]
            atm_iv = float(atm_row["iv"])

            # Skew: slope of IV vs moneyness (simple linear regression)
            x = g["moneyness"].values
            y = g["iv"].values
            if len(g) >= 2:
                coeffs = np.polyfit(x, y, 1)
                skew = float(coeffs[0])
            else:
                skew = np.nan

            # Curvature: second derivative via quadratic fit
            if len(g) >= 3:
                quad = np.polyfit(x, y, 2)
                curvature = float(quad[0])  # coefficient of x^2
            else:
                curvature = np.nan

            metrics.append(
                VolMetrics(
                    symbol=symbol,
                    expiration=exp,
                    timestamp=ts,
                    atm_iv=atm_iv,
                    skew=skew,
                    curvature=curvature,
                )
            )

        return metrics

    @staticmethod
    def to_dataframe(metrics: Iterable[VolMetrics]) -> pd.DataFrame:
        return pd.DataFrame([m.__dict__ for m in metrics])

