"""
run_pipeline.py
===============

Pipeline principal del proyecto.

Ejecuta automáticamente:

1. Generación de datos.
2. Carga en SQL Server.
3. Validación de la base de datos.

Proyecto:
    Sales Analytics Dashboard

Autor:
    Johnny Galicia
"""

from data_generator.generate_sales_data import generate_data
from database.load_data import load_database
from database.validate import validate_database
from pipeline.logger import logger

def run_pipeline():

    logger.info("Iniciando pipeline de automatización de análisis de ventas.")

    print("=" * 60)
    print("      SALES ANALYTICS AUTOMATION PIPELINE")
    print("=" * 60)

    # --------------------------------------------------------

    print("\n[1/3] Generando datasets...\n")
    logger.info("Generando datasets...")
    generate_data()

    print("\nDatasets generados correctamente.")
    logger.info("Datasets generados correctamente.")
    # --------------------------------------------------------

    print("\n[2/3] Cargando datos en SQL Server...\n")
    logger.info("Cargando datos en SQL Server...")

    load_database()

    print("\nBase de datos actualizada correctamente.")
    logger.info("Base de datos actualizada correctamente.")
    # --------------------------------------------------------

    print("\n[3/3] Validando carga...\n")
    logger.info("Validando carga de datos en SQL Server...")
    validate_database()

    print("\nValidación completada.")
    logger.info("Validación completada.")
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("PIPELINE FINALIZADO CORRECTAMENTE")
    print("Power BI está listo para actualizar.")
    print("=" * 60)
    logger.info("Pipeline finalizado correctamente.")


def main():

    run_pipeline()


if __name__ == "__main__":

    main()