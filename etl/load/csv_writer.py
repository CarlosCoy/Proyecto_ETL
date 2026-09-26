# ---------------------------------------------------------------------------
# Load: exportación a CSV
# ---------------------------------------------------------------------------

from pathlib import Path

import pandas as pd


def write_csv(
    df: pd.DataFrame,
    output_file: Path
) -> None:
    """Escribe un DataFrame como CSV (UTF-8 con BOM, vacíos sin texto)."""

    df.to_csv(
        output_file,
        index=False,
        na_rep="",
        encoding="utf-8-sig",
    )
