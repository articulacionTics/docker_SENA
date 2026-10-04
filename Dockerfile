# ---------- Etapa 1: builder — instala dependencias en un entorno virtual ----------
FROM python:3.14-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build
COPY app/requirements.txt .
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install -r requirements.txt \
 && /opt/venv/bin/pip uninstall -y pip   # pip no es necesario en runtime

# ---------- Etapa 2: runtime — solo intérprete, venv y código ----------
FROM python:3.14-slim AS runtime

LABEL org.opencontainers.image.title="docker-multiservice-lab-api" \
      org.opencontainers.image.description="API FastAPI del laboratorio Docker multiservicio (SENA)" \
      org.opencontainers.image.source="https://github.com/articulacionTics/docker_SENA" \
      org.opencontainers.image.authors="Lily Pardo"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Usuario sin privilegios (UID/GID 1001), sin shell de login ni home
RUN groupadd --system --gid 1001 appuser \
 && useradd --system --uid 1001 --gid appuser --no-create-home --shell /usr/sbin/nologin appuser

WORKDIR /srv
COPY --from=builder /opt/venv /opt/venv
# El código queda propiedad de root (solo lectura para appuser)
COPY app/ ./app/

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
