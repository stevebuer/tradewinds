vol_metrics (
    symbol TEXT,
    expiration DATE,
    timestamp TIMESTAMP,
    atm_iv NUMERIC,
    skew NUMERIC,
    curvature NUMERIC,
    PRIMARY KEY (symbol, expiration, timestamp)
)
