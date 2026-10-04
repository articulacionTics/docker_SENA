# AA1 — Requisitos de infraestructura

Proyecto: **docker-multiservice-lab**. Es una aplicación web multiservicio con Nginx como proxy inverso, una API FastAPI y PostgreSQL.
Programa SENA 22810024 · Competencia 220501086 · RA1: analizar los requisitos de infraestructura y plataforma tecnológica.

## 1. Alcance

La aplicación es deliberadamente mínima. Lo que se evalúa es la **infraestructura**: contenedores, imágenes, redes, volúmenes, aislamiento, configuración por variables de entorno, publicación en un registry y automatización CI/CD.

## 2. Componentes

| Componente | Imagen base | Puerto interno | Puerto externo | Requisito clave |
|---|---|---:|---:|---|
| Proxy inverso (`proxy`) | `nginx:1.30-alpine` | 80 | **8080** | Enrutar las peticiones a la API (único punto de entrada) |
| API backend (`api`) | `python:3.14-slim` (imagen propia `api-app:1.0.0`, Dockerfile multi-etapa) | 8000 | — | Conexión a la base de datos por la red interna |
| Base de datos (`db`) | `postgres:18-alpine` | 5432 | — | Almacenamiento persistente (volumen `pgdata`) |

Todos los servicios comparten la red Docker `interna`. Solo `proxy` publica un puerto en el host.

**Hardware y software mínimos** (sección 2 de la guía):

| Recurso | Mínimo | Recomendado |
|---|---|---|
| RAM | 4 GB | 8 GB o más |
| Disco libre | 15 GB | 25 GB o más |
| Procesador | 64 bits con virtualización habilitada (VT-x / AMD-V) o Apple Silicon | 2 núcleos o más |
| Motor | Docker Engine serie 29.x + plugin Compose (`docker compose`) | — |

## 3. Requisitos por sistema operativo

Los contenedores deben comportarse igual en los tres sistemas operativos admitidos. En los tres, Docker Engine corre sobre un núcleo Linux y se usan los mismos comandos.

| ID | Requisito | Justificación | Criterio de aceptación | Método de verificación |
|---|---|---|---|---|
| RI-OS-01 | **Windows 10 v2004+ / Windows 11:** Docker Engine dentro de una distribución Ubuntu en **WSL2** con systemd; sin Docker Desktop. | Windows no tiene núcleo Linux; WSL2 lo proporciona. Docker Desktop no se usa en el curso. | `wsl -l -v` muestra la distribución en VERSION 2. `docker context ls` marca `default` con `unix:///var/run/docker.sock`. `docker run --rm hello-world` funciona. `http://localhost:8080` responde desde el navegador de Windows. | PowerShell: `wsl --version`, `wsl -l -v`. Ubuntu: `docker --version`, `docker context ls`. **Verificado en este equipo** (`docs/entorno.md`) |
| RI-OS-02 | **Linux (Ubuntu 22.04/24.04/26.04):** Docker Engine nativo desde el repositorio oficial, gestionado por systemd. | Es el entorno equivalente al servidor de producción. | `systemctl is-active docker` → `active`. `docker --version` → 29.x. `docker compose version` responde. | `docker info` → `Operating System: Ubuntu …`. El servidor remoto del curso cumple este perfil |
| RI-OS-03 | **macOS 13+ (Intel o Apple Silicon):** Docker Engine dentro de una máquina virtual **Colima**; plugin Compose registrado en `~/.docker/config.json`. | macOS no tiene núcleo Linux. Las tres imágenes base publican variantes amd64 y arm64. | `colima status` → running. `docker compose version` responde. `docker image inspect` muestra `Architecture: arm64` en Apple Silicon. | `colima status`, `uname -m`, `docker info`. No hay integrante con macOS en este equipo: se documenta el procedimiento en el README |

## 4. Matriz de requisitos de infraestructura

