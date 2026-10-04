# Estado del proyecto

Última actualización: 2026-10-04 · Repositorio: https://github.com/articulacionTics/docker_SENA

| Fase | Estado | Evidencia / notas |
|---|---|---|
| Entorno (diagnóstico 3.2b + AA2 paso 3) | PASS | Windows 11 Pro 26200 · WSL 2.7.14 · Ubuntu 24.04.1 · **Docker Engine 29.8.2** · Compose v5.6.0 · BuildKit (`docs/entorno.md`, problemas P1–P9) |
| AA1 — Requisitos y arquitectura | PASS | `docs/requisitos.md` (RI-01…RI-15, RI-OS-01/02/03) · `docs/arquitectura.png` |
| AA2 — Docker Engine e imágenes | PASS | `docs/imagenes.md`: búsqueda, descarga, inspección; prácticas `db-app` y `web` con los comandos de la guía |
| AA3 — API + Dockerfile | PASS | `api-app:1.0.0` multi-etapa, UID 1001, 275 MB frente a 780 MB sin multi-etapa |
| AA4 — Compose + Nginx + PostgreSQL | PASS | `docker-compose.yml`, `nginx/default.conf`; db y api *healthy*; solo el proxy expone el 8080 |
| AA5 — Pruebas | PASS | `docs/pruebas.md`: P1–P10 en PASS |
| GHCR (publicación manual) | PASS | `ghcr.io/articulaciontics/docker_sena:1.0.0`, paquete público, `pull` sin credenciales |
| GitHub Actions | PASS | 4 corridas en verde, caché de 33 s → 21 s, tag `v1.0.0` publicado (`docs/despliegue-automatizado.md`) |
| Servidor remoto | PENDING | Pendiente de realizar cuando el instructor entregue las credenciales del servidor. Procedimiento y `deploy/docker-compose.prod.yml` listos |
| Copia limpia | PASS | `docs/checklist-anexo-c.md` §1 |
| Auditoría Anexo C | 8 PASS · 1 PENDING | `docs/checklist-anexo-c.md` (pendiente: despliegue remoto) |
| Video de demostración | PENDING | Lo graba la aprendiz |
