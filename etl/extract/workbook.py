# ---------------------------------------------------------------------------
# Extract: apertura del libro de Excel
# ---------------------------------------------------------------------------

from pathlib import Path

from openpyxl import load_workbook


VALID_EXTENSIONS = {
    ".xlsx",
    ".xlsm"
}


def open_workbook(
    input_path: Path,
    keep_formulas: bool
):
    """Valida la ruta y abre el libro de Excel."""

    if not input_path.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {input_path}"
        )

    if input_path.suffix.lower() not in VALID_EXTENSIONS:
        raise ValueError(
            "El archivo debe ser .xlsx o .xlsm"
        )

    return load_workbook(
        input_path,
        read_only=False,
        data_only=not keep_formulas,
    )
