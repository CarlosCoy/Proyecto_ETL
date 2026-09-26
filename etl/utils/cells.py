# ---------------------------------------------------------------------------
# Utilidades de celdas
# ---------------------------------------------------------------------------

import pandas as pd


def is_empty(value) -> bool:
    """Determina si una celda debe considerarse vacía."""

    if value is None:
        return True

    if isinstance(value, str):
        return value.strip() == ""

    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False
