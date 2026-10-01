# ---------------------------------------------------------------------------
# Load: escritura de DataFrames en PostgreSQL mediante psycopg
# ---------------------------------------------------------------------------

from typing import Any

import pandas as pd

from etl.load.sql_tables import SQL_TABLES


PRIMARY_KEYS = {
    "actdb": ["codigo_empleado"],
    "vac": ["codigo_empleado", "inicio_salida"],
    "polivalencia": ["codigo_empleado"],
    "calendario": ["fecha"],
}


# tabla: (columna, tabla referenciada, columna referenciada)
FOREIGN_KEYS = {
    "vac": ("codigo_empleado", "actdb", "codigo_empleado"),
}

# Registros que se crean en la tabla referenciada cuando faltan, con las
# columnas indicadas (el resto queda NULL): en VAC hay operarios con labores
# administrativas que no figuran en ActDB, pero son empleados válidos.
COMPLETE_REFERENCED = {
    "vac": ["codigo_empleado", "nombre"],
}

# Motivo con el que se reporta una fila sin clave primaria cuando eso tiene
# un significado propio (por defecto: "sin clave primaria").
MISSING_KEY_REASONS = {
    "vac": "pendientes por programar (sin inicio_salida)",
}

# Orden de carga: una tabla referenciada se carga antes que quien la usa.
LOAD_ORDER = list(SQL_TABLES)


def quote_identifier(identifier: str) -> str:
    """
    Escapa un identificador SQL de PostgreSQL.

    Permite utilizar nombres de columnas como:

        "117_OP_1"
        "NOKIA 2/3"
        "96 OP"
        "M. PRIMA"
    """

    escaped = identifier.replace('"', '""')

    return f'"{escaped}"'


def python_value(value: Any) -> Any:
    """
    Convierte valores de pandas/numpy a tipos Python compatibles
    con psycopg.

    Los valores vacíos se convierten en None para representar
    SQL NULL.
    """

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass

    if hasattr(value, "to_pydatetime"):
        try:
            value = value.to_pydatetime()
        except (ValueError, TypeError):
            pass

    return value


def create_table(
    connection,
    table_name: str,
) -> None:
    """
    Crea la tabla utilizando la sentencia definida en sql_tables.py.
    """

    if table_name not in SQL_TABLES:
        raise ValueError(
            f"No existe definición SQL para la tabla: {table_name}"
        )

    sql = SQL_TABLES[table_name]

    cursor = connection.cursor()

    try:
        cursor.execute(sql)
    finally:
        cursor.close()


def insert_dataframe(
    connection,
    df: pd.DataFrame,
    table_name: str,
) -> int:
    """
    Inserta o actualiza los registros del DataFrame.

    Si la clave primaria ya existe, se actualizan los valores.
    Si no existe, se inserta un nuevo registro.

    Retorna el número de filas procesadas.
    """

    if df.empty:
        return 0

    if table_name not in SQL_TABLES:
        raise ValueError(
            f"No existe definición SQL para la tabla: {table_name}"
        )

    if table_name not in PRIMARY_KEYS:
        raise ValueError(
            f"No existe definición de clave primaria para: {table_name}"
        )

    primary_keys = PRIMARY_KEYS[table_name]

    missing_keys = [
        key
        for key in primary_keys
        if key not in df.columns
    ]

    if missing_keys:
        raise ValueError(
            f"La tabla '{table_name}' requiere las columnas "
            f"de clave primaria: {', '.join(missing_keys)}"
        )

    columns = list(df.columns)

    quoted_columns = ", ".join(
        quote_identifier(column)
        for column in columns
    )

    placeholders = ", ".join(
        "%s"
        for _ in columns
    )

    update_columns = [
        column
        for column in columns
        if column not in primary_keys
    ]

    if update_columns:

        update_clause = ", ".join(
            f"{quote_identifier(column)} = "
            f"EXCLUDED.{quote_identifier(column)}"
            for column in update_columns
        )

        conflict_columns = ", ".join(
            quote_identifier(key)
            for key in primary_keys
        )

        conflict_clause = (
            f"ON CONFLICT ({conflict_columns}) "
            f"DO UPDATE SET {update_clause}"
        )

    else:

        conflict_columns = ", ".join(
            quote_identifier(key)
            for key in primary_keys
        )

        conflict_clause = (
            f"ON CONFLICT ({conflict_columns}) "
            f"DO NOTHING"
        )

    sql = (
        f"INSERT INTO {quote_identifier(table_name)} "
        f"({quoted_columns}) "
        f"VALUES ({placeholders}) "
        f"{conflict_clause}"
    )

    cursor = connection.cursor()

    rows_processed = 0

    try:

        for row in df.itertuples(
            index=False,
            name=None,
        ):

            values = tuple(
                python_value(value)
                for value in row
            )

            cursor.execute(
                sql,
                values,
            )

            rows_processed += 1

    finally:

        cursor.close()

    return rows_processed


