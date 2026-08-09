/*
--------------------------------------------------------
Script : 05_vw_payment_methods.sql
Autor  : Johnny Galicia
Proyecto: Sales Analytics Dashboard

Objetivo:
Crear una vista con indicadores por método de pago.
--------------------------------------------------------
*/

USE SalesAnalytics;
GO

CREATE OR ALTER VIEW vw_payment_methods AS

SELECT

    payment_method,

    COUNT(order_id) AS total_orders,

    SUM(order_amount) AS total_sales,

    AVG(order_amount) AS average_order

FROM orders

GROUP BY
    payment_method;

GO