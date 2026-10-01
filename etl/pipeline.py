# ---------------------------------------------------------------------------
# Pipeline: Extract → Transform → Load
# ---------------------------------------------------------------------------

import sys
from getpass import getpass
from pathlib import Path

import psycopg

from config import Config

from etl.extract.sheet_reader import extract_sheet
from etl.extract.workbook import open_workbook

from etl.load.csv_writer import write_csv
from etl.load.report import report_row, write_report
from etl.load.sql_writer import FOREIGN_KEYS, LOAD_ORDER, write_sql

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

    password = (
        Config.DB_PASSWORD
        or getpass("Ingrese la contraseña de la base de datos: ")
    )

    print("\nConectando a la base de datos...")

    try:

        connection = psycopg.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=password,
            sslmode="require",
            connect_timeout=15,
        )

        # Las tablas se crean y consultan dentro de DB_SCHEMA.
        cursor = connection.cursor()

        try:
            cursor.execute(
                f'CREATE SCHEMA IF NOT EXISTS "{Config.DB_SCHEMA}"'
            )
            cursor.execute(
                f'SET search_path TO "{Config.DB_SCHEMA}"'
            )
        finally:
            cursor.close()

        connection.commit()

        print(
            f"Conexión a base de datos establecida "
            f"(esquema {Config.DB_SCHEMA}).\n"
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

        # Las tablas referenciadas (actdb) se cargan antes que las que
        # dependen de ellas (vac), sin importar el orden de las pestañas.
        worksheets = sorted(
            wb.worksheets,
            key=lambda ws: (
                LOAD_ORDER.index(table_name(ws.title))
                if table_name(ws.title) in LOAD_ORDER
                else len(LOAD_ORDER)
            ),
        )

        for ws in worksheets:

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

                rows_processed, discarded, created_referenced = write_sql(
                    connection,
                    df,
                    table
                )

                if created_referenced:
                    print(
                        f"[INFO] {ws.title}: {created_referenced} "
                        f"registros creados en {FOREIGN_KEYS[table][1]}."
                    )

                print(
                    f"[OK]   SQL cargado:   "
                    f"{rows_processed} filas → {table}"
                )

                discarded_detail = "; ".join(
                    f"{count} {reason}"
                    for reason, count in discarded.items()
                )

                if discarded:
                    print(
                        f"[WARN] {ws.title}: filas no cargadas: "
                        f"{discarded_detail}"
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
                        filas_sql=rows_processed,
                        descartadas=discarded_detail,
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

                # Descarta la transacción fallida para que las demás hojas
                # puedan seguir cargándose.
                connection.rollback()

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