| ID | Descripción | Justificación | Criterio de aceptación | Método de verificación |
|---|---|---|---|---|
| RI-01 | Los tres servicios se ejecutan en contenedores independientes. | El aislamiento por responsabilidad permite actualizar, reiniciar y escalar cada componente por separado. | `docker compose ps` lista `db`, `api` y `proxy` en estado *running* (db y api *healthy*). | `docker compose ps` |
| RI-02 | Solo Nginx está expuesto al exterior. | Reduce la superficie de ataque, porque la API y la BD no son accesibles desde fuera del host Docker. | En `docker-compose.yml` solo `proxy` tiene `ports` (`8080:80`); `api` y `db` no tienen `ports`. | Revisar `docker-compose.yml`; `docker compose port api 8000` y `docker compose port db 5432` no devuelven puerto; `curl localhost:8000` y `localhost:5432` fallan |
| RI-03 | Los datos de PostgreSQL persisten entre reinicios. | Un contenedor es efímero, así que los datos deben sobrevivir a su recreación. | Un registro insertado sigue existiendo tras `docker compose down` + `docker compose up -d`. | Insertar → `down` (sin `-v`) → `up -d` → consultar |
| RI-04 | La solución opera con 4 GB de memoria RAM. | La guía apunta a equipos de gama media-baja y a servidores pequeños. | `docker stats` no supera ese consumo con los tres servicios arriba. Además, cada servicio tiene un límite de memoria (`deploy.resources.limits`) cuya suma queda muy por debajo de 4 GB. | `docker stats --no-stream`; `docker compose config` (límites) |
| RI-05 | Las credenciales no están en el código ni en Git. | Evita la filtración de secretos en el repositorio. | Las credenciales están en `.env` (ignorado). Solo se versiona `.env.example`. No hay contraseñas en `app/*.py`. | `git ls-files \| grep -x .env` (vacío); `git check-ignore .env`; revisar el código |
| RI-06 | La API usa una imagen propia construida con un Dockerfile multi-stage. | Separar build y runtime da una imagen final más pequeña y sin herramientas de compilación. | El `Dockerfile` tiene al menos 2 etapas `FROM`; `docker build -t api-app:1.0.0 .` termina bien. | `docker build`, `docker history api-app:1.0.0`, `docker images` |
| RI-07 | La API se ejecuta como usuario no privilegiado. | Si alguien compromete la aplicación, no obtiene privilegios de root dentro del contenedor. | El proceso corre como `appuser` (UID 1001). | `docker compose exec api id` → `uid=1001(appuser)` |
| RI-08 | PostgreSQL usa un volumen nombrado persistente. | El ciclo de vida de los datos queda separado del contenedor. | Existe el volumen `pgdata` montado en `/var/lib/postgresql`, que es la ruta oficial para PostgreSQL 18+. Con la ruta clásica `/var/lib/postgresql/data` el contenedor de PG18 falla (evidencia en `docs/imagenes.md` §4). | `docker volume ls`, `docker volume inspect`, `docker compose config` |
| RI-09 | La API y la BD se comunican por una red interna de Docker usando nombres de servicio. | El DNS interno de Docker evita IPs fijas y no requiere publicar puertos. | La API resuelve `db` y `/api/status` responde con la BD conectada. | `docker compose exec api python -c "import socket;print(socket.gethostbyname('db'))"`; `curl localhost:8080/api/status` |
| RI-10 | Nginx funciona como reverse proxy hacia la API. | Hay un único punto de entrada para agregar TLS, cabeceras y límites de forma centralizada. | `curl http://localhost:8080/health` → `{"status":"ok"}`, servido a través de Nginx. | `curl -i` (cabecera `Server: nginx`) |
| RI-11 | La aplicación se levanta con un solo comando. | Simplifica la operación y la evaluación. | `docker compose up -d --build` deja los 3 servicios activos. | Ejecutar el comando + `docker compose ps` |
| RI-12 | El despliegue es reproducible. | Cualquier persona obtiene el mismo resultado desde una copia limpia. | Las imágenes base usan etiquetas explícitas (sin `latest`) y las dependencias de Python están fijadas. Clonar + `cp .env.example .env` + `up` funciona. | Prueba desde copia limpia (`git clone` en una carpeta temporal) |
| RI-13 | La imagen de la API está publicada en GHCR. | Un registry permite distribuir la imagen al servidor sin construirla allí. | La imagen existe en `ghcr.io/articulaciontics/docker_sena` con etiquetas inmutables (`1.0.0`, `sha-xxxxxxx`) y se descarga sin construirla. | Página *Packages* de GitHub; `docker pull ghcr.io/articulaciontics/docker_sena:1.0.0` |
| RI-14 | GitHub Actions construye y publica la imagen automáticamente. | CI/CD elimina pasos manuales y deja trazabilidad commit → imagen. | El workflow `publicar-imagen.yml` corre en `push` a `main` y en tags `v*.*.*` y termina en verde. | Pestaña *Actions* del repositorio |
| RI-15 | El despliegue remoto usa la imagen publicada, sin construir en el servidor. | Producción debe ejecutar exactamente la imagen probada y trazable a un commit. | El compose del servidor (`deploy/docker-compose.prod.yml`) usa `image: ghcr.io/…:sha-xxxxxxx` y no tiene `build:`. `/health` responde en el servidor. | Revisión del archivo; `curl http://<servidor>:<puerto>/health` |

## 5. Trazabilidad

Cada requisito se rastrea así: **Requisito → Implementación → Prueba → Evidencia**. Las evidencias se registran en `docs/pruebas.md` y el resumen final en `docs/checklist-anexo-c.md`.

| ID | Implementación | Prueba (evidencia en) |
|---|---|---|
| RI-01 | `docker-compose.yml` (servicios db, api, proxy) | Arranque — `docs/pruebas.md` |
| RI-02 | `docker-compose.yml` (solo `proxy.ports`) | Aislamiento — `docs/pruebas.md` |
| RI-03, RI-08 | `volumes: pgdata` | Persistencia / volumen — `docs/pruebas.md` |
| RI-04 | `deploy.resources.limits` | Consumo — `docs/pruebas.md` |
| RI-05 | `.gitignore`, `.env.example`, variables de entorno | Revisión de Git — `docs/pruebas.md` |
| RI-06, RI-07 | `Dockerfile` | Build e `id` — `docs/imagenes.md`, `docs/pruebas.md` |
| RI-09 | `networks: interna`, `DB_HOST=db` | Red — `docs/pruebas.md` |
| RI-10 | `nginx/default.conf` | `/health` vía proxy — `docs/pruebas.md` |
| RI-11, RI-12 | Todo el repositorio | Copia limpia — `docs/pruebas.md` |
| RI-13, RI-14 | `.github/workflows/publicar-imagen.yml` | `docs/despliegue-automatizado.md` |
| RI-15 | `deploy/docker-compose.prod.yml`, job `desplegar` | `docs/manual-tecnico.md` (despliegue remoto) |
| RI-OS-01…03 | Docker Engine en WSL2 / Ubuntu nativo / Colima | `docs/entorno.md`, `README.md` |

## 6. Arquitectura

Ver `docs/arquitectura.png` (la fuente editable es `docs/arquitectura.svg`).

```text
Cliente ──HTTP :8080──► proxy (Nginx :80) ──► api (FastAPI :8000) ──► db (PostgreSQL :5432) ──► volumen pgdata
                        └───────────────────── red Docker: interna ─────────────────────┘
```
