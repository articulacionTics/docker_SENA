# Docker Multiservice Lab

> Estado: **en construcción** (AA1 completada). Ver [`docs/estado-proyecto.md`](docs/estado-proyecto.md).

## Descripción

Proyecto de la guía SENA *«Despliegue de aplicaciones y servicios en contenedores Docker»* (programa 22810024, competencia 220501086). Es una aplicación web multiservicio deliberadamente sencilla, pensada para demostrar el análisis de requisitos de infraestructura, imágenes Docker, Dockerfile multi-stage, redes, volúmenes, Docker Compose, el reverse proxy con Nginx, la publicación en GHCR y CI/CD con GitHub Actions.

## Arquitectura

![Arquitectura](docs/arquitectura.png)

| Servicio | Imagen | Puerto interno | Puerto en el host |
|---|---|---:|---:|
| `proxy` | `nginx:1.30-alpine` | 80 | **8080** |
| `api` | propia (`python:3.14-slim`, multi-stage) | 8000 | — |
| `db` | `postgres:18-alpine` | 5432 | — |

Los tres servicios están en la red Docker `interna`. Solo el proxy publica un puerto. PostgreSQL guarda sus datos en el volumen `pgdata`.

## Tecnologías

Docker Engine · Docker Compose v2 · Python 3.14 · FastAPI · Uvicorn · PostgreSQL 18 · Nginx 1.30 · GitHub Actions · GHCR

## Requisitos

- Linux, o Windows 11 con **WSL2 + Ubuntu**
- **Docker Engine** (no Docker Desktop) con el plugin **Docker Compose v2**
- Git
- En Windows, clonar el proyecto dentro de `/home/<usuario>/`, no en `/mnt/c/`

Ver los requisitos completos en [`docs/requisitos.md`](docs/requisitos.md).

## Instalación

```bash
git clone https://github.com/articulacionTics/docker_SENA.git docker-multiservice-lab
cd docker-multiservice-lab
cp .env.example .env
```

## Ejecución

```bash
docker compose up -d --build
docker compose ps
curl http://localhost:8080/health
```

*(Las secciones de configuración, verificación, persistencia, GHCR, GitHub Actions, despliegue remoto y troubleshooting se completarán en las siguientes fases.)*

## Estructura

```text
docker-multiservice-lab/
├── app/                  # API FastAPI
├── nginx/                # Configuración del reverse proxy
├── docs/                 # Requisitos, arquitectura, entorno, pruebas, manual
├── .github/workflows/    # CI/CD → GHCR
├── .env.example          # Plantilla de variables (copiar a .env)
├── Dockerfile
└── docker-compose.yml
```

## Autores

- **Lily Pardo** — Ficha 3602390 — SENA
- GitHub: [articulacionTics](https://github.com/articulacionTics)
