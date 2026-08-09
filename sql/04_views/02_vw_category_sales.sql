/*
--------------------------------------------------------
Script : 02_vw_category_sales.sql
Autor  : Johnny Galicia
Proyecto: Sales Analytics Dashboard

Objetivo:
Crear una vista con indicadores de ventas por categoría.

Descripción:
Cada fila representa una categoría de producto.

Indicadores:
- Productos vendidos
- Cantidad total
- Ventas totales
- Precio promedio
--------------------------------------------------------
*/

USE SalesAnalytics;
GO

CREATE OR ALTER VIEW vw_category_sales AS

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
    p.category;
GO