/*
--------------------------------------------------------
Script : 01_vw_country_sales.sql
Autor  : Johnny Galicia
Proyecto: Sales Analytics Dashboard

Objetivo:
Crear una vista con indicadores de ventas por país.

Descripción:
Cada fila representa un país e incluye:
- Número de órdenes
- Ventas totales
- Ticket promedio

Esta vista será utilizada posteriormente por Power BI.
--------------------------------------------------------
*/

USE SalesAnalytics;
GO

CREATE OR ALTER VIEW vw_country_sales AS

SELECT
    c.country,
    COUNT(o.order_id) AS total_orders,
    SUM(o.order_amount) AS total_sales,
    AVG(o.order_amount) AS average_order
FROM customers c
INNER JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.country;
GO