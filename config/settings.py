# ---------------------------------------------------------------------------
# Configuración de la ETL
# ---------------------------------------------------------------------------

import os

from dotenv import load_dotenv


# Los datos de conexión se leen de .env (no se versiona), nunca del código.
load_dotenv()


class Config:

    # -----------------------------------------------------------------------
    # Archivos
    # -----------------------------------------------------------------------

    INPUT_FILE = (
        r"D:\Maestria\Semestre I\ETL\Proyecto\Datos"
        r"\Copia de S38_HORARIO_PROD_P1_2026.xlsm"
    )

    OUTPUT_DIR = (
        r"D:\Maestria\Semestre I\ETL\Proyecto\CSV"
    )

    # -----------------------------------------------------------------------
    # Hojas a procesar
    # -----------------------------------------------------------------------

    SHEETS_TO_PROCESS = {
        "VAC",
        "POLIVALENCIA",
        "CALENDARIO",
        "ACTDB",
    }

    # -----------------------------------------------------------------------
    # Detección de tablas
    # -----------------------------------------------------------------------

    MIN_HEADER_CELLS = 2
    MAX_SCAN_ROWS = 250
    MAX_SCAN_COLS = 150
    MIN_DATA_ROWS = 1

    # -----------------------------------------------------------------------
    # Excel
    # -----------------------------------------------------------------------

    KEEP_FORMULAS = False

    # -----------------------------------------------------------------------
    # Base de datos
    # -----------------------------------------------------------------------

    DB_HOST = os.getenv("DB_HOST", "TU_HOST")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "TU_BASE_DATOS")
    DB_USER = os.getenv("DB_USER", "TU_USUARIO")

    # Vacío = se pide por teclado al ejecutar.
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # Esquema propio: Supabase expone "public" por su API y reserva "etl".
    DB_SCHEMA = os.getenv("DB_SCHEMA", "project_etl")