def discard_invalid_rows(
    connection,
    df: pd.DataFrame,
    table_name: str,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Separa las filas que la base rechazaría por sus llaves.

    - Sin valor en alguna columna de la clave primaria.
    - Con una llave foránea que no existe en la tabla referenciada.

    Retorna (filas válidas, {motivo: cantidad descartada}).
    """

    discarded = {}

    # Si falta una columna de la clave, insert_dataframe() lo reporta.
    primary_keys = [
        key
        for key in PRIMARY_KEYS.get(table_name, [])
        if key in df.columns
    ]

    missing_pk = df[primary_keys].isna().any(axis=1)

    if missing_pk.any():
        reason = MISSING_KEY_REASONS.get(table_name, "sin clave primaria")
        discarded[reason] = int(missing_pk.sum())
        df = df[~missing_pk]

    if table_name in FOREIGN_KEYS:

        column, ref_table, ref_column = FOREIGN_KEYS[table_name]

        cursor = connection.cursor()

        try:
            cursor.execute(
                f"SELECT {quote_identifier(ref_column)} "
                f"FROM {quote_identifier(ref_table)}"
            )
            existing = {row[0] for row in cursor.fetchall()}
        finally:
            cursor.close()

        missing_fk = (
            df[column].notna()
            & ~df[column].isin(existing)
        )

        if missing_fk.any():
            discarded[f"sin {column} en {ref_table}"] = int(missing_fk.sum())
            df = df[~missing_fk]

    return df, discarded


def complete_referenced_rows(
    connection,
    df: pd.DataFrame,
    table_name: str,
) -> int:
    """
    Crea en la tabla referenciada los registros que faltan (COMPLETE_REFERENCED).

    Si el registro ya existe, no se modifica: los datos completos de la
    tabla referenciada tienen prioridad.

    Retorna la cantidad de registros creados.
    """

    if table_name not in COMPLETE_REFERENCED:
        return 0

    column, ref_table, ref_column = FOREIGN_KEYS[table_name]

    columns = COMPLETE_REFERENCED[table_name]

    # Un registro por llave; la columna propia pasa a llamarse como la
    # referenciada.
    rows = (
        df[columns]
        .dropna(subset=[column])
        .drop_duplicates(subset=[column])
        .rename(columns={column: ref_column})
    )

    quoted_columns = ", ".join(
        quote_identifier(name)
        for name in rows.columns
    )

    placeholders = ", ".join(
        "%s"
        for _ in rows.columns
    )

    sql = (
        f"INSERT INTO {quote_identifier(ref_table)} "
        f"({quoted_columns}) "
        f"VALUES ({placeholders}) "
        f"ON CONFLICT ({quote_identifier(ref_column)}) DO NOTHING"
    )

    cursor = connection.cursor()

    created = 0

    try:

        for row in rows.itertuples(index=False, name=None):

            cursor.execute(
                sql,
                tuple(python_value(value) for value in row),
            )

            created += cursor.rowcount

    finally:
        cursor.close()

    return created


def write_sql(
    connection,
    df: pd.DataFrame,
    table_name: str,
) -> tuple[int, dict[str, int], int]:
    """
    Crea la tabla e inserta o actualiza el DataFrame.

    Retorna (filas procesadas, {motivo: filas descartadas},
    registros creados en la tabla referenciada).
    """

    create_table(
        connection,
        table_name,
    )

    created_referenced = complete_referenced_rows(
        connection,
        df,
        table_name,
    )

    df, discarded = discard_invalid_rows(
        connection,
        df,
        table_name,
    )

    rows_processed = insert_dataframe(
        connection,
        df,
        table_name,
    )

    connection.commit()

    return rows_processed, discarded, created_referenced