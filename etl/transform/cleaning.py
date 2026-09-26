# ---------------------------------------------------------------------------
# Transform: limpieza de datos
# ---------------------------------------------------------------------------

import numpy as np
import pandas as pd

from etl.transform.naming import unique_names


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia encabezados, espacios y representa vacíos como NaN."""

    df = df.copy()

    df.columns = unique_names(df.columns)

    # Cadenas vacías/espacios -> NaN
    for column in df.columns:

        if pd.api.types.is_object_dtype(df[column]):

            df[column] = df[column].map(
                lambda x:
                    np.nan
                    if isinstance(x, str) and x.strip() == ""
                    else (
                        x.strip()
                        if isinstance(x, str)
                        else x
                    )
            )

    # Eliminar filas completamente vacías.
    df = df.dropna(
        axis=0,
        how="all"
    )

    # Las columnas completamente vacías NO se eliminan.
    # Forman parte de la estructura de la futura tabla SQL.

    return df.reset_index(drop=True)
