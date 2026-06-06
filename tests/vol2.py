from datetime import datetime
from analytics.vol_dashboard import VolDashboard

dash = VolDashboard("postgresql://user:pass@localhost:5432/tradewinds")

symbol = "KO"
df = dash.load(symbol)

dash.plot_atm_iv(df, symbol)
dash.plot_skew(df, symbol)

latest = df["timestamp"].max()
dash.plot_term_structure(df, symbol, latest)

