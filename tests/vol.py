from datetime import datetime
from analytics.vol_dashboard import VolDashboard

db_url = "postgresql://user:pass@localhost:5432/tradewinds"
symbol = "KO"

dash = VolDashboard(db_url)
df = dash.load_vol_metrics(symbol)

dash.plot_atm_iv_time_series(df, symbol)
dash.plot_skew_time_series(df, symbol)

as_of = df["timestamp"].max()
dash.plot_term_structure(df, symbol, as_of)

