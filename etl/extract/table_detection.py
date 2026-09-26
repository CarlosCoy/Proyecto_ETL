# ---------------------------------------------------------------------------
# Extract: detección automática de tablas
# ---------------------------------------------------------------------------
#
# Se usa cuando la hoja no tiene una tabla estructurada de Excel.
# Busca la fila con más probabilidad de ser encabezado y delimita
# el bloque de datos que hay debajo.

import math
import re

import numpy as np
import pandas as pd

from etl.utils.cells import is_empty


def row_values(
    ws,
    row_number: int,
    max_col: int
) -> list:

    return [
        ws.cell(
            row=row_number,
            column=col
        ).value
        for col in range(1, max_col + 1)
    ]


def nonempty_positions(
    values: list
) -> list[int]:

    return [
        i
        for i, value in enumerate(values)
        if not is_empty(value)
    ]


def looks_like_header(
    ws,
    row_number: int,
    max_col: int,
    min_header_cells: int
) -> tuple[float, int]:
    """
    Puntúa una fila como posible encabezado.

    La heurística considera:

    - cantidad de celdas ocupadas;
    - cantidad de textos;
    - fórmulas;
    - existencia de datos debajo;
    - repetición de encabezados;
    - palabras que suelen aparecer en nombres de columnas.
    """

    values = row_values(
        ws,
        row_number,
        max_col
    )

    positions = nonempty_positions(values)

    if len(positions) < min_header_cells:
        return -math.inf, 0

    text_count = sum(
        isinstance(values[i], str)
        for i in positions
    )

    formula_count = sum(
        isinstance(values[i], str)
        and values[i].startswith("=")
        for i in positions
    )

    avg_len = (
        np.mean(
            [
                len(str(values[i]).strip())
                for i in positions
            ]
        )
        if positions
        else 0
    )

    score = 0.0

    text_ratio = (
        text_count /
        max(len(positions), 1)
    )

    score += text_ratio * 30.0

    score += min(
        len(positions),
        25
    ) * 1.5

    score -= formula_count * 5.0

    if avg_len > 80:
        score -= 4

    overlap_scores = []

    repeated_header_text = 0
    comparable_columns = 0

    for next_row in range(
        row_number + 1,
        min(
            row_number + 6,
            ws.max_row + 1
        )
    ):

        next_values = row_values(
            ws,
            next_row,
            max_col
        )

        overlap = sum(
            not is_empty(next_values[i])
            for i in positions
        )

        overlap_scores.append(
            overlap /
            max(len(positions), 1)
        )

        for i in positions:

            if (
                isinstance(values[i], str)
                and not values[i].startswith("=")
            ):

                comparable_columns += 1

                if (
                    isinstance(next_values[i], str)
                    and
                    next_values[i].strip().casefold()
                    ==
                    values[i].strip().casefold()
                ):
                    repeated_header_text += 1

    if overlap_scores:
        score += max(overlap_scores) * 12.0

    if comparable_columns:

        repetition_ratio = (
            repeated_header_text /
            comparable_columns
        )

        score -= repetition_ratio * 25.0

    header_keyword_pattern = re.compile(
        r"(id|codigo|cod|nombre|fecha|registro|"
        r"telefono|direccion|turno|puesto|maquina|"
        r"cargo|estado|tipo|valor|cantidad|empresa|"
        r"categoria|proceso|semana|dia|ruta|planta)",
        re.IGNORECASE,
    )

    keyword_hits = sum(
        bool(
            header_keyword_pattern.search(
                str(values[i])
            )
        )
        for i in positions
        if isinstance(values[i], str)
    )

    score += keyword_hits * 3.0

    return score, len(positions)


def detect_table_block(
    ws,
    max_scan_rows: int,
    max_scan_cols: int,
    min_header_cells: int
) -> tuple[int, int, int, int] | None:
    """
    Detecta una única tabla principal cuando la hoja
    no tiene una tabla estructurada de Excel.

    Retorna:

        (
            header_row,
            first_col,
            last_col,
            last_row
        )
    """

    scan_rows = min(
        ws.max_row,
        max_scan_rows
    )

    scan_cols = min(
        ws.max_column,
        max_scan_cols
    )

    candidates = []

    for row in range(
        1,
        scan_rows + 1
    ):

        score, count = looks_like_header(
            ws,
            row,
            scan_cols,
            min_header_cells
        )

        if score == -math.inf:
            continue

        positions = nonempty_positions(
            row_values(
                ws,
                row,
                scan_cols
            )
        )

        if not positions:
            continue

        first_col = min(positions) + 1
        last_col = max(positions) + 1

        candidates.append(
            (
                score,
                count,
                row,
                first_col,
                last_col
            )
        )

    if not candidates:
        return None

    candidates.sort(reverse=True)

    (
        _,
        header_count,
        header_row,
        first_col,
        last_col
    ) = candidates[0]

    if header_count < min_header_cells:
        return None

    last_row = header_row
    empty_streak = 0

    for row in range(
        header_row + 1,
        ws.max_row + 1
    ):

        values = [
            ws.cell(
                row=row,
                column=col
            ).value
            for col in range(
                first_col,
                last_col + 1
            )
        ]

        if all(
            is_empty(v)
            for v in values
        ):

            empty_streak += 1

            if empty_streak >= 3:
                break

            continue

        empty_streak = 0
        last_row = row

    if last_row <= header_row:
        return None

    return (
        header_row,
        first_col,
        last_col,
        last_row
    )


def dataframe_from_detected_block(
    ws,
    block
) -> pd.DataFrame:
    """Construye un DataFrame (sin limpiar) desde un bloque detectado."""

    (
        header_row,
        first_col,
        last_col,
        last_row
    ) = block

    rows = []

    for row in ws.iter_rows(
        min_row=header_row,
        max_row=last_row,
        min_col=first_col,
        max_col=last_col,
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
