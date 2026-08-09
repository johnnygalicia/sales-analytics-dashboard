"""
test_connection.py
==================

Realiza una consulta sencilla a SQL Server para verificar
que la comunicación entre Python y la base de datos funciona.

Proyecto:
    Sales Analytics Dashboard
"""

from connection import get_connection


def main():

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                DB_NAME() AS database_name,
                @@SERVERNAME AS server_name,
                GETDATE() AS current_datetime 
        """)

        result = cursor.fetchone()

        server_name = result[1]
        database_name = result[0]
        current_datetime = result[2]

        print("=" * 60)
        print("CONEXIÓN EXITOSA")
        print("=" * 60)
        print(f"Servidor      : {server_name}")
        print(f"Base de datos : {database_name}")
        print(f"Fecha         : {current_datetime}")
        print("=" * 60)

    except Exception as error:

        print("ERROR")
        print(error)

    finally:

        if connection:
            connection.close()
            print("\nConexión cerrada.")


if __name__ == "__main__":
    main()