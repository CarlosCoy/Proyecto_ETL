# ---------------------------------------------------------------------------
# Transform: preparación de DataFrames para SQL
# ---------------------------------------------------------------------------

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

NULL_VALUES = {
    "",
    "#N/A",
    "#NA",
    "N/A",
    "NA",
    "NULL",
    "NONE",
}


def normalize_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte valores que representan ausencia de información a None.

    Esto permite que posteriormente el SQL writer los inserte como NULL.
    """

    df = df.copy()

    for column in df.columns:

        df[column] = df[column].map(
            lambda value: (
                None
                if (
                    value is None
                    or pd.isna(value)
                    or (
                        isinstance(value, str)
                        and value.strip().upper() in NULL_VALUES
                    )
                )
                else value
            )
        )

    return df


def to_integer(series: pd.Series) -> pd.Series:
    """
    Convierte una serie a enteros anulables.
    """

    return pd.to_numeric(
        series,
        errors="coerce"
    ).astype("Int64")


def to_decimal(series: pd.Series) -> pd.Series:
    """
    Convierte una serie a valores numéricos decimales.
    """

    return pd.to_numeric(
        series,
        errors="coerce"
    )


def to_date(series: pd.Series) -> pd.Series:
    """
    Convierte una serie a fechas.

    Valores inválidos se convierten en NaT y posteriormente en None.
    """

    converted = pd.to_datetime(
        series,
        errors="coerce"
    )

    return converted.map(
        lambda value: (
            value.date()
            if pd.notna(value)
            else None
        )
    )


def to_boolean(series: pd.Series) -> pd.Series:
    """
    Convierte una columna de capacitación a boolean.

    Valores considerados TRUE:
        X
        SI
        SÍ
        TRUE
        1
        YES

    Cualquier otro valor no nulo se interpreta como FALSE.

    Valores nulos también se convierten en FALSE porque una celda vacía
    significa que el empleado no está marcado como capacitado.
    """

    true_values = {
        "X",
        "SI",
        "SÍ",
        "TRUE",
        "1",
        "YES",
    }

    return series.map(
        lambda value: (
            False
            if value is None or pd.isna(value)
            else (
                str(value).strip().upper()
                in true_values
            )
        )
    ).astype(bool)


def rename_if_exists(
    df: pd.DataFrame,
    mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Renombra únicamente las columnas que existan en el DataFrame.
    """

    existing_mapping = {
        source: target
        for source, target in mapping.items()
        if source in df.columns
    }

    return df.rename(
        columns=existing_mapping
    )


# ---------------------------------------------------------------------------
# ACTDB
# ---------------------------------------------------------------------------

