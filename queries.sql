-- queries.sql
-- Business-question style SQL queries run against ecommerce.db (table: orders)
-- Demonstrates: aggregation, filtering, joins-equivalent grouping, window functions, CTEs

-- 1. Total revenue and order count by product category
SELECT
    product_category,
    COUNT(*)            AS total_orders,
    SUM(revenue)         AS total_revenue,
    ROUND(AVG(revenue),2) AS avg_order_value
FROM orders
GROUP BY product_category
ORDER BY total_revenue DESC;

-- 2. Monthly revenue trend
SELECT
    strftime('%Y-%m', order_date) AS month,
    SUM(revenue) AS monthly_revenue,
    COUNT(*)     AS orders
FROM orders
GROUP BY month
ORDER BY month;

-- 3. Top 5 customers by total spend
SELECT
    customer_id,
    COUNT(*)     AS num_orders,
    SUM(revenue) AS total_spend
FROM orders
GROUP BY customer_id
ORDER BY total_spend DESC
LIMIT 5;

-- 4. Region performance with rank (window function)
SELECT
    region,
    SUM(revenue) AS revenue,
    RANK() OVER (ORDER BY SUM(revenue) DESC) AS revenue_rank
FROM orders
GROUP BY region;

-- 5. Average rating and delivery time by category (CTE)
WITH category_stats AS (
    SELECT
        product_category,
        AVG(rating)         AS avg_rating,
        AVG(delivery_days)  AS avg_delivery_days
    FROM orders
    WHERE rating IS NOT NULL
    GROUP BY product_category
)
SELECT * FROM category_stats
ORDER BY avg_rating DESC;

-- 6. Payment method preference by region
SELECT
    region,
    payment_method,
    COUNT(*) AS orders
FROM orders
GROUP BY region, payment_method
ORDER BY region, orders DESC;

-- 7. Orders with below-average rating but above-average revenue
-- (flags "expensive but disappointing" products worth investigating)
SELECT
    product_name,
    revenue,
    rating
FROM orders
WHERE rating < (SELECT AVG(rating) FROM orders WHERE rating IS NOT NULL)
  AND revenue > (SELECT AVG(revenue) FROM orders)
ORDER BY revenue DESC
LIMIT 10;
