from __future__ import annotations

import argparse
from pathlib import Path

from sqlacodegen.generators import DeclarativeGenerator
from sqlalchemy import MetaData, URL, create_engine

from config import Config


HEADER = '''\
# ---------------------------------------------------------------------------
# Modelos SQLAlchemy: una clase por tabla del esquema "{schema}".
#
# ARCHIVO GENERADO por generate_models.py a partir de la base de datos.
# No editar a mano: se sobrescribe cada vez que se regenera.
# ---------------------------------------------------------------------------

'''


def parse_args() -> argparse.Namespace:
    """Argumentos de línea de comandos (por defecto, los de config)."""

    parser = argparse.ArgumentParser(
        description="Genera las clases SQLAlchemy de las tablas cargadas."
    )

    parser.add_argument(
        "--schema",
        default=Config.DB_SCHEMA,
        help="Esquema de la base a leer.",
    )

    parser.add_argument(
        "--output",
        default="etl/models.py",
        help="Archivo Python donde se escriben las clases.",
    )

    return parser.parse_args()


def main():

    args = parse_args()

    if not Config.DB_PASSWORD:
        raise SystemExit(
            "Falta DB_PASSWORD en .env: no hay cómo conectarse a la base."
        )

    # SQLAlchemy no usa JDBC: se conecta a la misma base con psycopg,
    # usando los mismos datos de conexión de la ETL.
    engine = create_engine(
        URL.create(
            "postgresql+psycopg",
            username=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
        ),
        connect_args={"sslmode": "require", "connect_timeout": 15},
    )

    metadata = MetaData()

    metadata.reflect(
        engine,
        schema=args.schema
    )

    code = DeclarativeGenerator(
        metadata,
        engine,
        options=set()
    ).generate()

    output = Path(args.output)

    output.write_text(
        HEADER.format(schema=args.schema) + code,
        encoding="utf-8"
    )

    engine.dispose()

    print(
        f"{len(metadata.tables)} tablas -> {output}"
    )


if __name__ == "__main__":
    main()
