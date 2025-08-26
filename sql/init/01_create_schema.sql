-- PostgreSQL initialization script for crypto data pipeline
-- This script creates the necessary database schema for storing cryptocurrency data

-- Create database and user (if not exists)
-- Note: This is handled by docker-compose environment variables

-- Create schema for raw data
CREATE SCHEMA IF NOT EXISTS raw_data;
CREATE SCHEMA IF NOT EXISTS processed_data;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA raw_data TO crypto_user;
GRANT ALL PRIVILEGES ON SCHEMA processed_data TO crypto_user;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO crypto_user;

-- Create table for coin market data
CREATE TABLE IF NOT EXISTS raw_data.coin_market_data (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    current_price DECIMAL(20, 8),
    market_cap BIGINT,
    market_cap_rank INTEGER,
    fully_diluted_valuation BIGINT,
    total_volume BIGINT,
    high_24h DECIMAL(20, 8),
    low_24h DECIMAL(20, 8),
    price_change_24h DECIMAL(20, 8),
    price_change_percentage_24h DECIMAL(10, 4),
    price_change_percentage_7d DECIMAL(10, 4),
    price_change_percentage_30d DECIMAL(10, 4),
    price_change_percentage_1y DECIMAL(10, 4),
    market_cap_change_24h BIGINT,
    market_cap_change_percentage_24h DECIMAL(10, 4),
    circulating_supply DECIMAL(30, 8),
    total_supply DECIMAL(30, 8),
    max_supply DECIMAL(30, 8),
    ath DECIMAL(20, 8),
    ath_change_percentage DECIMAL(10, 4),
    ath_date TIMESTAMP WITH TIME ZONE,
    atl DECIMAL(20, 8),
    atl_change_percentage DECIMAL(10, 4),
    atl_date TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_coin_market_data_coin_id ON raw_data.coin_market_data(coin_id);
CREATE INDEX IF NOT EXISTS idx_coin_market_data_collected_at ON raw_data.coin_market_data(collected_at);
CREATE INDEX IF NOT EXISTS idx_coin_market_data_market_cap_rank ON raw_data.coin_market_data(market_cap_rank);

-- Create table for global market data
CREATE TABLE IF NOT EXISTS raw_data.global_market_data (
    id SERIAL PRIMARY KEY,
    active_cryptocurrencies INTEGER,
    upcoming_icos INTEGER,
    ongoing_icos INTEGER,
    ended_icos INTEGER,
    markets INTEGER,
    total_market_cap_usd DECIMAL(30, 2),
    total_volume_24h_usd DECIMAL(30, 2),
    market_cap_percentage_btc DECIMAL(10, 4),
    market_cap_percentage_eth DECIMAL(10, 4),
    market_cap_change_percentage_24h_usd DECIMAL(10, 4),
    bitcoin_dominance DECIMAL(10, 4),
    ethereum_dominance DECIMAL(10, 4),
    updated_at TIMESTAMP WITH TIME ZONE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for global market data
CREATE INDEX IF NOT EXISTS idx_global_market_data_collected_at ON raw_data.global_market_data(collected_at);

-- Create table for trending coins
CREATE TABLE IF NOT EXISTS raw_data.trending_coins (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    market_cap_rank INTEGER,
    thumb VARCHAR(500),
    small VARCHAR(500),
    large VARCHAR(500),
    slug VARCHAR(200),
    price_btc DECIMAL(20, 12),
    score INTEGER,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for trending coins
CREATE INDEX IF NOT EXISTS idx_trending_coins_collected_at ON raw_data.trending_coins(collected_at);
CREATE INDEX IF NOT EXISTS idx_trending_coins_coin_id ON raw_data.trending_coins(coin_id);

-- Create table for price history (time series data)
CREATE TABLE IF NOT EXISTS raw_data.price_history (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    market_cap DECIMAL(30, 2),
    volume_24h DECIMAL(30, 2),
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for price history
CREATE INDEX IF NOT EXISTS idx_price_history_coin_id ON raw_data.price_history(coin_id);
CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON raw_data.price_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_price_history_coin_timestamp ON raw_data.price_history(coin_id, timestamp);

-- Create unique constraint to prevent duplicate price points
CREATE UNIQUE INDEX IF NOT EXISTS idx_price_history_unique ON raw_data.price_history(coin_id, timestamp);

-- Create table for API collection logs
CREATE TABLE IF NOT EXISTS raw_data.collection_logs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL,
    records_collected INTEGER DEFAULT 0,
    error_message TEXT,
    execution_time_seconds DECIMAL(10, 3),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for collection logs
CREATE INDEX IF NOT EXISTS idx_collection_logs_source ON raw_data.collection_logs(source);
CREATE INDEX IF NOT EXISTS idx_collection_logs_started_at ON raw_data.collection_logs(started_at);

-- Create materialized view for latest coin prices
CREATE MATERIALIZED VIEW IF NOT EXISTS processed_data.latest_coin_prices AS
SELECT DISTINCT ON (coin_id)
    coin_id,
    symbol,
    name,
    current_price,
    market_cap,
    market_cap_rank,
    price_change_percentage_24h,
    price_change_percentage_7d,
    total_volume,
    collected_at
FROM raw_data.coin_market_data
ORDER BY coin_id, collected_at DESC;

-- Create index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_latest_coin_prices_coin_id ON processed_data.latest_coin_prices(coin_id);

-- Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_latest_coin_prices()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY processed_data.latest_coin_prices;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions on all tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw_data TO crypto_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA processed_data TO crypto_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO crypto_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA raw_data TO crypto_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA processed_data TO crypto_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO crypto_user;

-- Create extension for better time-series performance
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Convert price_history to a time-series table (if TimescaleDB is available)
-- This will provide better performance for time-series queries
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable('raw_data.price_history', 'timestamp', if_not_exists => TRUE);
    END IF;
END $$;

-- Create some useful views for analytics
CREATE OR REPLACE VIEW analytics.top_gainers_24h AS
SELECT 
    coin_id,
    symbol,
    name,
    current_price,
    price_change_percentage_24h,
    market_cap_rank,
    collected_at
FROM processed_data.latest_coin_prices
WHERE price_change_percentage_24h IS NOT NULL
ORDER BY price_change_percentage_24h DESC
LIMIT 10;

CREATE OR REPLACE VIEW analytics.top_losers_24h AS
SELECT 
    coin_id,
    symbol,
    name,
    current_price,
    price_change_percentage_24h,
    market_cap_rank,
    collected_at
FROM processed_data.latest_coin_prices
WHERE price_change_percentage_24h IS NOT NULL
ORDER BY price_change_percentage_24h ASC
LIMIT 10;

CREATE OR REPLACE VIEW analytics.market_overview AS
SELECT
    COUNT(*) as total_coins,
    SUM(market_cap) as total_market_cap,
    AVG(price_change_percentage_24h) as avg_24h_change,
    COUNT(CASE WHEN price_change_percentage_24h > 0 THEN 1 END) as coins_up,
    COUNT(CASE WHEN price_change_percentage_24h < 0 THEN 1 END) as coins_down,
    MAX(collected_at) as last_updated
FROM processed_data.latest_coin_prices;

-- Insert initial log entry
INSERT INTO raw_data.collection_logs (source, endpoint, status, started_at, completed_at)
VALUES ('system', 'database_init', 'success', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Display setup completion message
DO $$
BEGIN
    RAISE NOTICE 'Crypto Data Pipeline database schema created successfully!';
    RAISE NOTICE 'Schemas: raw_data, processed_data, analytics';
    RAISE NOTICE 'Tables: coin_market_data, global_market_data, trending_coins, price_history, collection_logs';
    RAISE NOTICE 'Views: latest_coin_prices, top_gainers_24h, top_losers_24h, market_overview';
END $$;
