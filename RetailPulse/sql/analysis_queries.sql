-- Create the table before importing the generated/app CSV into SQLite.
CREATE TABLE IF NOT EXISTS orders (
  order_id TEXT PRIMARY KEY,
  order_date TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL,
  region TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price REAL NOT NULL,
  unit_cost REAL NOT NULL,
  discount_pct REAL NOT NULL,
  order_status TEXT NOT NULL,
  payment_method TEXT
);

-- 1. Overall KPIs (financial values include Delivered orders only).
SELECT
  COUNT(*) AS total_orders,
  SUM(CASE WHEN order_status='Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
  COUNT(DISTINCT CASE WHEN order_status='Delivered' THEN customer_id END) AS delivered_customers,
  ROUND(SUM(CASE WHEN order_status='Delivered' THEN quantity*unit_price*(1-discount_pct) ELSE 0 END),2) AS revenue,
  ROUND(SUM(CASE WHEN order_status='Delivered' THEN quantity*(unit_price*(1-discount_pct)-unit_cost) ELSE 0 END),2) AS gross_profit
FROM orders;

-- 2. Monthly revenue and profit trend.
SELECT strftime('%Y-%m',order_date) AS month,
  ROUND(SUM(quantity*unit_price*(1-discount_pct)),2) AS revenue,
  ROUND(SUM(quantity*(unit_price*(1-discount_pct)-unit_cost)),2) AS gross_profit
FROM orders WHERE order_status='Delivered'
GROUP BY strftime('%Y-%m',order_date) ORDER BY month;

-- 3. Category and regional performance.
SELECT category, region,
  ROUND(SUM(quantity*unit_price*(1-discount_pct)),2) AS revenue
FROM orders WHERE order_status='Delivered'
GROUP BY category, region ORDER BY revenue DESC;

-- 4. Top products.
SELECT product_name, SUM(quantity) AS units_sold,
  ROUND(SUM(quantity*unit_price*(1-discount_pct)),2) AS revenue
FROM orders WHERE order_status='Delivered'
GROUP BY product_name ORDER BY revenue DESC LIMIT 10;

-- 5. Repeat purchase segmentation.
WITH customer_orders AS (
  SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
  FROM orders WHERE order_status='Delivered' GROUP BY customer_id
)
SELECT CASE WHEN order_count=1 THEN 'One-time' ELSE 'Repeat' END AS customer_type,
  COUNT(*) AS customers
FROM customer_orders GROUP BY customer_type;
