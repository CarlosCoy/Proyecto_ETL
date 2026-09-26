# ---------------------------------------------------------------------------
# Transform: normalización de nombres (columnas y tablas)
# ---------------------------------------------------------------------------

import re
from typing import Iterable

from etl.utils.cells import is_empty


def normalize_name(value: object, fallback: str) -> str:
    """
    Convierte un nombre de columna/tabla a un identificador estable.

    Ejemplo:
        'Fecha Nacimiento' -> 'fecha_nacimiento'
    """

    if is_empty(value):
        text = fallback
    else:
        text = str(value).strip()

    # Quitar acentos.
    replacements = str.maketrans(
        "áéíóúüñÁÉÍÓÚÜÑ",
        "aeiouunAEIOUUN",
    )

    text = text.translate(replacements)
    text = text.lower()

    text = re.sub(r"[^a-zA-Z0-9_]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")

    if not text:
        text = fallback

    if text[0].isdigit():
        text = f"col_{text}"

    return text


def unique_names(
    names: Iterable[object],
    prefix: str = "columna"
) -> list[str]:
    """Normaliza encabezados y evita duplicados."""

    result = []
    used = {}

    for index, name in enumerate(names, start=1):

        base = normalize_name(
            name,
            f"{prefix}_{index}"
        )

        count = used.get(base, 0) + 1
        used[base] = count

        result.append(
            base if count == 1 else f"{base}_{count}"
        )

    return result


def table_name(sheet_name: str) -> str:
    """Genera el nombre de tabla a partir del nombre de la hoja."""

    return normalize_name(
        sheet_name,
        "tabla"
    )
