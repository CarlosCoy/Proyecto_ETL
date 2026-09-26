# ---------------------------------------------------------------------------
# Extract: tablas estructuradas de Excel
# ---------------------------------------------------------------------------

import pandas as pd
from openpyxl.utils.cell import range_boundaries


def get_structured_tables(ws):
    """Obtiene las tablas estructuradas de una hoja."""

    return list(ws.tables.values())


def table_area(table) -> int:
    """Cantidad de celdas que ocupa una tabla estructurada."""

    min_col, min_row, max_col, max_row = (
        range_boundaries(table.ref)
    )

    return (
        (max_col - min_col + 1)
        *
        (max_row - min_row + 1)
    )


def dataframe_from_excel_table(
    ws,
    table
) -> pd.DataFrame:
    """
    Lee exactamente el rango de una tabla estructurada (sin limpiar).

    La primera fila del rango se considera encabezado.
    """

    min_col, min_row, max_col, max_row = (
        range_boundaries(table.ref)
    )

    rows = []

    for row in ws.iter_rows(
        min_row=min_row,
        max_row=max_row,
        min_col=min_col,
        max_col=max_col,
        values_only=True,
    ):
        rows.append(list(row))

    if not rows:
        return pd.DataFrame()

    header = rows[0]
    data = rows[1:]

    return pd.DataFrame(
        data,
        columns=header
    )
