"""Acceso a PostgreSQL.

La configuración se lee SOLO de variables de entorno (inyectadas por
Docker Compose desde .env). No hay credenciales en el código.
"""

import os

import psycopg


def _settings() -> dict:
    faltantes = [v for v in ("DB_NAME", "DB_ADMIN_PASSWORD") if v not in os.environ]
    if faltantes:
        raise RuntimeError(f"Faltan variables de entorno: {', '.join(faltantes)}")
    return {
        "host": os.environ.get("DB_HOST", "db"),
        "port": int(os.environ.get("DB_PORT", "5432")),
        "dbname": os.environ["DB_NAME"],
        "user": os.environ.get("DB_USER", "postgres"),
        "password": os.environ["DB_ADMIN_PASSWORD"],
    }


def db_host() -> str:
    return os.environ.get("DB_HOST", "db")


def get_connection() -> psycopg.Connection:
    return psycopg.connect(**_settings(), connect_timeout=5)


def init_schema() -> None:
    """Crea la tabla de ejemplo usada en la prueba de persistencia."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notas (
                id         SERIAL PRIMARY KEY,
                texto      TEXT NOT NULL,
                creado_en  TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
