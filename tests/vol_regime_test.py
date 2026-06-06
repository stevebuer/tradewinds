from analytics.vol_regimes import VolRegimeDetector
from analytics.vol_dashboard import VolDashboard

dash = VolDashboard("postgresql://user:pass@localhost:5432/tradewinds")
df = dash.load("KO")

detector = VolRegimeDetector(n_regimes=3)
df_regimes = detector.fit_predict(df)

