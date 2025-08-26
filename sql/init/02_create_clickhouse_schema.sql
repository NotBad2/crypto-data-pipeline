-- ClickHouse initialization script for crypto data pipeline
-- This script creates the necessary tables for time-series data storage

-- Create database
CREATE DATABASE IF NOT EXISTS crypto_timeseries;

-- Use the database
USE crypto_timeseries;

-- Create table for high-frequency price data
CREATE TABLE IF NOT EXISTS price_ticks (
    coin_id LowCardinality(String),
    symbol LowCardinality(String),
    timestamp DateTime64(3, 'UTC'),
    price Decimal64(8),
    volume_24h Nullable(Decimal64(8)),
    market_cap Nullable(Decimal64(8)),
    source LowCardinality(String) DEFAULT 'coingecko',
    collected_at DateTime64(3, 'UTC') DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (coin_id, timestamp)
TTL timestamp + INTERVAL 2 YEAR;

-- Create table for aggregated hourly data
CREATE TABLE IF NOT EXISTS price_hourly (
    coin_id LowCardinality(String),
    symbol LowCardinality(String),
    hour DateTime('UTC'),
    open_price Decimal64(8),
    high_price Decimal64(8),
    low_price Decimal64(8),
    close_price Decimal64(8),
    avg_price Decimal64(8),
    volume_24h Nullable(Decimal64(8)),
    market_cap Nullable(Decimal64(8)),
    price_change Decimal64(8),
    price_change_pct Decimal64(4),
    records_count UInt32,
    first_seen DateTime64(3, 'UTC'),
    last_seen DateTime64(3, 'UTC')
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (coin_id, hour)
TTL hour + INTERVAL 5 YEAR;

-- Create table for daily aggregated data
CREATE TABLE IF NOT EXISTS price_daily (
    coin_id LowCardinality(String),
    symbol LowCardinality(String),
    date Date,
    open_price Decimal64(8),
    high_price Decimal64(8),
    low_price Decimal64(8),
    close_price Decimal64(8),
    avg_price Decimal64(8),
    volume_24h Nullable(Decimal64(8)),
    market_cap Nullable(Decimal64(8)),
    price_change Decimal64(8),
    price_change_pct Decimal64(4),
    volatility Decimal64(4),
    records_count UInt32,
    first_seen DateTime64(3, 'UTC'),
    last_seen DateTime64(3, 'UTC')
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (coin_id, date);

-- Create table for market events and anomalies
CREATE TABLE IF NOT EXISTS market_events (
    id UUID DEFAULT generateUUIDv4(),
    coin_id LowCardinality(String),
    event_type LowCardinality(String), -- 'price_spike', 'volume_surge', 'new_ath', 'crash'
    timestamp DateTime64(3, 'UTC'),
    description String,
    severity LowCardinality(String), -- 'low', 'medium', 'high', 'critical'
    price_before Decimal64(8),
    price_after Decimal64(8),
    price_change_pct Decimal64(4),
    volume_change_pct Nullable(Decimal64(4)),
    market_cap_before Nullable(Decimal64(8)),
    market_cap_after Nullable(Decimal64(8)),
    detected_at DateTime64(3, 'UTC') DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, coin_id);

-- Create table for global market metrics
CREATE TABLE IF NOT EXISTS global_metrics (
    timestamp DateTime64(3, 'UTC'),
    total_market_cap Decimal64(8),
    total_volume_24h Decimal64(8),
    bitcoin_dominance Decimal64(4),
    ethereum_dominance Decimal64(4),
    market_cap_change_24h Decimal64(4),
    active_cryptocurrencies UInt32,
    fear_greed_index Nullable(UInt8),
    collected_at DateTime64(3, 'UTC') DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY timestamp;

-- Create materialized views for real-time aggregations

-- Hourly aggregation view
CREATE MATERIALIZED VIEW IF NOT EXISTS price_hourly_mv TO price_hourly AS
SELECT
    coin_id,
    symbol,
    toStartOfHour(timestamp) as hour,
    argMin(price, timestamp) as open_price,
    max(price) as high_price,
    min(price) as low_price,
    argMax(price, timestamp) as close_price,
    avg(price) as avg_price,
    argMax(volume_24h, timestamp) as volume_24h,
    argMax(market_cap, timestamp) as market_cap,
    close_price - open_price as price_change,
    (close_price - open_price) / open_price * 100 as price_change_pct,
    count() as records_count,
    min(collected_at) as first_seen,
    max(collected_at) as last_seen
FROM price_ticks
GROUP BY coin_id, symbol, hour;

-- Daily aggregation view
CREATE MATERIALIZED VIEW IF NOT EXISTS price_daily_mv TO price_daily AS
SELECT
    coin_id,
    symbol,
    toDate(timestamp) as date,
    argMin(price, timestamp) as open_price,
    max(price) as high_price,
    min(price) as low_price,
    argMax(price, timestamp) as close_price,
    avg(price) as avg_price,
    argMax(volume_24h, timestamp) as volume_24h,
    argMax(market_cap, timestamp) as market_cap,
    close_price - open_price as price_change,
    (close_price - open_price) / open_price * 100 as price_change_pct,
    stddevPop(price) / avg(price) * 100 as volatility,
    count() as records_count,
    min(collected_at) as first_seen,
    max(collected_at) as last_seen
FROM price_ticks
GROUP BY coin_id, symbol, date;

-- Create functions for common queries

-- Function to get latest prices
CREATE OR REPLACE FUNCTION getLatestPrices()
RETURNS TABLE (
    coin_id String,
    symbol String,
    price Decimal64(8),
    timestamp DateTime64(3, 'UTC'),
    price_change_24h Decimal64(4)
) AS $$
SELECT 
    pt.coin_id,
    pt.symbol,
    pt.price,
    pt.timestamp,
    COALESCE((pt.price - pd.close_price) / pd.close_price * 100, 0) as price_change_24h
FROM (
    SELECT 
        coin_id,
        symbol,
        price,
        timestamp,
        ROW_NUMBER() OVER (PARTITION BY coin_id ORDER BY timestamp DESC) as rn
    FROM price_ticks
    WHERE timestamp >= now() - INTERVAL 1 HOUR
) pt
LEFT JOIN (
    SELECT coin_id, close_price
    FROM price_daily
    WHERE date = today() - 1
) pd ON pt.coin_id = pd.coin_id
WHERE pt.rn = 1
ORDER BY pt.timestamp DESC;
$$;

-- Create indexes for better query performance
-- Note: ClickHouse uses ORDER BY for indexing, but we can optimize with additional keys

-- Create table for API performance metrics
CREATE TABLE IF NOT EXISTS api_metrics (
    timestamp DateTime64(3, 'UTC'),
    source LowCardinality(String),
    endpoint String,
    response_time_ms UInt32,
    status_code UInt16,
    records_fetched UInt32,
    error_message Nullable(String),
    collected_at DateTime64(3, 'UTC') DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (source, timestamp)
TTL timestamp + INTERVAL 90 DAY;

-- Insert initial test data
INSERT INTO global_metrics (timestamp, total_market_cap, total_volume_24h, bitcoin_dominance, ethereum_dominance, market_cap_change_24h, active_cryptocurrencies)
VALUES (now(), 0, 0, 0, 0, 0, 0);

-- Create a view for monitoring data freshness
CREATE OR REPLACE VIEW data_freshness AS
SELECT 
    'price_ticks' as table_name,
    max(timestamp) as latest_data,
    count() as total_records,
    uniq(coin_id) as unique_coins
FROM price_ticks
UNION ALL
SELECT 
    'global_metrics' as table_name,
    max(timestamp) as latest_data,
    count() as total_records,
    0 as unique_coins
FROM global_metrics;

-- Create alerts view for monitoring
CREATE OR REPLACE VIEW monitoring_alerts AS
SELECT 
    'stale_data' as alert_type,
    table_name,
    latest_data,
    now() - latest_data as age_seconds,
    CASE 
        WHEN now() - latest_data > INTERVAL 1 HOUR THEN 'critical'
        WHEN now() - latest_data > INTERVAL 30 MINUTE THEN 'warning'
        ELSE 'ok'
    END as severity
FROM data_freshness
WHERE now() - latest_data > INTERVAL 10 MINUTE;
