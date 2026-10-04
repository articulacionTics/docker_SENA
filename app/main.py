"""API mínima del laboratorio Docker multiservicio.

Endpoints:
  GET  /            -> página de inicio (HTML con el estado en vivo)
  GET  /health      -> estado del proceso (no consulta la BD)
  GET  /api/status  -> resuelve el hostname de la BD y consulta PostgreSQL
  GET  /api/notas   -> lista las notas guardadas (prueba de persistencia)
  POST /api/notas   -> guarda una nota {"texto": "..."}
"""

import logging
import socket
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app import database

log = logging.getLogger("uvicorn.error")
INDEX_HTML = Path(__file__).parent / "static" / "index.html"


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        database.init_schema()
        log.info("Esquema verificado en PostgreSQL (%s)", database.db_host())
    except Exception as exc:  # la API arranca igual; /api/status mostrará el error
        log.warning("No se pudo inicializar el esquema: %s", exc)
    yield


app = FastAPI(title="Docker Multiservice Lab API", version="1.0.0", lifespan=lifespan)


class NotaIn(BaseModel):
    texto: str = Field(min_length=1, max_length=200)


@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(INDEX_HTML, media_type="text/html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/status")
def status():
    host = database.db_host()
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror as exc:
        raise HTTPException(503, detail=f"No se pudo resolver '{host}': {exc}")
    try:
        with database.get_connection() as conn:
            version = conn.execute("SHOW server_version").fetchone()[0]
            db_name = conn.execute("SELECT current_database()").fetchone()[0]
    except Exception as exc:
        raise HTTPException(503, detail=f"Error conectando a PostgreSQL: {exc}")
    return {
        "api": "ok",
        "database": "connected",
        "db_host": host,
        "db_ip": ip,
        "db_name": db_name,
        "postgres_version": version,
        "api_hostname": socket.gethostname(),
    }


@app.get("/api/notas")
def listar_notas():
    with database.get_connection() as conn:
        rows = conn.execute(
            "SELECT id, texto, creado_en FROM notas ORDER BY id"
        ).fetchall()
    return [{"id": r[0], "texto": r[1], "creado_en": r[2].isoformat()} for r in rows]


@app.post("/api/notas", status_code=201)
def crear_nota(nota: NotaIn):
    with database.get_connection() as conn:
        row = conn.execute(
            "INSERT INTO notas (texto) VALUES (%s) RETURNING id", (nota.texto,)
        ).fetchone()
    return {"id": row[0], "texto": nota.texto}
