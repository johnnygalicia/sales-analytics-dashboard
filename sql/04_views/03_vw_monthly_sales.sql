/*
--------------------------------------------------------
Script : 03_vw_monthly_sales.sql
Autor  : Johnny Galicia
Proyecto: Sales Analytics Dashboard

Objetivo:
Crear una vista con indicadores mensuales.

Cada fila representa un mes calendario.
--------------------------------------------------------
*/

USE SalesAnalytics;
GO

CREATE OR ALTER VIEW vw_monthly_sales AS

SELECT

    FORMAT(order_date, 'yyyy-MM') AS period,

    DATEFROMPARTS(
        YEAR(order_date),
        MONTH(order_date),
        1
    ) AS period_start,

    YEAR(order_date) AS sales_year,

    MONTH(order_date) AS sales_month,

    COUNT(order_id) AS total_orders,

    SUM(order_amount) AS total_sales,

    AVG(order_amount) AS average_order

FROM orders

GROUP BY

    YEAR(order_date),
    MONTH(order_date),
    FORMAT(order_date, 'yyyy-MM'),
    DATEFROMPARTS(
        YEAR(order_date),
        MONTH(order_date),
        1
    );
GO