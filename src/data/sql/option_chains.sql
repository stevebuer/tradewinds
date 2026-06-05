-- Option chain table for tradewinds
-- Stores normalized TD Ameritrade chain data

CREATE TABLE option_chains (
    id SERIAL PRIMARY KEY,
    underlying TEXT NOT NULL,                 -- e.g. KO, PG, JNJ
    quote_time TIMESTAMP NOT NULL,            -- when the chain was fetched
    expiration DATE NOT NULL,                 -- option expiration date
    strike NUMERIC NOT NULL,                  -- strike price
    option_type TEXT NOT NULL,                -- 'call' or 'put'
    bid NUMERIC,
    ask NUMERIC,
    last NUMERIC,
    delta NUMERIC,
    gamma NUMERIC,
    theta NUMERIC,
    vega NUMERIC,
    implied_vol NUMERIC,
    open_interest INT,
    volume INT
);

