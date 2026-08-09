"""
connection.py
=============

Módulo encargado de administrar la conexión con SQL Server.

Proyecto:
    Sales Analytics Dashboard

Autor:
    Johnny Galicia

Descripción:
    Centraliza toda la configuración de conexión al servidor SQL Server.
    Cualquier otro módulo del proyecto debe importar la función
    get_connection() en lugar de crear conexiones directamente.
"""

import pyodbc


# ============================================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================================

SERVER = "localhost"
DATABASE = "SalesAnalytics"
DRIVER = "ODBC Driver 18 for SQL Server"


# ============================================================
# FUNCIÓN DE CONEXIÓN
# ============================================================

def get_connection():
    """
    Crea y devuelve una conexión abierta a SQL Server.

    Returns
    -------
    pyodbc.Connection
        Conexión activa a la base de datos.
    """

    connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    connection = pyodbc.connect(connection_string)

    return connection


# ============================================================
# PRUEBA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    try:

        conn = get_connection()

        print("=" * 50)
        print("Conexión establecida correctamente.")
        print(f"Servidor : {SERVER}")
        print(f"Base      : {DATABASE}")
        print("=" * 50)

        conn.close()

    except Exception as error:

        print("Error de conexión:")
        print(error)