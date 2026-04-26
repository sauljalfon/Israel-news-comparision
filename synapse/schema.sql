-- ============================================
-- Israel News Intelligence Pipeline
-- Synapse Serverless SQL Setup
-- ============================================
-- Run these in order on Synapse Studio (Built-in pool)
-- ============================================

-- Step 1: Create the database
-- (Run this in the 'master' database)
CREATE DATABASE news_analytics;

-- ============================================
-- Switch to news_analytics before running the rest
-- USE news_analytics;
-- ============================================

-- Step 2: Create master key (required for credentials)
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'YourStrongPassword123!';

-- Step 3: Create credential using Synapse Managed Identity
-- Requires Storage Blob Data Reader role on stilnewscompdev
CREATE DATABASE SCOPED CREDENTIAL managed_identity_credential
WITH IDENTITY = 'Managed Identity';

-- Step 4: Create external data source pointing to Gold layer
CREATE EXTERNAL DATA SOURCE blob_storage
WITH (
    LOCATION = 'https://stilnewscompdev.blob.core.windows.net/processed',
    CREDENTIAL = managed_identity_credential
);

-- Step 5: Create external file format for Parquet
CREATE EXTERNAL FILE FORMAT parquet_format
WITH (
    FORMAT_TYPE = PARQUET
);

-- Step 6: Create external table for headlines + market data
-- LOCATION = '**' scans all subfolders recursively
-- Each date folder (e.g. 2025-04-22/) contains articles.parquet
-- TASE data is pivoted: one row per article with all market columns
CREATE EXTERNAL TABLE headlines (
    [source]            VARCHAR(32),
    language            VARCHAR(8),
    title               VARCHAR(MAX),
    url                 VARCHAR(MAX),
    published           VARCHAR(64),
    full_text           VARCHAR(MAX),
    category            VARCHAR(64),
    sentiment           FLOAT,
    urgency             VARCHAR(32),
    geographic_scope    VARCHAR(32),
    summary             VARCHAR(MAX),
    keywords            VARCHAR(MAX),
    entities_people     VARCHAR(MAX),
    entities_orgs       VARCHAR(MAX),
    entities_places     VARCHAR(MAX),
    [date]              VARCHAR(16),
    ta125_open          FLOAT,
    ta125_close         FLOAT,
    ta125_high          FLOAT,
    ta125_low           FLOAT,
    ta125_volume        FLOAT,
    ta35_open           FLOAT,
    ta35_close          FLOAT,
    ta35_high           FLOAT,
    ta35_low            FLOAT,
    ta35_volume         FLOAT
)
WITH (
    LOCATION = '**',
    DATA_SOURCE = blob_storage,
    FILE_FORMAT = parquet_format
);

-- ============================================
-- Example queries
-- ============================================

-- Count articles per date
SELECT [date], COUNT(*) AS article_count
FROM headlines
GROUP BY [date]
ORDER BY [date];

-- Category distribution
SELECT category, COUNT(*) AS count
FROM headlines
GROUP BY category
ORDER BY count DESC;

-- Average sentiment by source
SELECT [source], AVG(sentiment) AS avg_sentiment
FROM headlines
GROUP BY [source]
ORDER BY avg_sentiment;

-- Articles with market data
SELECT title, category, sentiment, ta125_close, ta35_close
FROM headlines;

-- Breaking news
SELECT title, [source], category, sentiment
FROM headlines
WHERE urgency = 'Breaking';

-- Daily sentiment vs market close
SELECT [date],
       AVG(sentiment) AS avg_sentiment,
       MAX(ta125_close) AS ta125_close,
       MAX(ta35_close) AS ta35_close
FROM headlines
GROUP BY [date]
ORDER BY [date];

-- News by geographic scope
SELECT geographic_scope, COUNT(*) AS count, AVG(sentiment) AS avg_sentiment
FROM headlines
GROUP BY geographic_scope
ORDER BY count DESC;
