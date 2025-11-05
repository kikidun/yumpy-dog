
-- Insert customers
INSERT INTO monitors (monitor_id, name, url, interval, created_at, expected_response, last_checked) VALUES
    (DEFAULT, 'Plex', 'http://172.16.20.40:32400/identity', 60, CURRENT_TIMESTAMP, '200', null),
    (DEFAULT, 'Proxmox', 'https://172.16.20.35:8006/#v1:0:=node%2Feevee:4:5::::::', 90, CURRENT_TIMESTAMP, '200', null),
    (DEFAULT, 'Switch', 'http://172.16.20.254/csdaffe074/config/log_off_page.htm', 15, CURRENT_TIMESTAMP, '200', null),
    (DEFAULT, 'Router', 'https://172.16.255.250/', 15, CURRENT_TIMESTAMP, '200', null);


-- Insert orders
INSERT INTO healthcheck_data (datapoint_id, healthcheck_timestamp, monitor_id, response, response_time) VALUES
    (DEFAULT, '2025-11-03 10:30:00', 1, 200, '0:00:00.045014'),
    (DEFAULT, '2025-11-03 10:31:00', 1, 200, '0:00:00.045014'),
    (DEFAULT, '2025-11-03 10:32:00', 1, 200, '0:00:00.045014'),
    (DEFAULT, '2025-11-03 10:33:00', 1, 200, '0:00:00.045014'),
    (DEFAULT, '2025-11-03 10:30:00', 2, 200, '0:00:00.045014'),
    (DEFAULT, '2025-11-03 10:31:00', 2, 200, '0:00:00.045014'),
    (DEFAULT, '2025-11-03 10:32:00', 2, 500, '0:00:00.145014'),
    (DEFAULT, '2025-11-03 10:33:00', 2, 200, '0:00:00.045014');




--SELECT c.name FROM customers c
--JOIN orders o ON c.customer_id = o.customer_id
--WHERE o.product_name = "Laptop";


-- INSERT INTO config (key, value) VALUES ('worker_enabled', 'True') ON CONFLICT (key) DO NOTHING;

-- UPDATE config SET value = 'False', updated_at = CURRENT_TIMESTAMP WHERE key = 'worker_enabled';