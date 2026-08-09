"""
validate.py
===========

Valida la carga de datos en SQL Server.

Proyecto:
    Sales Analytics Dashboard

Autor:
    Johnny Galicia

Descripción:
    Consulta el número de registros de cada tabla
    para verificar que la carga fue exitosa.
"""

from database.connection import get_connection

# ============================================================
# TABLAS A VALIDAR
# ============================================================

TABLES = [
    "customers",
    "products",
    "orders",
    "order_items"
]


# ============================================================
# VALIDACIÓN
# ============================================================

def validate_database():

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        print("=" * 60)
        print("VALIDANDO BASE DE DATOS")
        print("=" * 60)

        for table in TABLES:

            query = f"SELECT COUNT(*) FROM {table}"

            cursor.execute(query)

            total = cursor.fetchone()[0]

            print(f"{table:15} -> {total:,} registros")

        print("=" * 60)
        print("Validación completada correctamente.")
        print("=" * 60)

    except Exception as error:

        print("\nError durante la validación:")
        print(error)

    finally:

        if connection:
            connection.close()


# ============================================================
# MAIN
# ============================================================

def main():

    validate_database()


if __name__ == "__main__":

    main()