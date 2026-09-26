# ---------------------------------------------------------------------------
# Extract: lectura de una hoja
# ---------------------------------------------------------------------------

import pandas as pd

from etl.extract.structured_tables import (
    dataframe_from_excel_table,
    get_structured_tables,
    table_area,
)
from etl.extract.table_detection import (
    dataframe_from_detected_block,
    detect_table_block,
)


def extract_sheet(
    ws,
    min_header_cells: int,
    max_scan_rows: int,
    max_scan_cols: int
) -> tuple[pd.DataFrame, str, str]:
    """
    Extrae la tabla principal de una hoja, sin limpiarla.

    Prioridad:

    1. Tabla estructurada de Excel.
    2. Detección automática de bloque.

    Retorna (dataframe, fuente, rango).
    """

    structured_tables = get_structured_tables(ws)

    if structured_tables:

        # Si hay varias tablas estructuradas,
        # se toma la de mayor superficie.
        table = max(
            structured_tables,
            key=table_area,
        )

        df = dataframe_from_excel_table(
            ws,
            table
        )

        source = (
            f"tabla_excel:{table.name}"
        )

        return (
            df,
            source,
            table.ref
        )

    block = detect_table_block(
        ws,
        max_scan_rows,
        max_scan_cols,
        min_header_cells
    )

    if block is None:
        return (
            pd.DataFrame(),
            "no_detectada",
            ""
        )

    df = dataframe_from_detected_block(
        ws,
        block
    )

    source = "deteccion_automatica"

    ref = (
        f"{ws.cell(block[0], block[1]).coordinate}:"
        f"{ws.cell(block[3], block[2]).coordinate}"
    )

    return (
        df,
        source,
        ref
    )