def transform_actdb(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara ACTDB para SQL.
    """

    df = df.copy()

    # -----------------------------------------------------------------------
    # Nombres
    # -----------------------------------------------------------------------

    df = rename_if_exists(
        df,
        {
            "registro": "codigo_empleado",
        }
    )

    # -----------------------------------------------------------------------
    # Tipos
    # -----------------------------------------------------------------------

    if "codigo_empleado" in df.columns:
        df["codigo_empleado"] = to_integer(
            df["codigo_empleado"]
        )

    if "fecha_nacimiento" in df.columns:
        df["fecha_nacimiento"] = to_date(
            df["fecha_nacimiento"]
        )

    if "categoria" in df.columns:
        df["categoria"] = to_integer(
            df["categoria"]
        )

    if "ruta" in df.columns:
        df["ruta"] = to_integer(
            df["ruta"]
        )

    # -----------------------------------------------------------------------
    # Teléfono
    # -----------------------------------------------------------------------

    if "telefono" in df.columns:

        df["telefono"] = df["telefono"].map(
            lambda value: (
                None
                if pd.isna(value)
                else (
                    str(int(value))
                    if isinstance(
                        value,
                        (
                            int,
                            float,
                            np.integer,
                            np.floating,
                        )
                    )
                    and float(value).is_integer()
                    else str(value).strip()
                )
            )
        )

    # -----------------------------------------------------------------------
    # Nulls
    # -----------------------------------------------------------------------

    df = normalize_nulls(df)

    return df


# ---------------------------------------------------------------------------
# VAC
# ---------------------------------------------------------------------------

# Columnas de la tabla vac (ver sql_tables.py).
VAC_COLUMNS = [
    "codigo_empleado",
    "nombre",
    "maquina",
    "mes",
    "fecha_ingreso",
    "turno_actual",
    "vacaciones_dic",
    "tipo",
    "inicio_salida",
    "dias_a_tomar",
    "fin",
    "llegada",
    "observaciones",
    "mes_de_salida",
    "estado",
    "fecha",
    "dias",
]


def transform_vac(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara VAC para SQL.
    """

    df = df.copy()

    # -----------------------------------------------------------------------
    # Nombres
    # -----------------------------------------------------------------------

    df = rename_if_exists(
        df,
        {
            "registro": "codigo_empleado",
        }
    )

    # -----------------------------------------------------------------------
    # Enteros
    # -----------------------------------------------------------------------

    integer_columns = [
        "codigo_empleado",
        "mes",
        "turno_actual",
        "dias_a_tomar",
        "mes_de_salida",
    ]

    for column in integer_columns:

        if column in df.columns:

            df[column] = to_integer(
                df[column]
            )

    # -----------------------------------------------------------------------
    # Fechas
    # -----------------------------------------------------------------------

    date_columns = [
        "fecha_ingreso",
        "inicio_salida",
        "fin",
        "llegada",
        "fecha",
    ]

    for column in date_columns:

        if column in df.columns:

            df[column] = to_date(
                df[column]
            )

    # -----------------------------------------------------------------------
    # Decimales
    # -----------------------------------------------------------------------

    if "dias" in df.columns:

        df["dias"] = to_decimal(
            df["dias"]
        )

    # -----------------------------------------------------------------------
    # Columnas del modelo
    # -----------------------------------------------------------------------

    # La hoja trae además columnas sin encabezado y un calendario visual
    # (una columna vacía por día) que no forman parte de la tabla vac.
    df = df[[
        column
        for column in VAC_COLUMNS
        if column in df.columns
    ]]

    # -----------------------------------------------------------------------
    # Nulls
    # -----------------------------------------------------------------------

    df = normalize_nulls(df)

    return df


# ---------------------------------------------------------------------------
# POLIVALENCIA
# ---------------------------------------------------------------------------

# Columnas originales después de pasar por unique_names().
#
# El Excel original tiene nombres como:
#
#   117_OP_1
#   NOKIA 2/3
#   96 OP
#
# naming.py los transforma en:
#
#   col_117_op_1
#   nokia_2_3
#   col_96_op
#
# Aquí los convertimos al nombre que tendrá la tabla SQL.

POLIVALENCIA_COLUMN_MAPPING = {

    # -----------------------------------------------------------------------
    # Bloque 1
    # -----------------------------------------------------------------------

    "col_117_op_1": "117_OP_1",
    "col_118_op_1": "118_OP_1",
    "col_202_op_1": "202_OP_1",
    "col_202_ay_1": "202_AY_1",
    "col_203_op_1": "203_OP_1",
    "col_203_ay": "203_AY",
    "col_207_op_1": "207_OP_1",
    "col_208_op_1": "208_OP_1",
    "col_209_op_1": "209_OP_1",
    "bo1_op_1": "BO1_OP_1",
    "col_300_op_1": "300_OP_1",
    "col_300_ay_1": "300_AY_1",
    "col_301_op_1": "301_OP_1",
    "col_301_ay_1": "301_AY_1",
    "col_315_op_1": "315_OP_1",
    "col_315_ay_1": "315_AY_1",
    "col_316_op_1": "316_OP_1",
    "col_316_pl_1": "316_PL_1",
    "col_316_em_1": "316_EM_1",
    "col_323_op_1": "323_OP_1",
    "col_323_ay_1": "323_AY_1",
    "col_910_op_1": "910_OP_1",
    "col_429_op_1": "429_OP_1",
    "col_429_ay_1": "429_AY_1",
    "col_429_az_1": "429_AZ_1",
    "col_213_op_1": "213_OP_1",
    "col_213_o2_1": "213_O2_1",
    "col_224_op_1": "224_OP_1",
    "col_340_op_1": "340_OP_1",
    "col_341_op_1": "341_OP_1",
    "col_343_op_1": "343_OP_1",
    "utl_op_1": "UTL_OP_1",
    "tmc_op_1": "TMC_OP_1",
    "montacarga": "MONTACARGA",
    "mp": "MP",
    "desperdicio": "DESPERDICIO",
    "entregas": "ENTREGAS",
    "nokia_2_3": "NOKIA 2/3",

    # -----------------------------------------------------------------------
    # Bloque 2
    # -----------------------------------------------------------------------

    "col_94": "94",
    "col_96_op": "96 OP",
    "col_96_ayu": "96 AYU",
    "col_105": "105",
    "col_101": "101",
    "col_97": "97",
    "col_204_op": "204 OP",
    "col_204_ayu": "204 AYU",
    "col_205_op": "205 OP",
    "col_205_ayu": "205 AYU",
    "col_230": "230",
    "col_235": "235",
    "col_324_op": "324 OP",
    "col_324_ay": "324 AY",
    "col_482_op": "482 OP",
    "col_482_ay": "482 AY",
    "col_481_op": "481 OP",
    "col_481_ay": "481 AY",
    "col_318_op": "318 OP",
    "col_318_ay": "318 AY",
    "lp100": "LP100",
    "nokia_1": "NOKIA 1",
    "col_935_op": "935 OP",
    "col_935_ay": "935 AY",
    "col_260_op": "260 OP",
    "col_260_ay": "260 AY",
    "peeling": "PEELING",
    "col_729": "729",
    "col_136": "136",
    "col_137": "137",
    "col_443_op": "443 OP",
    "col_443_ay": "443 AY",
    "col_430": "430",
    "col_435": "435",
    "utillaje": "UTILLAJE",
    "tmc": "TMC",
    "entregas_2": "ENTREGAS 2",
    "m_prima": "M. PRIMA",
    "desperdicio_2": "DESPERDICIO 2",
    "montacarga_2": "MONTACARGA 2",

    # -----------------------------------------------------------------------
    # Bloque 3
    # -----------------------------------------------------------------------

    "col_132_op_1": "132_OP_1",
    "col_109_op_1": "109_OP_1",
    "col_150_op_1": "150_OP_1",
    "col_151_op_1": "151_OP_1",
    "col_99_op_1": "99_OP_1",
    "col_129_op_1": "129_OP_1",
    "col_130_op_1": "130_OP_1",
    "col_229_op_1": "229_OP_1",
    "col_234_op_1": "234_OP_1",
    "col_219_op_1": "219_OP_1",
    "col_225_op_1": "225_OP_1",
    "col_210_op_1": "210_OP_1",
    "col_233_op_1": "233_OP_1",
    "col_308_op_1": "308_OP_1",
    "col_310_op_1": "310_OP_1",
    "col_227_op_1": "227_OP_1",
    "col_227_ayu_1": "227_AYU_1",
    "col_321_op_1": "321_OP_1",
    "col_319_op_1": "319_OP_1",
    "col_302_op_1": "302_OP_1",
    "col_302_ayu_1": "302_AYU_1",
    "col_311_op_1": "311_OP_1",
    "col_311_ayu_1": "311_AYU_1",
    "col_1251_op_1": "1251_OP_1",
    "col_505_op_1": "505_OP_1",
    "col_506_op_1": "506_OP_1",
    "col_520_op_1": "520_OP_1",
    "col_533_op_1": "533_OP_1",
    "col_711_op_1": "711_OP_1",
    "col_509_op_1": "509_OP_1",
    "col_519_op_1": "519_OP_1",
    "col_708_op_1": "708_OP_1",
    "utl_op1": "UTL_OP1",
    "tmc_2": "TMC 2",
    "mp_2": "MP 2",
    "entrega": "ENTREGA",
    "desperdicio_3": "DESPERDICIO 3",
    "peeling_2": "PEELING 2",
    "montacargas": "MONTACARGAS",
}


def transform_polivalencia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara POLIVALENCIA para SQL.

    - cod -> codigo_empleado
    - planta -> INTEGER
    - Convierte X/vacío a boolean.
    - Renombra las columnas de capacidades.
    """

    df = df.copy()

    # -----------------------------------------------------------------------
    # Clave primaria
    # -----------------------------------------------------------------------

    df = rename_if_exists(
        df,
        {
            "cod": "codigo_empleado",
        }
    )

    if "codigo_empleado" in df.columns:

        df["codigo_empleado"] = to_integer(
            df["codigo_empleado"]
        )

    # -----------------------------------------------------------------------
    # Planta
    # -----------------------------------------------------------------------

    if "planta" in df.columns:

        df["planta"] = to_integer(
            df["planta"]
        )

    # -----------------------------------------------------------------------
    # Renombrar capacidades
    # -----------------------------------------------------------------------

    df = rename_if_exists(
        df,
        POLIVALENCIA_COLUMN_MAPPING
    )

    # -----------------------------------------------------------------------
    # Convertir capacidades a boolean
    # -----------------------------------------------------------------------

    boolean_columns = [
        column
        for column in df.columns
        if column not in {
            "codigo_empleado",
            "planta",
            "operador",
        }
    ]

    for column in boolean_columns:

        df[column] = to_boolean(
            df[column]
        )

    # -----------------------------------------------------------------------
    # Nulls
    # -----------------------------------------------------------------------

    df = normalize_nulls(
        df
    )

    return df


# ---------------------------------------------------------------------------
# CALENDARIO
# ---------------------------------------------------------------------------

def transform_calendario(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara CALENDARIO para SQL.

    Convierte la columna 'festivos' en:

        fecha
        anio
        mes
        dia

    'fecha' será la clave primaria de la tabla SQL.
    """

    df = df.copy()

    # -----------------------------------------------------------------------
    # Validar columna origen
    # -----------------------------------------------------------------------

    if "festivos" not in df.columns:

        raise ValueError(
            "La tabla calendario no contiene la columna 'festivos'."
        )

    # -----------------------------------------------------------------------
    # Convertir a fecha
    # -----------------------------------------------------------------------

    fechas = pd.to_datetime(
        df["festivos"],
        errors="coerce"
    )

    # -----------------------------------------------------------------------
    # Construir columnas
    # -----------------------------------------------------------------------

    df["fecha"] = fechas.dt.date
    df["anio"] = fechas.dt.year
    df["mes"] = fechas.dt.month
    df["dia"] = fechas.dt.day

    # -----------------------------------------------------------------------
    # Eliminar columna original
    # -----------------------------------------------------------------------

    df = df.drop(
        columns=["festivos"]
    )

    # -----------------------------------------------------------------------
    # Tipos
    # -----------------------------------------------------------------------

    df["anio"] = df["anio"].astype("Int64")
    df["mes"] = df["mes"].astype("Int64")
    df["dia"] = df["dia"].astype("Int64")

    # -----------------------------------------------------------------------
    # Eliminar fechas inválidas
    # -----------------------------------------------------------------------

    df = df.dropna(
        subset=[
            "fecha",
            "anio",
            "mes",
            "dia",
        ]
    )

    # -----------------------------------------------------------------------
    # Eliminar fechas duplicadas
    # -----------------------------------------------------------------------

    df = df.drop_duplicates(
        subset=["fecha"],
        keep="first"
    )

    # -----------------------------------------------------------------------
    # Orden de columnas
    # -----------------------------------------------------------------------

    df = df[
        [
            "fecha",
            "anio",
            "mes",
            "dia",
        ]
    ]

    return df.reset_index(
        drop=True
    )


# ---------------------------------------------------------------------------
# Transformación principal
# ---------------------------------------------------------------------------

TRANSFORMERS: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "actdb": transform_actdb,
    "vac": transform_vac,
    "polivalencia": transform_polivalencia,
    "calendario": transform_calendario,
}


def transform_for_sql(
    df: pd.DataFrame,
    table: str,
) -> pd.DataFrame:
    """
    Aplica la transformación específica de SQL según la tabla.

    Parámetros
    ----------
    df:
        DataFrame previamente procesado por clean_dataframe().

    table:
        Nombre normalizado de la tabla.

    Retorna
    -------
    pd.DataFrame
        DataFrame preparado para SQL.
    """

    table = table.strip().lower()

    if table not in TRANSFORMERS:

        raise ValueError(
            f"No existe una transformación SQL "
            f"para la tabla '{table}'."
        )

    transformed = TRANSFORMERS[table](
        df
    )

    return transformed.reset_index(
        drop=True
    )

