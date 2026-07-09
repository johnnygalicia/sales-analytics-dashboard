"""
sales_sql_summary.py

Valida las principales métricas de ventas utilizando SQLite,
SQLAlchemy y consultas SQL.

Métricas generadas:
- Total de órdenes
- Ingresos mensuales
- Ticket promedio

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


# ============================================================
# Persistencia en SQLite
# ============================================================

def load_orders_to_database(
    orders: pd.DataFrame,
    engine
) -> None:
    """
    Inserta las órdenes en SQLite.
    """

    orders.to_sql(
        "orders",
        engine,
        if_exists="replace",
        index=False
    )


# ============================================================
# Consulta SQL
# ============================================================

def monthly_sales_summary(engine) -> pd.DataFrame:
    """
    Calcula métricas mensuales utilizando SQL.
    """

    query = """
    SELECT
        strftime('%Y-%m', order_date) AS order_month,
        COUNT(order_id) AS total_orders,
        SUM(order_amount) AS revenue,
        AVG(order_amount) AS average_ticket
    FROM orders
    WHERE order_status = 'completed'
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

    load_orders_to_database(
        orders,
        engine
    )

    monthly_metrics = monthly_sales_summary(
        engine
    )

    print("\n========== MÉTRICAS MENSUALES (SQL) ==========\n")
    print(monthly_metrics)


if __name__ == "__main__":
    main()