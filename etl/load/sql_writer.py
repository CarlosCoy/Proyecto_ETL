# ---------------------------------------------------------------------------
# Load: escritura de DataFrames en PostgreSQL mediante JDBC
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
    con JDBC/JayDeBeApi.

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
        "?"
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


def write_sql(
    connection,
    df: pd.DataFrame,
    table_name: str,
) -> int:
    """
    Crea la tabla e inserta o actualiza el DataFrame.

    Retorna el número de filas procesadas.
    """

    create_table(
        connection,
        table_name,
    )

    rows_processed = insert_dataframe(
        connection,
        df,
        table_name,
    )

    connection.commit()

    return rows_processed