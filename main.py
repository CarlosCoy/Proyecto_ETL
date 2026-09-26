from __future__ import annotations

import argparse
from pathlib import Path

from config import Config
from etl.pipeline import run_etl


def parse_args() -> argparse.Namespace:
    """Argumentos de línea de comandos (por defecto, los de config)."""

    parser = argparse.ArgumentParser(
        description="ETL Excel -> CSV: un CSV por cada hoja del libro."
    )

    parser.add_argument(
        "--input",
        default=Config.INPUT_FILE,
        help="Ruta del Excel de entrada (.xlsx / .xlsm).",
    )

    parser.add_argument(
        "--output",
        default=Config.OUTPUT_DIR,
        help="Carpeta donde se generarán los CSV.",
    )

    parser.add_argument(
        "--keep-formulas",
        action="store_true",
        default=Config.KEEP_FORMULAS,
        help="Conservar las fórmulas como texto en lugar de su valor.",
    )

    return parser.parse_args()


def main():

    args = parse_args()

    run_etl(
        input_path=Path(args.input).expanduser().resolve(),
        output_path=Path(args.output).expanduser().resolve(),
        keep_formulas=args.keep_formulas,
        min_header_cells=Config.MIN_HEADER_CELLS,
        max_scan_rows=Config.MAX_SCAN_ROWS,
        max_scan_cols=Config.MAX_SCAN_COLS,
        sheets_to_process=Config.SHEETS_TO_PROCESS,
    )


if __name__ == "__main__":
    main()
