/*
--------------------------------------------------------
Script : 04_vw_top_customers.sql
Autor  : Johnny Galicia
Proyecto: Sales Analytics Dashboard

Objetivo:
Crear una vista con indicadores por cliente.

Cada fila representa un cliente.

Indicadores:

- Nivel de cliente
- Número de órdenes
- Gasto total
- Ticket promedio
--------------------------------------------------------
*/

USE SalesAnalytics;
GO

CREATE OR ALTER VIEW vw_top_customers AS

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
    c.customer_segment;

GO