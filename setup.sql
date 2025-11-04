-- Create a database (run this separately or connect to postgres first)
-- CREATE DATABASE demo_db;

-- Connect to your database, then run:

-- Drop tables if they exist (for clean slate)
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

-- Create customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    city VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table (related to customers)
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    order_date DATE DEFAULT CURRENT_DATE
);

-- Insert customers
INSERT INTO customers (name, email, city) VALUES
    ('Alice Johnson', 'alice@email.com', 'Seattle'),
    ('Bob Smith', 'bob@email.com', 'Portland'),
    ('Carol White', 'carol@email.com', 'Seattle'),
    ('David Brown', 'david@email.com', 'Austin'),
    ('Eve Davis', 'eve@email.com', 'Portland');

-- Insert orders
INSERT INTO orders (customer_id, product_name, quantity, price) VALUES
    (1, 'Laptop', 1, 1299.99),
    (1, 'Mouse', 2, 24.99),
    (2, 'Keyboard', 1, 89.99),
    (3, 'Monitor', 2, 349.99),
    (3, 'Webcam', 1, 79.99),
    (4, 'Headphones', 1, 199.99),
    (5, 'USB Cable', 5, 9.99),
    (5, 'Laptop', 1, 1499.99);