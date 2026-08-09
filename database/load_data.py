"""
load_data.py
============

Carga los archivos CSV del proyecto.

Versión 1:
    - Detecta automáticamente los archivos.
    - Verifica que existan.
    - Los carga en DataFrames.
"""

from pathlib import Path

import pandas as pd
from database.connection import get_connection

# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_FOLDER = PROJECT_ROOT / "datasets"


CSV_FILES = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv"
}


# ============================================================
# CARGAR DATASETS
# ============================================================

def load_csv_files():

    dataframes = {}

    print("=" * 60)
    print("BUSCANDO DATASETS")
    print("=" * 60)

    for table_name, filename in CSV_FILES.items():

        filepath = DATASET_FOLDER / filename

        if not filepath.exists():
            raise FileNotFoundError(f"No existe: {filepath}")

        dataframe = pd.read_csv(filepath)

        dataframes[table_name] = dataframe

        print(f"{filename:20} -> {len(dataframe):,} registros")

    print("=" * 60)

    return dataframes

# ============================================================
# LIMPIAR TABLA
# ===========================================================
def clear_tables():

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        print("\nLimpiando tablas...")

        tables = [
            "order_items",
            "orders",
            "products",
            "customers"
        ]

        for table in tables:

            cursor.execute(f"DELETE FROM {table}")

            print(f"{table:15} limpiada.")

        connection.commit()

        print("Todas las tablas fueron limpiadas.\n")

    finally:

        if connection:
            connection.close()

# ============================================================
# CARGAR DATAFRAME EN TABLA 
# ===========================================================

def load_table(table_name: str, dataframe):

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.fast_executemany = True

        print(f"\nInsertando {table_name}...")

        columns = list(dataframe.columns)

        columns_sql = ", ".join(columns)

        placeholders = ", ".join(["?"] * len(columns))

        query = f"""
            INSERT INTO {table_name}
            ({columns_sql})
            VALUES ({placeholders})
        """

        data = list(dataframe.itertuples(index=False, name=None))

        cursor.executemany(query, data)

        connection.commit()

        print(f"{len(data):,} registros insertados.")

    except Exception as error:

        print(f"\nError cargando {table_name}")
        print(error)

    finally:

        if connection:
            connection.close()
# ============================================================
# LOAD DATABASE
# ============================================================

def load_database():

    datasets = load_csv_files()

    clear_tables()
    
    load_order = [
        "customers",
        "products",
        "orders",
        "order_items"
    ]

    for table_name in load_order:

        load_table(
            table_name, 
            datasets[table_name]
        )
        
    print("\nCarga de datos finalizada .")

def main():

    load_database()

if __name__ == "__main__":
    main()