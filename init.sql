-- Create a database (run this separately or connect to postgres first)
-- CREATE DATABASE demo_db;

-- Connect to your database, then run:

-- Drop tables if they exist (for clean slate)
DROP TABLE IF EXISTS monitors;
DROP TABLE IF EXISTS healthcheck_data;

-- Create customers table
CREATE TABLE monitors (
    monitor_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(150) NOT NULL,
    interval INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_response VARCHAR(100) DEFAULT '200',
    last_checked TIMESTAMP
);

-- Create a data table
CREATE TABLE healthcheck_data (
    datapoint_id SERIAL PRIMARY KEY,
    healthcheck_timestamp TIMESTAMPTZ NOT NULL,
    monitor_id INT,
    response FLOAT,
    response_time INTERVAL
); --PARTITION BY RANGE (healthcheck_timestamp);
