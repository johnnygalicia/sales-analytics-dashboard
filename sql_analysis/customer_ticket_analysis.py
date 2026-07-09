"""
customer_ticket_analysis.py

Identifica clientes cuyo ticket promedio supera
el ticket promedio global utilizando subconsultas SQL.

Consultas incluidas:
- Ticket promedio global.
- Clientes con ticket promedio superior al promedio general.

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
    Inserta las tablas en SQLite.
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
# Ticket promedio global
# ============================================================

def global_average_ticket(engine) -> float:
    """
    Calcula el ticket promedio global.
    """

    query = """
    SELECT
        AVG(order_amount) AS global_average_ticket
    FROM orders
    WHERE order_status = 'completed';
    """

    result = pd.read_sql_query(query, engine)

    return float(result.loc[0, "global_average_ticket"])    


# ============================================================
# Consulta 2
# Clientes con ticket superior al promedio
# ============================================================

def customers_above_average_ticket(engine) -> pd.DataFrame:
    """
    Identifica los clientes cuyo ticket promedio
    supera el promedio global.
    """

    query = """
    SELECT
        c.customer_id,
        c.customer_segment,
        COUNT(o.order_id) AS total_orders,
        AVG(o.order_amount) AS average_customer_ticket
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    WHERE o.order_status = 'completed'
    GROUP BY
        c.customer_id,
        c.customer_segment
    HAVING AVG(o.order_amount) >
    (
        SELECT AVG(order_amount)
        FROM orders
        WHERE order_status = 'completed'
    )
    ORDER BY average_customer_ticket DESC;
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

    global_ticket = global_average_ticket(
        engine
    )

    customers_analysis = customers_above_average_ticket(
        engine
    )

    print("\n========== TICKET PROMEDIO GLOBAL ==========\n")
    print(f"${global_ticket:.2f}")

    print("\n========== CLIENTES SOBRE EL PROMEDIO ==========\n")
    print(customers_analysis)

    print("\n========== RESUMEN ==========\n")
    print(f"Ticket promedio global: ${global_ticket:.2f}")
    print(
        f"Clientes por encima del promedio: "
        f"{len(customers_analysis)}"
    )


if __name__ == "__main__":
    main()