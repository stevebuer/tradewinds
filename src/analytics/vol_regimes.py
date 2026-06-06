import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


class VolRegimeDetector:
    """
    Detects volatility regimes using ATM IV, skew, and curvature.
    """

    def __init__(self, n_regimes: int = 3):
        self.n_regimes = n_regimes
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=n_regimes, n_init=10)

    def fit(self, df: pd.DataFrame):
        """
        df must contain: atm_iv, skew, curvature
        """
        features = df[["atm_iv", "skew", "curvature"]].fillna(0.0)
        scaled = self.scaler.fit_transform(features)
        self.model.fit(scaled)

    def predict(self, df: pd.DataFrame) -> pd.Series:
        features = df[["atm_iv", "skew", "curvature"]].fillna(0.0)
        scaled = self.scaler.transform(features)
        return pd.Series(self.model.predict(scaled), index=df.index, name="regime")

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df)
        df = df.copy()
        df["regime"] = self.predict(df)
        return df

