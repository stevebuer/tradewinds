from analytics.vol_dashboard import VolDashboard
from analytics.vol_regimes import VolRegimeDetector
from analytics.vol_regime_heatmap import VolRegimeHeatmap

dash = VolDashboard("postgresql://user:pass@localhost:5432/tradewinds")
df = dash.load("KO")

# detect regimes
detector = VolRegimeDetector(n_regimes=3)
df_regimes = detector.fit_predict(df)

# build heatmap
heat = VolRegimeHeatmap()
matrix = heat.prepare_matrix(df_regimes)
heat.plot(matrix, "KO")

