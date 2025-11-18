CREATE TABLE IF NOT EXISTS monitors (
    monitor_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(150) NOT NULL,
    interval INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_response VARCHAR(100) DEFAULT '200',
    last_checked TIMESTAMP
);

CREATE TABLE IF NOT EXISTS healthcheck_data (
    datapoint_id SERIAL PRIMARY KEY,
    healthcheck_timestamp TIMESTAMPTZ NOT NULL,
    monitor_id INT,
    response FLOAT,
    response_time INTERVAL
);

CREATE TABLE IF NOT EXISTS config (
    key varchar(100) UNIQUE,
    value text NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO config (key, value) VALUES ('worker_enabled', 'True');