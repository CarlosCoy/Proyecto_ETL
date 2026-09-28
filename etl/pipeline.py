# ---------------------------------------------------------------------------
# Pipeline: Extract → Transform → Load
# ---------------------------------------------------------------------------

import sys
from getpass import getpass
from pathlib import Path

import jaydebeapi

from config import Config

from etl.extract.sheet_reader import extract_sheet
from etl.extract.workbook import open_workbook

from etl.load.csv_writer import write_csv
from etl.load.report import report_row, write_report
from etl.load.sql_writer import write_sql

from etl.transform.cleaning import clean_dataframe
from etl.transform.naming import table_name
from etl.transform.sql_transform import transform_for_sql


def run_etl(
    input_path: Path,
    output_path: Path,
    keep_formulas: bool,
    min_header_cells: int,
    max_scan_rows: int,
    max_scan_cols: int,
    sheets_to_process: set[str],
) -> Path:
    """
    Ejecuta la ETL únicamente sobre las hojas configuradas.

    Flujo:

        Excel
          ↓
        Extract
          ↓
        Cleaning
          ↓
        Transformación SQL
          ↓
        CSV
          ↓
        PostgreSQL
          ↓
        UPSERT

    Genera un CSV por cada hoja procesada más el reporte.

    Retorna la ruta del reporte generado.
    """

    # -----------------------------------------------------------------------
    # Conexión a base de datos
    # -----------------------------------------------------------------------

    password = getpass(
        "Ingrese la contraseña de la base de datos: "
    )

    print("\nConectando a la base de datos...")

    try:

        connection = jaydebeapi.connect(
            Config.DB_DRIVER,
            Config.DB_URL,
            [
                Config.DB_USER,
                password,
            ],
            [str(Config.DB_JAR)],
        )

        print(
            "Conexión a base de datos establecida.\n"
        )

    except Exception as exc:

        print(
            f"[ERROR] No fue posible conectar a la base de datos: {exc}",
            file=sys.stderr
        )

        raise

    # -----------------------------------------------------------------------
    # Abrir workbook
    # -----------------------------------------------------------------------

    wb = open_workbook(
        input_path,
        keep_formulas
    )

    # -----------------------------------------------------------------------
    # Normalizar nombres de hojas configuradas
    # -----------------------------------------------------------------------

    sheets_to_process = {
        sheet.strip().upper()
        for sheet in sheets_to_process
    }

    # -----------------------------------------------------------------------
    # Crear directorio de salida
    # -----------------------------------------------------------------------

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    report = []

    # -----------------------------------------------------------------------
    # Información inicial
    # -----------------------------------------------------------------------

    print(
        f"\nExcel origen: {input_path}"
    )

    print(
        f"Salida:       {output_path}"
    )

    print(
        f"Hojas Excel:  {len(wb.worksheets)}"
    )

    print(
        f"Hojas filtro: {', '.join(sorted(sheets_to_process))}\n"
    )

    try:

        # ===================================================================
        # Procesamiento de hojas
        # ===================================================================

        for ws in wb.worksheets:

            # ---------------------------------------------------------------
            # Filtro de hojas
            # ---------------------------------------------------------------

            if ws.title.strip().upper() not in sheets_to_process:

                print(
                    f"[SKIP] {ws.title}: hoja fuera del filtro."
                )

                continue

            # ---------------------------------------------------------------
            # Nombre de tabla
            # ---------------------------------------------------------------

            table = table_name(
                ws.title
            )

            try:

                # ===========================================================
                # EXTRACT
                # ===========================================================

                raw_df, source, detected_range = extract_sheet(
                    ws,
                    min_header_cells,
                    max_scan_rows,
                    max_scan_cols
                )

                # ===========================================================
                # TRANSFORM - Limpieza genérica
                # ===========================================================

                df = clean_dataframe(
                    raw_df
                )

                # ===========================================================
                # TRANSFORM - Adaptación al modelo SQL
                # ===========================================================

                df = transform_for_sql(
                    df,
                    table
                )

                # -----------------------------------------------------------
                # Archivo CSV
                # -----------------------------------------------------------

                output_file = (
                    output_path /
                    f"{table}.csv"
                )

                # -----------------------------------------------------------
                # Validar si quedaron datos
                # -----------------------------------------------------------

                if df.empty:

                    report.append(
                        report_row(
                            hoja=ws.title,
                            tabla=table,
                            fuente=source,
                            rango=detected_range,
                            estado="SIN_DATOS",
                            archivo=output_file.name,
                        )
                    )

                    print(
                        f"[WARN] {ws.title}: "
                        "no se detectaron datos."
                    )

                    continue

                # ===========================================================
                # LOAD - CSV
                # ===========================================================

                write_csv(
                    df,
                    output_file
                )

                print(
                    f"[OK]   CSV generado: {output_file.name}"
                )

                # ===========================================================
                # LOAD - PostgreSQL
                # ===========================================================

                rows_processed = write_sql(
                    connection,
                    df,
                    table
                )

                print(
                    f"[OK]   SQL cargado:   "
                    f"{rows_processed} filas → {table}"
                )

                # -----------------------------------------------------------
                # Reporte
                # -----------------------------------------------------------

                report.append(
                    report_row(
                        hoja=ws.title,
                        tabla=table,
                        fuente=source,
                        rango=detected_range,
                        filas=len(df),
                        columnas=len(df.columns),
                        estado="OK",
                        archivo=output_file.name,
                    )
                )

                print(
                    f"[OK]   {ws.title:<25} "
                    f"{len(df):>6} filas x "
                    f"{len(df.columns):>3} columnas "
                    f"| {source:<24} "
                    f"| {detected_range}"
                )

            except Exception as exc:

                report.append(
                    report_row(
                        hoja=ws.title,
                        tabla=table,
                        estado=f"ERROR: {exc}",
                    )
                )

                print(
                    f"[ERROR] {ws.title}: {exc}",
                    file=sys.stderr
                )

    finally:

        # -------------------------------------------------------------------
        # Cerrar conexión
        # -------------------------------------------------------------------

        connection.close()

        print(
            "\nConexión a base de datos cerrada."
        )

    # -----------------------------------------------------------------------
    # Generar reporte
    # -----------------------------------------------------------------------

    report_file = write_report(
        report,
        output_path
    )

    print(
        f"\nReporte generado: {report_file}"
    )

    print(
        "ETL finalizada."
    )

    return report_file