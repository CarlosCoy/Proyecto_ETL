from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from config import Config
from utils import process_sheet, table_name


def main():

    input_path = Path(
        Config.INPUT_FILE
    ).expanduser().resolve()

    output_path = Path(
        Config.OUTPUT_DIR
    ).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {input_path}"
        )

    if input_path.suffix.lower() not in {
        ".xlsx",
        ".xlsm"
    }:
        raise ValueError(
            "El archivo debe ser .xlsx o .xlsm"
        )

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    wb = load_workbook(
        input_path,
        read_only=False,
        data_only=not Config.KEEP_FORMULAS,
    )

    report = []

    print(
        f"\nExcel origen: {input_path}"
    )

    print(
        f"Salida:       {output_path}"
    )

    print(
        f"Hojas:        {len(wb.worksheets)}\n"
    )

    for ws in wb.worksheets:

        try:

            df, source, detected_range = process_sheet(
                ws,
                Config.MIN_HEADER_CELLS,
                Config.MAX_SCAN_ROWS,
                Config.MAX_SCAN_COLS
            )

            table = table_name(
                ws.title
            )

            output_file = (
                output_path /
                f"{table}.csv"
            )

            if df.empty:

                report.append({
                    "hoja": ws.title,
                    "tabla": table,
                    "fuente": source,
                    "rango": detected_range,
                    "filas": 0,
                    "columnas": 0,
                    "estado": "SIN_DATOS",
                    "archivo": output_file.name,
                })

                print(
                    f"[WARN] {ws.title}: "
                    "no se detectaron datos."
                )

                continue

            # ---------------------------------------------------------------
            # Exportación CSV
            # ---------------------------------------------------------------

            df.to_csv(
                output_file,
                index=False,
                na_rep="",
                encoding="utf-8-sig",
            )

            report.append({
                "hoja": ws.title,
                "tabla": table,
                "fuente": source,
                "rango": detected_range,
                "filas": len(df),
                "columnas": len(df.columns),
                "estado": "OK",
                "archivo": output_file.name,
            })

            print(
                f"[OK]   {ws.title:<25} "
                f"{len(df):>6} filas x "
                f"{len(df.columns):>3} columnas "
                f"| {source:<24} "
                f"| {detected_range}"
            )

        except Exception as exc:

            report.append({
                "hoja": ws.title,
                "tabla": table_name(ws.title),
                "fuente": "",
                "rango": "",
                "filas": 0,
                "columnas": 0,
                "estado": f"ERROR: {exc}",
                "archivo": "",
            })

            print(
                f"[ERROR] {ws.title}: {exc}",
                file=sys.stderr
            )

    # -----------------------------------------------------------------------
    # Generar reporte
    # -----------------------------------------------------------------------

    report_df = pd.DataFrame(
        report
    )

    report_file = (
        output_path /
        "_etl_report.csv"
    )

    report_df.to_csv(
        report_file,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"\nReporte generado: {report_file}"
    )

    print(
        "ETL finalizada."
    )


if __name__ == "__main__":
    main()