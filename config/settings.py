# ---------------------------------------------------------------------------
# Configuración de la ETL
# ---------------------------------------------------------------------------

from pathlib import Path

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

    DB_HOST = "TU_HOST"
    DB_PORT = 5432
    DB_NAME = "TU_BASE_DATOS"
    DB_USER = "TU_USUARIO"

    DB_DRIVER = "org.postgresql.Driver"

    DB_URL = (
        f"jdbc:postgresql://"
        f"{DB_HOST}:{DB_PORT}/"
        f"{DB_NAME}"
    )

    DB_JAR = (
        Path(__file__).resolve().parent
        / "lib"
        / "postgresql-42.7.13.jar"
    )