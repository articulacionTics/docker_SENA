# Docker Multiservice Lab

[![Publicar imagen](https://github.com/articulacionTics/docker_SENA/actions/workflows/publicar-imagen.yml/badge.svg)](https://github.com/articulacionTics/docker_SENA/actions/workflows/publicar-imagen.yml)

**Autora:** Lily Pardo · **Ficha:** 3602390 · SENA, Centro de Comercio y Servicios, Regional Tolima · **GitHub:** [@Lilypar59](https://github.com/Lilypar59)
**Programa:** Despliegue de aplicaciones y servicios en contenedores Docker (22810024) · **Competencia:** 220501086

## 🔗 Enlaces públicos (entrega)

Todos los enlaces son públicos y se abren sin iniciar sesión en GitHub.

| Qué | Enlace |
|---|---|
| **🌐 Aplicación desplegada en un servidor remoto (Google Cloud)** | **http://34.60.209.202:8080/health** · [`/api/status`](http://34.60.209.202:8080/api/status) · [`/docs`](http://34.60.209.202:8080/docs). Disponible hasta el **martes 2026-10-06** (después se apaga la VM para no generar costos) |
| **Repositorio** | https://github.com/articulacionTics/docker_SENA |
| **GitHub Actions: todas las corridas** | **https://github.com/articulacionTics/docker_SENA/actions** |
| Flujo «Publicar imagen» (historial del workflow) | https://github.com/articulacionTics/docker_SENA/actions/workflows/publicar-imagen.yml |
| Archivo del workflow | [`.github/workflows/publicar-imagen.yml`](.github/workflows/publicar-imagen.yml) |
| Imagen publicada en GHCR | https://github.com/articulacionTics/docker_SENA/pkgs/container/docker_sena |

Corridas de GitHub Actions, todas en verde ✅:

| Corrida | Disparador | Commit | Resultado |
|---|---|---|---|
| [37179035255](https://github.com/articulacionTics/docker_SENA/actions/runs/37179035255) | push a `main`: primera publicación automática | `936efea` | ✅ success |
| [37179196305](https://github.com/articulacionTics/docker_SENA/actions/runs/37179196305) | push a `main`: segunda corrida, con caché (33 s → 21 s) | `eedc2f7` | ✅ success |
| [37179265278](https://github.com/articulacionTics/docker_SENA/actions/runs/37179265278) | push a `main` | `734cdec` | ✅ success |
| [37179266818](https://github.com/articulacionTics/docker_SENA/actions/runs/37179266818) | etiqueta **`v1.0.0`**: publica la imagen `1.0.0` | `734cdec` | ✅ success |
| [37179327708](https://github.com/articulacionTics/docker_SENA/actions/runs/37179327708) | push a `main` | `58d1f9b` | ✅ success |
| [37218004512](https://github.com/articulacionTics/docker_SENA/actions/runs/37218004512) | push a `main` | `d7973af` | ✅ success |
| [37225015773](https://github.com/articulacionTics/docker_SENA/actions/runs/37225015773) | push a `main`: **primer despliegue automático en el servidor GCP** (job `desplegar`, intento 2) | `22da6e7` | ✅ success |
| [37225492900](https://github.com/articulacionTics/docker_SENA/actions/runs/37225492900) | push a `main`: **despliegue continuo verificado**. El servidor se actualizó solo y `/health` pasó a `{"status":"ok"}` | `f5d72ca` | ✅ success |

Cada push a `main` genera una corrida nueva; la lista completa y actualizada está siempre en la pestaña [Actions](https://github.com/articulacionTics/docker_SENA/actions).

> La corrida [37225163601](https://github.com/articulacionTics/docker_SENA/actions/runs/37225163601) (`010f591`) falló a propósito en el paso «Verificar la configuración del despliegue»: los secretos del servidor se habían creado como *Variables* y no como *Secrets*. Tras corregirlos, las corridas siguientes desplegaron con éxito.

```bash
docker pull ghcr.io/articulaciontics/docker_sena:1.0.0
```

## Descripción

Proyecto integrador de la guía SENA **«Despliegue de aplicaciones y servicios en contenedores Docker»**: programa 22810024, competencia 220501086 (RA1 y RA2).

Es una aplicación web multiservicio, deliberadamente sencilla, desplegada con **Docker Engine** y **Docker Compose**:

- un **reverse proxy Nginx**, único punto de entrada;
- una **API FastAPI**, con imagen propia construida mediante un Dockerfile multi-etapa y ejecutada sin privilegios;
- una base de datos **PostgreSQL** con datos persistentes en un volumen.

La imagen de la API se publica automáticamente en **GHCR** con **GitHub Actions** cada vez que un cambio llega a `main`.

## Inicio rápido (evaluación del instructor)

Con Docker Engine instalado (ver [Instalación del motor](#instalación-del-motor)):

```bash
git clone https://github.com/articulacionTics/docker_SENA.git
cd docker_SENA
cp .env.example .env
docker compose up -d --build
```

Abra http://localhost:8080/health en el navegador; debe ver `{"status":"ok"}`. Lo que debe aparecer en cada paso está en [Verificación: qué verá al ejecutarlo](#verificación-qué-verá-al-ejecutarlo), y la forma de entrega y su revisión en [Entrega del proyecto](#entrega-del-proyecto-según-la-guía).

## Arquitectura

![Arquitectura](docs/arquitectura.png)

| Servicio | Imagen | Puerto interno | Puerto en el host | Función |
|---|---|---:|---:|---|
| `proxy` | `nginx:1.30-alpine` | 80 | **8080** | Reverse proxy hacia `http://api:8000` |
| `api` | `api-app:1.0.0` (base `python:3.14-slim`, multi-etapa, UID 1001) | 8000 | — | Backend FastAPI |
| `db` | `postgres:18-alpine` | 5432 | — | Base de datos (volumen `pgdata`) |

Los tres servicios están en la red bridge `interna` y se encuentran por **nombre de servicio**. Solo el proxy publica un puerto; la API y la BD no son accesibles desde el host.

## Tecnologías

Docker Engine 29 · Docker Compose (plugin `docker compose`) · Python 3.14 · FastAPI · Uvicorn · psycopg 3 · PostgreSQL 18 · Nginx 1.30 · GitHub Actions · GitHub Container Registry (GHCR)

## Requisitos

| Recurso | Mínimo |
|---|---|
| RAM | 4 GB (la solución consume ≈ 81 MiB en reposo, ver `docs/pruebas.md` P9) |
| Disco libre | 15 GB |
| CPU | 64 bits con virtualización habilitada (VT-x / AMD-V) o Apple Silicon |
| Software | **Docker Engine 29.x** con el plugin Compose, y Git. **No se usa Docker Desktop.** |
| Puerto libre | 8080 en el host |

La matriz completa de requisitos de infraestructura (RI-01…RI-15, RI-OS-01…03) está en [`docs/requisitos.md`](docs/requisitos.md).

## Instalación del motor

En los tres sistemas operativos se termina usando **el mismo Docker Engine y los mismos comandos**; lo único que cambia es cómo se obtiene el núcleo Linux. En [`docs/entorno.md`](docs/entorno.md) está documentada la instalación real del equipo (Windows 11 + WSL2), con sus salidas y los problemas resueltos.

### Ubuntu 22.04 / 24.04 / 26.04 (nativo)

```bash
sudo apt remove -y docker.io docker-compose docker-compose-v2 docker-doc podman-docker
sudo apt update && sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER      # cerrar sesión y volver a entrar
```

> Use `apt remove`, **no** `apt purge docker.io`: la purga borra `/var/lib/docker`, con todas las imágenes, contenedores y volúmenes (`docs/entorno.md`, P7).

### Windows 10 v2004+ / Windows 11 (WSL2)

En **PowerShell como Administrador**:

```powershell
wsl --install --no-distribution
wsl --update
wsl --set-default-version 2
wsl --install -d Ubuntu-24.04 --web-download
wsl --set-default Ubuntu-24.04
```

Dentro de **Ubuntu**, active systemd y luego instale Docker Engine con los mismos comandos de la sección de Ubuntu:

```bash
printf '[boot]\nsystemd=true\n' | sudo tee /etc/wsl.conf
```

Después, en PowerShell, ejecute `wsl --shutdown` y vuelva a abrir Ubuntu. Desde ahí: **docker, git y el proyecto se usan siempre dentro de Ubuntu**, y PowerShell solo para los comandos `wsl`. Abra `http://localhost:8080` en el navegador de Windows: WSL2 reenvía el puerto.

### macOS 13+ (Intel o Apple Silicon) con Colima

```bash
brew install docker docker-compose colima
mkdir -p ~/.docker
colima start --cpu 2 --memory 4 --disk 20
```

Registre el plugin de Compose en `~/.docker/config.json`: `{ "cliPluginsExtraDirs": ["/opt/homebrew/lib/docker/cli-plugins"] }`. En Mac Intel la ruta es `/usr/local/lib/docker/cli-plugins`. Colima no arranca sola: ejecute `colima start` tras cada reinicio. Las tres imágenes base publican variante arm64.

### Verificar el motor (los tres sistemas)

```bash
docker --version             # serie 29 o superior
docker compose version
docker context ls            # el asterisco debe estar en "default"
docker run --rm hello-world  # "Hello from Docker!"
```

## Instalación del proyecto

```bash
git clone https://github.com/articulacionTics/docker_SENA.git
cd docker_SENA
cp .env.example .env
```

## Configuración

`.env` **no se versiona** (está en `.gitignore`). `.env.example` contiene las mismas claves con valores ficticios.

| Variable | Ejemplo | Uso |
|---|---|---|
| `DB_NAME` | `appdb` | Base de datos que crea PostgreSQL y que usa la API |
| `DB_USER` | `postgres` | Usuario de PostgreSQL |
| `DB_ADMIN_PASSWORD` | `cambiar_esta_clave` | Contraseña de PostgreSQL. **Cámbiela** fuera del laboratorio |
| `DB_HOST` | `db` | Host de la BD para la API: el nombre del servicio, nunca `localhost` |
| `DB_PORT` | `5432` | Puerto interno de PostgreSQL |

## Ejecución

```bash
docker compose up -d --build
```

Compose construye la imagen de la API y arranca **db**. Cuando db está *healthy* arranca **api**, y cuando api está *healthy* arranca **proxy**. Tarda unos 30 a 40 segundos la primera vez.

## Verificación: qué verá al ejecutarlo

Los ejemplos siguientes son **salidas reales** de este proyecto (Docker Engine 29.8.2, 2026-10-04). Los identificadores (`api_hostname`, IP interna, `id` de las notas, fechas) cambian en cada equipo y en cada arranque.

### 1. Al levantar la solución

```text
$ docker compose up -d --build
 Image api-app:1.0.0 Built
 Volume docker-sena_pgdata Created
 Network docker-sena_interna Created
 Container docker-sena-db-1 Started
 Container docker-sena-db-1 Healthy
 Container docker-sena-api-1 Started
 Container docker-sena-api-1 Healthy
 Container docker-sena-proxy-1 Started
```

El orden es deliberado: **db** → (*healthy*) → **api** → (*healthy*) → **proxy**.

### 2. Estado de los servicios

```text
$ docker compose ps
NAME                  IMAGE                STATUS                    PORTS
docker-sena-api-1     api-app:1.0.0        Up 6 seconds (healthy)    8000/tcp
docker-sena-db-1      postgres:18-alpine   Up 16 seconds (healthy)   5432/tcp
docker-sena-proxy-1   nginx:1.30-alpine    Up Less than a second     0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

Fíjese en que solo **proxy** tiene `0.0.0.0:8080->…`. `api` (8000) y `db` (5432) muestran el puerto interno sin publicar: **no son accesibles desde el host**.

### 3. En el navegador (Windows, Linux o macOS)

| Abra esta URL | Debe ver |
|---|---|
| http://localhost:8080/health | `{"status":"ok"}` |
| http://localhost:8080/api/status | JSON con `"database":"connected"` y `"postgres_version":"18.6"` |
| http://localhost:8080/docs | Página **«Docker Multiservice Lab API - Swagger UI»** con los endpoints `/health`, `/api/status` y `/api/notas`. Desde ahí puede probar `POST /api/notas` (*Try it out* → `{"texto": "mi nota"}` → *Execute*) |
| http://localhost:8080/api/notas | Lista JSON de las notas guardadas |
| http://localhost:8000 · http://localhost:5432 | **No cargan**, y es lo correcto: la API y la BD no están expuestas |

En Windows, abra las URL en el navegador normal de Windows: WSL2 reenvía el puerto 8080 automáticamente.

### 4. Desde la terminal

```text
$ curl http://localhost:8080/health
{"status":"ok"}

$ curl -s http://localhost:8080/api/status | python3 -m json.tool
{
    "api": "ok",
    "database": "connected",
    "db_host": "db",
    "db_ip": "172.18.0.2",
    "db_name": "appdb",
    "postgres_version": "18.6",
    "api_hostname": "6e53f68b938e"
}
```

`db_host: "db"` y `db_ip: "172.18.x.x"` demuestran que la API encuentra la base de datos **por nombre de servicio** en la red interna.

Guardar y leer una nota:

```text
$ curl -X POST -H 'Content-Type: application/json' -d '{"texto":"hola desde el README"}' http://localhost:8080/api/notas
{"id":4,"texto":"hola desde el README"}

$ curl http://localhost:8080/api/notas
[{"id":1,"texto":"dato persistente AA5","creado_en":"2026-10-04T04:55:43.073540+00:00"}, ..., {"id":4,"texto":"hola desde el README","creado_en":"2026-10-04T16:44:30.703858+00:00"}]
```

Respuestas de error esperadas:

| Petición | Respuesta |
|---|---|
| `GET /no-existe` | `404 Not Found` · `{"detail":"Not Found"}` |
| `POST /api/notas` con `{"texto": ""}` | `422 Unprocessable Entity` (validación: el texto debe tener entre 1 y 200 caracteres) |

### 5. Registros del proxy (`docker compose logs proxy`)

```text
proxy-1  | 172.18.0.1 - - [04/Oct/2026:16:44:30 +0000] "POST /api/notas HTTP/1.1" 201 39 "-" "curl/8.5.0" "-"
proxy-1  | 172.18.0.1 - - [04/Oct/2026:16:44:30 +0000] "GET /api/notas HTTP/1.1" 200 333 "-" "curl/8.5.0" "-"
proxy-1  | 172.18.0.1 - - [04/Oct/2026:16:44:30 +0000] "GET /no-existe HTTP/1.1" 404 22 "-" "curl/8.5.0" "-"
proxy-1  | 172.18.0.1 - - [04/Oct/2026:16:44:30 +0000] "POST /api/notas HTTP/1.1" 422 145 "-" "curl/8.5.0" "-"
```

Cada petición pasa por Nginx antes de llegar a la API.

### 6. Otras comprobaciones

| Comando | Resultado esperado |
|---|---|
| `docker compose exec api id` | `uid=1001(appuser) gid=1001(appuser) groups=1001(appuser)` (sin root) |
| `docker compose exec api python -c "import socket; print(socket.gethostbyname('db'))"` | Una IP privada, p. ej. `172.18.0.2` |
| `docker compose port db 5432` | `:0` (sin puerto publicado) |
| `curl --max-time 3 http://localhost:5432` | Sin respuesta |
| `docker stats --no-stream` | Unos 80 MiB en total (proxy ≈ 14 MiB, api ≈ 49 MiB, db ≈ 18 MiB) |

Todas las pruebas con sus salidas completas están en [`docs/pruebas.md`](docs/pruebas.md).

## Detener servicios

```bash
docker compose down        # elimina los contenedores y la red; CONSERVA los datos
docker compose down -v     # elimina también el volumen: BORRA los datos
```

## Persistencia

PostgreSQL guarda sus datos en el volumen nombrado `pgdata` (`docker-sena_pgdata`), montado en `/var/lib/postgresql`. Esa es la ruta oficial para PostgreSQL 18+: la clásica `/var/lib/postgresql/data` hace fallar el contenedor (`docs/imagenes.md` §4). Los datos sobreviven a `docker compose down` + `up -d` (`docs/pruebas.md` P5).

```bash
curl -X POST -H 'Content-Type: application/json' -d '{"texto":"hola"}' http://localhost:8080/api/notas
docker compose down && docker compose up -d
curl http://localhost:8080/api/notas      # la nota sigue ahí
```

## Estructura

```text
docker_SENA/
├── app/                         # API FastAPI (main.py, database.py, requirements.txt)
├── nginx/default.conf           # Reverse proxy -> http://api:8000
├── deploy/docker-compose.prod.yml  # Compose del servidor: usa la imagen de GHCR, sin build
├── docs/                        # Requisitos, arquitectura, entorno, imágenes, pruebas, CI/CD, manual
├── .github/workflows/publicar-imagen.yml  # CI/CD: construir y publicar en GHCR
├── Dockerfile                   # Multi-etapa, usuario appuser (UID 1001)
├── docker-compose.yml           # db + api + proxy, red interna, volumen pgdata
├── .env.example                 # Plantilla de variables (copiar a .env)
├── .dockerignore  .gitignore  .gitattributes
└── README.md
```

## GHCR

La imagen de la API está publicada y es **pública**:

```bash
docker pull ghcr.io/articulaciontics/docker_sena:1.0.0
```

Paquete: https://github.com/articulacionTics/docker_SENA/pkgs/container/docker_sena. Etiquetas: `1.0.0` (publicación manual y versión), `sha-xxxxxxx` (una por commit, inmutable) y `latest` (último `main`, nunca para producción).

## GitHub Actions

`.github/workflows/publicar-imagen.yml` se ejecuta en cada `push` a `main` y en cada etiqueta `v*.*.*`:

1. checkout;
2. Buildx;
3. login en GHCR con el `GITHUB_TOKEN` temporal (sin tokens guardados en el repositorio);
4. cálculo de etiquetas (`latest`, `sha-…`, versión semver);
5. build y push con caché de capas (`type=gha`).

El detalle, el enlace a las corridas y la continuación hacia producción están en [`docs/despliegue-automatizado.md`](docs/despliegue-automatizado.md).

## Despliegue remoto

✅ **Desplegado y funcionando en Google Cloud:** **http://34.60.209.202:8080/health**. La VM estará encendida hasta el martes **2026-10-06**.

| Dato | Valor |
|---|---|
| Proveedor | Google Cloud Compute Engine, nivel gratuito (*Always Free*) |
| Máquina | `e2-micro` (2 vCPU compartidas, 1 GB de RAM + 1 GB de swap) · disco persistente estándar de 30 GB |
| Sistema | Ubuntu 24.04 LTS (x86/64) + Docker Engine (repositorio oficial) |
| Ruta | `/srv/app` (copia del repositorio) |
| Compose | `deploy/docker-compose.prod.yml`: la API usa `ghcr.io/articulaciontics/docker_sena:<etiqueta inmutable>`, **sin `build:`** |
| Puerto | 8080 (regla de firewall de VPC `permitir-8080`); 8000 y 5432 no expuestos |
| Despliegue continuo | Job `desplegar` de GitHub Actions por SSH, con los secretos `SERVIDOR_HOST`, `SERVIDOR_USUARIO`, `SERVIDOR_SSH_KEY` y la variable `DESPLIEGUE_HABILITADO=true` |

Verificación desde Internet (2026-10-04):

```text
$ curl -i http://34.60.209.202:8080/health
HTTP/1.1 200 OK
Server: nginx/1.30.5
{"status":"ok"}

$ curl http://34.60.209.202:8080/api/status
{"api":"ok","database":"connected","db_host":"db","db_ip":"172.18.0.2","db_name":"appdb","postgres_version":"18.6","api_hostname":"16660b3a4ebf"}

$ curl --max-time 5 http://34.60.209.202:8000   → sin respuesta (correcto)
$ curl --max-time 5 http://34.60.209.202:5432   → sin respuesta (correcto)
```

**Despliegue continuo demostrado:** el commit `f5d72ca` cambió la respuesta de `/health`. La [corrida 37225492900](https://github.com/articulacionTics/docker_SENA/actions/runs/37225492900) construyó la imagen, la publicó como `sha-f5d72ca` y, en el job `desplegar`, actualizó el servidor por SSH y verificó `/health`. Nadie entró a la VM: el servidor pasó solo de `{"status":"okis"}` a `{"status":"ok"}`.

Procedimiento manual (el mismo que se usó en la VM):

```bash
git clone https://github.com/articulacionTics/docker_SENA.git /srv/app && cd /srv/app
cp .env.example .env
sed -i "s/^DB_ADMIN_PASSWORD=.*/DB_ADMIN_PASSWORD=$(openssl rand -hex 16)/" .env   # contraseña propia del servidor
export API_TAG=1.0.0              # o sha-xxxxxxx (etiqueta inmutable)
export PROXY_PORT=8080
docker compose --env-file .env -f deploy/docker-compose.prod.yml pull
docker compose --env-file .env -f deploy/docker-compose.prod.yml up -d
```

El detalle completo está en [`docs/manual-tecnico.md`](docs/manual-tecnico.md) §9.

## Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| `port is already allocated` / `address already in use` en 8080 | Otro programa o contenedor usa el puerto (por ejemplo, Docker Desktop abierto) | `docker ps`; cerrar Docker Desktop; o cambiar el mapeo `8080:80` |
| `502` o `504 Gateway Time-out` en Nginx | El proxy no alcanza la API | `docker compose ps` (¿api *healthy*?); `docker compose logs api`. En WSL2, un firewall UFW de **otra** distribución puede bloquear el tráfico entre contenedores: `sudo ufw default allow routed` en esa distro y `wsl --shutdown` (`docs/entorno.md`, P6) |
| `/api/status` → `Error conectando a PostgreSQL` | La BD no está lista o el `.env` no coincide | `docker compose ps db`; revisar `.env`. Si cambió la contraseña después del primer arranque, el volumen conserva la anterior: `docker compose down -v` (borra los datos) |
| `Temporary failure in name resolution` durante `docker build` (WSL2) | Los contenedores heredan el DNS `10.255.255.254` de WSL | `/etc/docker/daemon.json` con `{"dns":["8.8.8.8","1.1.1.1"]}` y reiniciar Docker |
| `DEPRECATED: The legacy builder is deprecated` | Enlaces rotos de Docker Desktop en `/usr/local/lib/docker/cli-plugins` | `sudo find /usr/local/lib/docker/cli-plugins -xtype l -delete` |
| El contenedor `db` termina con `Exited (1)` y menciona `/var/lib/postgresql/data` | Volumen montado en la ruta de PostgreSQL ≤ 17 | Montar en `/var/lib/postgresql` (como en este repositorio) |
| `docker context ls` no marca `default` | El cliente apunta a Docker Desktop | `docker context use default` y desactivar la integración WSL de Docker Desktop |

## Entrega del proyecto (según la guía)

Según la guía GFPI-F-135 (sección 4 y Anexo C), **el único entregable calificable es este repositorio de GitHub**, evaluado al finalizar la semana 5.

### Cómo se entrega

1. Publique en el **aula virtual**:
   - el enlace del repositorio: **https://github.com/articulacionTics/docker_SENA**;
   - el **enlace público de GitHub Actions**, donde están las corridas del flujo creado: **https://github.com/articulacionTics/docker_SENA/actions**.
2. El repositorio y el paquete de GHCR deben ser **públicos**. Los dos lo son: los enlaces se abren y la imagen se descarga sin credenciales.
3. Este README debe identificar a la autora y lo desarrollado. Ver [Autora y trabajo desarrollado](#autora-y-trabajo-desarrollado).




### Evidencias por actividad

| Actividad | Evidencia en el repositorio |
|---|---|
| AA1 — Requisitos y arquitectura | `docs/requisitos.md`, `docs/arquitectura.png` |
| AA2 — Entorno e imágenes base | `docs/entorno.md`, `docs/imagenes.md` |
| AA3 — Imagen propia con Dockerfile | `Dockerfile`, `.dockerignore`, `app/`, `docs/imagenes.md` §5 |
| AA4 — Orquestación con Compose y redes | `docker-compose.yml`, `nginx/default.conf` |
| AA5 — Validación, publicación y documentación | `docs/pruebas.md`, `.github/workflows/publicar-imagen.yml`, `docs/despliegue-automatizado.md`, `docs/manual-tecnico.md`, release `v1.0.0` |
| Transferencia — Servidor remoto | `deploy/docker-compose.prod.yml`, `docs/manual-tecnico.md` §9 y §11 |
| Desempeño | Historial de commits del repositorio y corridas de GitHub Actions |

### Lista de verificación antes de entregar

- [x] `docker compose up -d --build` funciona desde una copia limpia.
- [x] `.env` **no** está en el repositorio; solo `.env.example`.
- [x] La pestaña **Actions** muestra corridas en verde.
- [x] El paquete de GHCR es **público** y tiene etiquetas inmutables (`sha-…`, `1.0.0`).
- [x] Etiqueta `v1.0.0` publicada.
- [x] Enlace público de GitHub Actions verificado (se abre sin sesión).
- [x] Nombre de la autora y trabajo desarrollado en este README.
- [x] *Release* `v1.0.0` creado en GitHub (*Releases → Draft a new release*).
- [x] Despliegue en un servidor remoto en GCP: http://34.60.209.202:8080/health (Google Cloud e2-micro), con despliegue continuo desde GitHub Actions.
  
El estado verificado de cada criterio está en [`docs/checklist-anexo-c.md`](docs/checklist-anexo-c.md).

## Autora y trabajo desarrollado

**Lily Pardo** · Ficha **3602390** · SENA, Centro de Comercio y Servicios, Regional Tolima

- **Perfil personal de GitHub:** [@Lilypar59](https://github.com/Lilypar59)
- Cuenta donde se aloja el repositorio del proyecto: [articulacionTics](https://github.com/articulacionTics)

Proyecto desarrollado individualmente (equipo de un integrante).

### Lo que desarrollé

| Actividad | Trabajo realizado | Resultado |
|---|---|---|
| **AA1 — Requisitos y arquitectura** | Matriz de requisitos de infraestructura RI-01…RI-15 y RI-OS-01/02/03 (Windows, Linux, macOS), cada uno con criterio de aceptación y método de verificación; tabla de componentes HW/SW; diagrama de arquitectura con puertos, red interna y volumen | [`docs/requisitos.md`](docs/requisitos.md), [`docs/arquitectura.png`](docs/arquitectura.png) |
| **AA2 — Entorno e imágenes base** | Diagnóstico del equipo; Docker Engine **29.8.2** en Ubuntu 24.04 sobre **WSL2** (sin Docker Desktop); búsqueda, descarga e inspección de `postgres:18-alpine`, `python:3.14-slim` y `nginx:1.30-alpine`; PostgreSQL y Nginx como contenedores sueltos; **9 problemas de entorno diagnosticados y resueltos** (DNS de WSL en contenedores, builder antiguo, firewall UFW de otra distro, volumen de PostgreSQL 18…) | [`docs/entorno.md`](docs/entorno.md), [`docs/imagenes.md`](docs/imagenes.md) |
| **AA3 — Imagen propia** | API FastAPI mínima (`/health`, `/api/status`, `/api/notas`) con configuración solo por variables de entorno; **Dockerfile multi-etapa** con usuario sin privilegios `appuser` (UID 1001), sin `pip` en la imagen final y con `HEALTHCHECK`; ciclo de vida (`tag`, `history`, `rmi`, `system df`) | Imagen de **275 MB frente a 780 MB** sin multi-etapa (−65 %) |
| **AA4 — Orquestación** | `docker-compose.yml` con `db`, `api` y `proxy` en la red `interna`, volumen `pgdata`, healthchecks, `depends_on: service_healthy`, límites de memoria y `restart`; Nginx como reverse proxy; **solo el proxy expone un puerto** (8080) | Solución completa con **un solo comando** |
| **AA5 — Validación, publicación y documentación** | 10 pruebas documentadas (arranque, proxy, API→BD, red, persistencia, aislamiento, volumen, usuario, consumo y secretos); publicación **manual** en GHCR; flujo de **GitHub Actions** con caché y etiquetas inmutables `sha-…`; etiqueta `v1.0.0`; README y manual técnico | [`docs/pruebas.md`](docs/pruebas.md) (10/10 PASS), [Actions](https://github.com/articulacionTics/docker_SENA/actions) en verde, [`docs/despliegue-automatizado.md`](docs/despliegue-automatizado.md) |
| **Transferencia** | **Despliegue en un servidor remoto propio** (Google Cloud e2-micro, Ubuntu 24.04 + Docker Engine) con la imagen de GHCR y sin `build:`; **despliegue continuo** por SSH desde GitHub Actions, con secretos y verificación de `/health`; propuesta de escalamiento a la nube y consideraciones de la **Ley 1581 de 2012** | **http://34.60.209.202:8080/health**, [`deploy/docker-compose.prod.yml`](deploy/docker-compose.prod.yml), [`docs/manual-tecnico.md`](docs/manual-tecnico.md) |
| **Auditoría** | Prueba desde copia limpia (clonar → `cp .env.example .env` → `up`) y revisión de los 9 criterios del Anexo C | [`docs/checklist-anexo-c.md`](docs/checklist-anexo-c.md): **9 de 9 en PASS** |

Estado por fase: [`docs/estado-proyecto.md`](docs/estado-proyecto.md).
