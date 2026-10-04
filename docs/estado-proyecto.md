# Estado del proyecto

Última actualización: 2026-10-03 · Repositorio: https://github.com/articulacionTics/docker_SENA

| Fase | Estado | Evidencia / notas |
|---|---|---|
| Entorno (diagnóstico 3.2b + AA2 paso 3) | PASS | Windows 11 Pro 26200 · WSL 2.7.14 · Ubuntu 24.04.1 · **Docker Engine 29.8.2** · Compose v5.6.0 · BuildKit · `hello-world` OK (`docs/entorno.md`) |
| AA1 — Requisitos y arquitectura | PASS | `docs/requisitos.md` (RI-01…RI-15, RI-OS-01 Windows / 02 Linux / 03 macOS, componentes, trazabilidad) y `docs/arquitectura.png` |
| AA2 — Docker Engine e imágenes | PASS (parcial) | Imágenes buscadas, descargadas e inspeccionadas (`docs/imagenes.md`). Pendiente repetir la práctica `db-app` con `-p 5432` tal como la guía, bloqueada por P8 (Docker Desktop ocupando los puertos 5432 y 8080) |
| AA3 — API + Dockerfile | PASS | `api-app:1.0.0` construida con BuildKit, UID 1001, 275 MB frente a 780 MB sin multi-etapa (`docs/imagenes.md` §5) |
| AA4 — Compose + Nginx + PostgreSQL | EN CURSO | `docker compose config` OK; falta levantar la solución (P8) |
| AA5 — Pruebas | PENDING | |
| GHCR (publicación manual) | PENDING | Requiere un PAT `write:packages` y `docker login ghcr.io` (la usuaria) |
| GitHub Actions | PENDING | |
| Servidor remoto | PENDING | Pendiente de realizar cuando el instructor entregue las credenciales del servidor |
| Auditoría Anexo C | PENDING | |
