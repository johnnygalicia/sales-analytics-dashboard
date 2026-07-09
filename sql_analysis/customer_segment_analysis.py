"""
customer_segment_analysis.py

Analiza el comportamiento de las ventas utilizando consultas SQL
sobre una base de datos SQLite.

Consultas incluidas:
- Ventas mensuales por segmento de cliente.
- Ratio mensual de cancelaciones.

Autor: Johnny M. Galicia O.
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


# ============================================================
# Configuración de rutas
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "datasets"

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DB_PATH = DATABASE_DIR / "sales.db"


# ============================================================
# Conexión a SQLite
# ============================================================

def create_database_engine():
    """
    Crea la conexión con la base de datos SQLite.
    """
    return create_engine(f"sqlite:///{DB_PATH}")


# ============================================================
# Carga de datos
# ============================================================

def load_orders() -> pd.DataFrame:
    """
    Carga el conjunto de datos de órdenes.
    """
    return pd.read_csv(
        DATA_DIR / "orders.csv",
        parse_dates=["order_date"]
    )


def load_customers() -> pd.DataFrame:
    """
    Carga el conjunto de datos de clientes.
    """
    return pd.read_csv(
        DATA_DIR / "customers.csv",
        parse_dates=["signup_date"]
    )


# ============================================================
# Persistencia en SQLite
# ============================================================

def load_tables_to_database(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    engine
) -> None:
    """
    Inserta las tablas en la base de datos SQLite.
    """

    orders.to_sql(
        "orders",
        engine,
        if_exists="replace",
        index=False
    )

    customers.to_sql(
        "customers",
        engine,
        if_exists="replace",
        index=False
    )


# ============================================================
# Consulta 1
# Ventas mensuales por segmento
# ============================================================

def sales_by_customer_segment(engine) -> pd.DataFrame:
    """
    Obtiene las ventas mensuales agrupadas por segmento de cliente.
    """

    query = """
    SELECT
        strftime('%Y-%m', o.order_date) AS order_month,
        c.customer_segment,
        COUNT(o.order_id) AS total_orders,
        SUM(o.order_amount) AS revenue,
        AVG(o.order_amount) AS average_ticket
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    WHERE o.order_status = 'completed'
    GROUP BY order_month, c.customer_segment
    ORDER BY order_month, revenue DESC;
    """

    return pd.read_sql_query(query, engine)


# ============================================================
# Consulta 2
# Ratio mensual de cancelaciones
# ============================================================

def monthly_cancellation_ratio(engine) -> pd.DataFrame:
    """
    Calcula el porcentaje de órdenes canceladas por mes.
    """

    query = """
    SELECT
        strftime('%Y-%m', order_date) AS order_month,
        COUNT(*) AS total_orders,
        SUM(
            CASE
                WHEN order_status = 'canceled'
                THEN 1
                ELSE 0
            END
        ) AS canceled_orders,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN order_status = 'canceled'
                    THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            4
        ) AS cancel_ratio
    FROM orders
    GROUP BY order_month
    ORDER BY order_month;
    """

    return pd.read_sql_query(query, engine)


# ============================================================
# Programa principal
# ============================================================

def main():

    engine = create_database_engine()

    orders = load_orders()

    customers = load_customers()

    load_tables_to_database(
        orders,
        customers,
        engine
    )

    segment_analysis = sales_by_customer_segment(
        engine
    )

    cancellation_analysis = monthly_cancellation_ratio(
        engine
    )

    print("\n========== VENTAS POR SEGMENTO ==========\n")
    print(segment_analysis)

    print("\n========== RATIO DE CANCELACIONES ==========\n")
    print(cancellation_analysis)


if __name__ == "__main__":
    main()