"""
logger.py
=========

Configuración del sistema de logging del proyecto.

Proyecto:
    Sales Analytics Dashboard
"""

import logging
from pathlib import Path


# ============================================================
# CREAR CARPETA LOGS SI NO EXISTE
# ============================================================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"


# ============================================================
# CONFIGURACIÓN
# ============================================================

logging.basicConfig(

    filename=LOG_FILE,

    level=logging.INFO,

    format="%(asctime)s | %(levelname)-8s | %(message)s",

    datefmt="%Y-%m-%d %H:%M:%S",

    filemode="a"
)


logger = logging.getLogger(__name__)