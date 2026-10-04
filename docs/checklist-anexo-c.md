# Auditoría contra el Anexo C (requisitos de aprobación del repositorio)

- **Fecha:** 2026-10-04.
- **Repositorio:** https://github.com/articulacionTics/docker_SENA
- **Estados:** PASS (verificado con evidencia), FAIL o PENDING.

Ningún punto se marca PASS sin haber ejecutado o inspeccionado su evidencia.

| # | Requisito del Anexo C | Estado | Evidencia |
|---|---|---|---|
| 1 | La solución se levanta con un solo comando desde una copia limpia | **PASS** | §1 abajo: `git clone` desde GitHub en una carpeta temporal → `cp .env.example .env` → `docker compose up -d --build`. Tres servicios arriba en 19 s; `/health` y `/api/status` responden por el puerto 8080 del proxy |
| 2 | Matriz de requisitos de infraestructura y diagrama de arquitectura | **PASS** | [`docs/requisitos.md`](requisitos.md): RI-01…RI-15 y RI-OS-01 (Windows), RI-OS-02 (Linux), RI-OS-03 (macOS), cada uno con criterio de aceptación y método de verificación. [`docs/arquitectura.png`](arquitectura.png): servicios, puertos, red `interna` y volumen `pgdata` |
| 3 | Entorno de cada integrante e instalación de Docker Engine | **PASS** | [`docs/entorno.md`](entorno.md). El equipo tiene un integrante: Windows 11, **ruta 2B (WSL2)**, Ubuntu 24.04.1, `docker --version` → 29.8.2, `docker compose version` → v5.6.0, problemas P1–P9 y su solución. Los procedimientos de las rutas 2A (Ubuntu) y 2C (Colima) están en el README |
| 4 | Imagen de la API con Dockerfile multi-etapa y usuario sin privilegios | **PASS** | [`Dockerfile`](../Dockerfile): etapas `builder` y `runtime`, `USER appuser` (UID 1001). `docker history` en [`docs/imagenes.md`](imagenes.md) §5.2. `docker compose exec api id` → `uid=1001(appuser)`. 275 MB frente a 780 MB sin multi-etapa |
| 5 | Tres servicios orquestados con Compose en una red interna; solo el proxy expone puerto | **PASS** | [`docker-compose.yml`](../docker-compose.yml): `db`, `api` y `proxy` en la red `interna`; solo `proxy` tiene `ports` (`8080:80`); `db` y `api` sin `ports`. [`docs/pruebas.md`](pruebas.md) P1, P4 y P6: `docker compose ps`, y `curl` a 5432 y 8000 sin respuesta |
| 6 | Persistencia de PostgreSQL mediante un volumen | **PASS** | [`docs/pruebas.md`](pruebas.md) P5: la nota creada sobrevive a `docker compose down` + `up -d`; volumen `docker-sena_pgdata` (P7) |
| 7 | Imagen publicada en un registry | **PASS** | Paquete público https://github.com/articulacionTics/docker_SENA/pkgs/container/docker_sena (`ghcr.io/articulaciontics/docker_sena`), etiquetas `1.0.0`, `latest` y `sha-…`. `docker pull` sin credenciales funcionó ([`docs/despliegue-automatizado.md`](despliegue-automatizado.md) §2) |
| 8 | Documentación completa (README y manual técnico) **y el despliegue remoto funciona** | **PENDING** | Documentación: **PASS**. El [`README.md`](../README.md) cubre la instalación en los 3 sistemas operativos, ejecución, verificación, GHCR, CI/CD y troubleshooting; el [`docs/manual-tecnico.md`](manual-tecnico.md) incluye arquitectura, pruebas y la propuesta de escalamiento con la Ley 1581. **Despliegue remoto: PENDING**, a la espera de que el instructor entregue el servidor (host, usuario, puerto y clave). El procedimiento y `deploy/docker-compose.prod.yml` están listos y validados con `docker compose config` |
| 9 | Publicación automática al integrar cambios en la rama principal | **PASS** | [`.github/workflows/publicar-imagen.yml`](../.github/workflows/publicar-imagen.yml). Corridas en verde: [37179035255](https://github.com/articulacionTics/docker_SENA/actions/runs/37179035255), [37179196305](https://github.com/articulacionTics/docker_SENA/actions/runs/37179196305), [37179265278](https://github.com/articulacionTics/docker_SENA/actions/runs/37179265278) y [37179266818](https://github.com/articulacionTics/docker_SENA/actions/runs/37179266818) (tag `v1.0.0`). La imagen aparece en Packages con etiquetas inmutables `sha-…`. [`docs/despliegue-automatizado.md`](despliegue-automatizado.md) explica cómo seguiría la cadena hasta producción |

**Resultado: 8 PASS · 1 PENDING** (despliegue remoto, que depende del servidor del instructor).

---

## 1. Prueba desde copia limpia (simulación del instructor)

Se ejecutó en una carpeta temporal fuera del proyecto, con un nombre de proyecto Compose distinto (`COMPOSE_PROJECT_NAME`). Así arrancó con un volumen nuevo, sin datos previos, como en el equipo del instructor.

```text
### carpeta temporal: /home/liya/copia-limpia-c1oK
$ git clone https://github.com/articulacionTics/docker_SENA.git
clonado
commit: eedc2f7 docs: agregar manual técnico y propuesta de escalamiento
$ cp .env.example .env
$ docker compose up -d --build
   Image api-app:1.0.0 Built
   Volume sena-copia-limpia_pgdata Created
   Network sena-copia-limpia_interna Created
   Container sena-copia-limpia-db-1 Started
   Container sena-copia-limpia-db-1 Healthy
   Container sena-copia-limpia-api-1 Started
   Container sena-copia-limpia-api-1 Healthy
   Container sena-copia-limpia-proxy-1 Started
(respondiendo en 19 s)
$ docker compose ps
NAME                        STATUS                    PORTS
sena-copia-limpia-api-1     Up 6 seconds (healthy)    8000/tcp
sena-copia-limpia-db-1      Up 17 seconds (healthy)   5432/tcp
sena-copia-limpia-proxy-1   Up 1 second               0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
$ curl http://localhost:8080/health
{"status":"ok"}
$ curl http://localhost:8080/api/status
{"api":"ok","database":"connected","db_host":"db","db_ip":"172.18.0.2","db_name":"appdb","postgres_version":"18.6","api_hostname":"c8571c10a97c"}
```

Después se limpió con `docker compose down -v` (solo el volumen de la copia limpia) y se eliminó la carpeta temporal.

## 2. Pendientes para cerrar el curso

| Pendiente | Responsable | Detalle |
|---|---|---|
| Despliegue en el servidor remoto | Instructor (credenciales) → aprendiz | Procedimiento en [`docs/manual-tecnico.md`](manual-tecnico.md) §9. Para el despliegue automático: secretos `SERVIDOR_*` y variable `DESPLIEGUE_HABILITADO=true` |
| Video de demostración (3–5 min) | Aprendiz | Mostrar: `git clone` → `cp .env.example .env` → `docker compose up -d --build` → `ps` → `/health` → persistencia → aislamiento → Actions en verde → GHCR |
| Release en GitHub de `v1.0.0` | Aprendiz (interfaz web) | La etiqueta `v1.0.0` ya existe; falta crear el *Release* desde *Releases → Draft a new release* |
| Reflexión del foro, cuestionario y mapa conceptual | Aprendiz (aula virtual) | Fuera del repositorio. El mapa conceptual está en `C:\LProyectos\cl\mapa-conceptual.png` |
