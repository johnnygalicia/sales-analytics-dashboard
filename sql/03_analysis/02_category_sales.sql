/*
--------------------------------------------------------
Script : 02_category_sales.sql
Autor  : Johnny Galicia
Proyecto: Sales Analytics Dashboard

Objetivo:
Analizar las ventas por categoría de producto.

Pregunta de negocio:
¿Qué categorías generan mayores ingresos?

Tablas utilizadas:
- products
- order_items

Salida:
category
products_sold
total_quantity
total_sales
average_price
--------------------------------------------------------
*/

USE SalesAnalytics;
GO

SELECT
    p.category,
    COUNT(DISTINCT oi.product_id) AS products_sold,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * p.price) AS total_sales,
    AVG(p.price) AS average_price
FROM order_items oi
INNER JOIN products p
    ON oi.product_id = p.product_id
GROUP BY
    p.category
ORDER BY
    total_sales DESC;
GO