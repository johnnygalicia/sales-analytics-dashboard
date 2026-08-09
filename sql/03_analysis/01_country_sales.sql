SELECT
    c.country,
    COUNT(o.order_id) AS total_orders,
    SUM(o.order_amount) AS total_sales,
    AVG(o.order_amount) AS average_order
FROM customers c
INNER JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.country
ORDER BY
    total_sales DESC;
    