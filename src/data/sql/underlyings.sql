CREATE TABLE underlyings (
    symbol TEXT PRIMARY KEY,          -- KO, PG, JNJ
    name TEXT,                        -- Coca-Cola, Procter & Gamble
    sector TEXT,                      -- Consumer Staples
    industry TEXT,                    -- Beverages—Non-Alcoholic
    is_active BOOLEAN DEFAULT TRUE,   -- whether to ingest chains
    is_wheel_candidate BOOLEAN,       -- part of your wheel universe
    dividend_yield NUMERIC,           -- optional
    market_cap BIGINT,                -- optional
    beta NUMERIC,                     -- optional
    last_updated TIMESTAMP DEFAULT NOW()
);
