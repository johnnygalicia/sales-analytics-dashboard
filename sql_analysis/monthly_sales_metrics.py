"""
monthly_sales_metrics.py

Calcula métricas mensuales de ventas utilizando Pandas.

Métricas generadas:
- Total de órdenes
- Ingresos mensuales
- Ticket promedio

Autor: Johnny M. Galicia O.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# Configuración de rutas
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datasets"


# ============================================================
# Carga de datos
# ============================================================

def load_orders() -> pd.DataFrame:
    """
    Carga el conjunto de datos de órdenes.

    Returns
    -------
    pd.DataFrame
        DataFrame con las órdenes de venta.
    """
    orders = pd.read_csv(
        DATA_DIR / "orders.csv",
        parse_dates=["order_date"]
    )

    return orders


# ============================================================
# Preparación de datos
# ============================================================

def prepare_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara el conjunto de datos para el análisis.

    - Conserva únicamente órdenes completadas.
    - Crea la columna del periodo mensual.

    Parameters
    ----------
    orders : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """

    orders = orders.loc[
        orders["order_status"] == "completed"
    ].copy()

    orders["order_month"] = (
        orders["order_date"]
        .dt
        .to_period("M")
    )

    return orders


# ============================================================
# Métricas mensuales
# ============================================================

def calculate_monthly_sales_metrics(
    orders: pd.DataFrame
) -> pd.DataFrame:
    """
    Calcula los principales indicadores mensuales de ventas.
    """

    monthly_metrics = (
        orders
        .groupby("order_month")
        .agg(
            total_orders=("order_id", "count"),
            revenue=("order_amount", "sum"),
            average_ticket=("order_amount", "mean")
        )
        .reset_index()
        .sort_values("order_month")
    )

    return monthly_metrics


# ============================================================
# Programa principal
# ============================================================

def main():

    orders = load_orders()

    orders = prepare_orders(orders)

    monthly_metrics = calculate_monthly_sales_metrics(
        orders
    )

    print("\n========== MÉTRICAS MENSUALES ==========\n")
    print(monthly_metrics)


if __name__ == "__main__":
    main()