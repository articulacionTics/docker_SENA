# Estado del proyecto

Última actualización: 2026-10-03 · Repositorio: https://github.com/articulacionTics/docker_SENA

| Fase | Estado | Evidencia / notas |
|---|---|---|
| Entorno (diagnóstico 3.2b + AA2 paso 3) | PASS | Windows 11 Pro 26200 · WSL 2.7.14 · Ubuntu 24.04.1 · **Docker Engine 29.8.2** · Compose v5.6.0 · BuildKit · `hello-world` OK (`docs/entorno.md`) |
| AA1 — Requisitos y arquitectura | PASS | `docs/requisitos.md` (RI-01…RI-15, RI-OS-01 Windows / 02 Linux / 03 macOS, componentes, trazabilidad) y `docs/arquitectura.png` |
| AA2 — Docker Engine e imágenes | PASS | Imágenes buscadas, descargadas e inspeccionadas; práctica `db-app` (`-p 5432`, `shared_buffers=32MB`) y `web` con los comandos de la guía; entorno limpio (`docs/imagenes.md`) |
| AA3 — API + Dockerfile | PASS | `api-app:1.0.0` construida con BuildKit, UID 1001, 275 MB frente a 780 MB sin multi-etapa (`docs/imagenes.md` §5) |
| AA4 — Compose + Nginx + PostgreSQL | PASS | `docker compose up -d --build`: db y api *healthy*, proxy en 8080; `/health` 200 vía Nginx; `/api/status` → `database: connected` (tras resolver P6, el UFW de Ubuntu-20.04) |
| AA5 — Pruebas | PASS | `docs/pruebas.md`: P1–P10 en PASS (arranque desde cero, proxy, API→BD, red, persistencia, aislamiento, volumen, usuario, consumo ≈81 MiB, secretos) |
| GHCR (publicación manual) | PENDING | Requiere un PAT `write:packages` y `docker login ghcr.io` (la usuaria) |
| GitHub Actions | PENDING | |
| Servidor remoto | PENDING | Pendiente de realizar cuando el instructor entregue las credenciales del servidor |
| Auditoría Anexo C | PENDING | |
