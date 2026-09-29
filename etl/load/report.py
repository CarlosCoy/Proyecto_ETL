# ---------------------------------------------------------------------------
# Load: reporte de ejecución
# ---------------------------------------------------------------------------

from pathlib import Path

import pandas as pd


REPORT_FILE_NAME = "_etl_report.csv"


def report_row(
    hoja: str,
    tabla: str,
    fuente: str = "",
    rango: str = "",
    filas: int = 0,
    columnas: int = 0,
    estado: str = "OK",
    archivo: str = "",
    filas_sql: int = 0,
    descartadas: str = "",
) -> dict:
    """Construye una fila del reporte para una hoja."""

    return {
        "hoja": hoja,
        "tabla": tabla,
        "fuente": fuente,
        "rango": rango,
        "filas": filas,
        "columnas": columnas,
        "estado": estado,
        "archivo": archivo,
        "filas_sql": filas_sql,
        "descartadas": descartadas,
    }


def write_report(
    report: list[dict],
    output_path: Path
) -> Path:
    """Guarda el reporte en la carpeta de salida y devuelve su ruta."""

    report_file = (
        output_path /
        REPORT_FILE_NAME
    )

    pd.DataFrame(report).to_csv(
        report_file,
        index=False,
        encoding="utf-8-sig",
    )

    return report_file
