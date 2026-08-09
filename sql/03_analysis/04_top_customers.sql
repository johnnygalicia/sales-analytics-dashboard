/*
--------------------------------------------------------
Script : 04_top_customers.sql
Autor  : Johnny Galicia
Proyecto: Sales Analytics Dashboard

Objetivo:
Identificar los clientes con mayor valor para la empresa.

Pregunta de negocio:
¿Quiénes son los mejores clientes?

Tablas utilizadas:
- customers
- orders

Salida:
customer_id
country
customer_segment
customer_level
total_orders
total_spent
average_order
--------------------------------------------------------
*/

USE SalesAnalytics;
GO

SELECT

    c.customer_id,

    c.country,

    c.customer_segment,

    CASE

        WHEN SUM(o.order_amount) >= 20000 THEN 'VIP'

        WHEN SUM(o.order_amount) >= 15000 THEN 'Premium'

        ELSE 'Standard'

    END AS customer_level,

    COUNT(o.order_id) AS total_orders,

    SUM(o.order_amount) AS total_spent,

    AVG(o.order_amount) AS average_order

FROM customers c

INNER JOIN orders o

    ON c.customer_id = o.customer_id

GROUP BY

    c.customer_id,
    c.country,
    c.customer_segment

ORDER BY

    total_spent DESC;

GO