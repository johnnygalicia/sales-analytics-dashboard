USE SalesAnalytics;
GO

CREATE OR ALTER VIEW vw_sales_detail
AS

SELECT

    -- ===============================
    -- PEDIDO
    -- ===============================

    o.order_id,
    o.order_date,
    YEAR(o.order_date)  AS sales_year,
    MONTH(o.order_date) AS sales_month,

    -- ===============================
    -- CLIENTE
    -- ===============================

    c.customer_id,
    c.country,
    c.customer_segment,
    c.acquisition_channel,
    c.is_active,

    -- ===============================
    -- PRODUCTO
    -- ===============================

    p.product_id,
    p.category,
    p.price,
    p.cost,

    -- ===============================
    -- DETALLE DEL PEDIDO
    -- ===============================

    oi.quantity,

    -- ===============================
    -- MÉTRICAS
    -- ===============================

    (oi.quantity * p.price) AS total_sale,

    (oi.quantity * p.cost) AS total_cost,

    (oi.quantity * (p.price - p.cost)) AS total_profit,

    -- ===============================
    -- PEDIDO
    -- ===============================

    o.payment_method,
    o.order_status

FROM orders o

INNER JOIN customers c
    ON o.customer_id = c.customer_id

INNER JOIN order_items oi
    ON o.order_id = oi.order_id

INNER JOIN products p
    ON oi.product_id = p.product_id;

GO