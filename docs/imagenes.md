# AA2 — Administración de imágenes

Fecha: 2026-10-03 · Host: Ubuntu 24.04.1 (WSL2) · Primera práctica con Docker Engine 28.0.1; repetida y ampliada con **29.8.2** (ver `docs/entorno.md`, P2).

Se usan **etiquetas explícitas** y nunca `latest`, para que el despliegue sea reproducible: la misma etiqueta siempre resuelve a la misma versión mayor/menor. Para fijar una imagen exacta byte a byte se puede usar el *digest* (`imagen@sha256:...`), que se registra abajo.

## 1. Buscar y descargar

```text
$ docker search postgres --limit 5
NAME                DESCRIPTION                                     STARS     OFFICIAL
postgres            The PostgreSQL object-relational database sy…   15028     [OK]
cimg/postgres                                                       9
circleci/postgres   The PostgreSQL object-relational database sy…   35
kasmweb/postgres    Postgres image maintained by Kasm Technologi…   6
elestio/postgres    Postgres, verified and packaged by Elestio      2
```

Se elige la imagen marcada como **OFFICIAL**, porque la mantiene Docker y el proyecto PostgreSQL.

```bash
docker pull postgres:18-alpine
docker pull python:3.14-slim
docker pull nginx:1.30-alpine
docker images
```

`docker images` con Docker Engine 29 (almacén containerd). *DISK USAGE* es el tamaño descomprimido en disco y *CONTENT SIZE* el tamaño comprimido que se descarga:

```text
IMAGE                ID             DISK USAGE   CONTENT SIZE
python:3.14-slim     c3e521df8b2b        192MB         48.7MB
nginx:1.30-alpine    0985e772fb9f       93.6MB           27MB
postgres:18-alpine   77f585114c32        433MB          121MB
```

Con Engine 28 (almacén clásico) las mismas imágenes reportaban 128 MB, 62.4 MB y 304 MB. Con Engine 29 la cifra es mayor porque el almacén containerd también conserva el contenido comprimido. Los *digest* son los mismos.

`docker image inspect postgres:18-alpine | head -30` (extracto):

```text
"RepoTags": [ "postgres:18-alpine" ],
"RepoDigests": [ "postgres@sha256:77f585114c32fbca283dc835b0596f4e52b51b4c6662d7810b2f4084f60a1873" ],
"Created": "2026-09-17T21:29:50.207676277Z",
"ExposedPorts": { "5432/tcp": {} },
"Env": [ ..., "PG_MAJOR=18", "PG_VERSION=18.6", ..., "PGDATA=/var/lib/postgresql/18/docker" ],
"Entrypoint": [ "docker-entrypoint.sh" ],
"Cmd": [ "postgres" ]
```

## 2. Ficha de cada imagen

Datos obtenidos con `docker image inspect <imagen>` y ejecutando el binario dentro del contenedor (`docker run --rm <imagen> <cmd> --version`).

### postgres:18-alpine

| Campo | Valor |
|---|---|
| Propósito | Base de datos del servicio `db` |
| Versión | PostgreSQL **18.6** (`postgres --version`) · Alpine 3.24.2 |
| Arquitectura / SO | amd64 / linux |
| Tamaño | 304 MB (303 729 906 bytes) · 9 capas |
| Digest | `postgres@sha256:77f585114c32fbca283dc835b0596f4e52b51b4c6662d7810b2f4084f60a1873` |
| Creada | 2026-09-17 |
| Puerto expuesto | 5432/tcp |
| Volumen declarado | `/var/lib/postgresql` |
| PGDATA por defecto | `/var/lib/postgresql/18/docker` |
| Entrypoint / Cmd | `docker-entrypoint.sh` / `postgres` |
| Descarga | `docker pull postgres:18-alpine` |
| Inspección | `docker image inspect postgres:18-alpine` |

### python:3.14-slim

| Campo | Valor |
|---|---|
| Propósito | Imagen base de la API (etapas *builder* y *runtime* del Dockerfile) |
| Versión | Python **3.14.8** · Debian 13.7 (*slim*) |
| Arquitectura / SO | amd64 / linux |
| Tamaño | 128 MB (127 876 699 bytes) · 4 capas |
| Digest | `python@sha256:0741d101873c12ab927e6f8653feb8862b9bd58771177acb1b885b95141f91b4` |
| Creada | 2026-10-01 |
| Usuario por defecto | root (por eso el Dockerfile crea `appuser`) |
| Cmd | `python3` |
| Descarga | `docker pull python:3.14-slim` |
| Inspección | `docker image inspect python:3.14-slim` |

### nginx:1.30-alpine

| Campo | Valor |
|---|---|
| Propósito | Reverse proxy del servicio `proxy` |
| Versión | nginx **1.30.5** (`nginx -v`) · Alpine 3.24.2 |
| Arquitectura / SO | amd64 / linux |
| Tamaño | 62.4 MB (62 394 233 bytes) · 8 capas |
| Digest | `nginx@sha256:0985e772fb9f729e6fa0980da05fca5d9c468e870eed43071545afa9d2e27d94` |
| Creada | 2026-09-22 |
| Puerto expuesto | 80/tcp |
| Entrypoint / Cmd | `/docker-entrypoint.sh` / `nginx -g daemon off;` |
| Descarga | `docker pull nginx:1.30-alpine` |
| Inspección | `docker image inspect nginx:1.30-alpine` |

**Alpine o slim:** Alpine (musl) produce imágenes muy pequeñas y conviene para servicios ya compilados, como Nginx y PostgreSQL. Para Python se elige `slim` (Debian, glibc), porque las *wheels* binarias de PyPI, como la de `psycopg[binary]`, se publican principalmente para glibc. Así se evita compilar dependencias.

## 3. Práctica: Nginx independiente

```bash
docker run -d --name web -p 8080:80 nginx:1.30-alpine
curl -i http://localhost:8080
docker logs web
docker rm -f web
```

Resultado:

```text
web nginx:1.30-alpine Up 2 seconds 0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
HTTP/1.1 200 OK
Server: nginx/1.30.5
Content-Type: text/html
<title>Welcome to nginx!</title>
172.17.0.1 - - [04/Oct/2026:00:01:24 +0000] "GET / HTTP/1.1" 200 896 "-" "curl/8.5.0" "-"
```

El contenedor se eliminó al terminar.

## 4. Práctica: PostgreSQL independiente con volumen `pgdata-practica`

El objetivo es demostrar creación, ejecución, logs, persistencia y eliminación. Se probaron tres formas de montar el volumen, porque PostgreSQL 18 cambió la ruta de los datos.

### Experimento A: montaje clásico `/var/lib/postgresql/data` (falla)

```bash
docker volume create pgdata-practica
docker run -d --name pg-practica -e POSTGRES_PASSWORD=*** \
  -v pgdata-practica:/var/lib/postgresql/data postgres:18-alpine
docker logs pg-practica
```

```text
pg-practica Exited (1) 3 seconds ago
       Counter to that, there appears to be PostgreSQL data in:
         /var/lib/postgresql/data (unused mount/volume)
       ...
       The suggested container configuration for 18+ is to place a single mount
       at /var/lib/postgresql which will then place PostgreSQL data in a
       subdirectory, allowing usage of "pg_upgrade --link" without mount point
       boundary issues.
```

### Experimento B: `/var/lib/postgresql/data` + `PGDATA=/var/lib/postgresql/data` (funciona, pero crea un volumen extra)

```text
SHOW data_directory  → /var/lib/postgresql/data
Mounts:
  volume pgdata-practica -> /var/lib/postgresql/data
  volume b00cf4f0...     -> /var/lib/postgresql      ← volumen anónimo adicional
```

Los datos persisten, pero Docker crea un volumen anónimo por el `VOLUME /var/lib/postgresql` de la imagen. Ese volumen queda huérfano al eliminar el contenedor.

### Experimento C: montaje `/var/lib/postgresql` (recomendación oficial para PG 18+)

```bash
docker volume create pgdata-practica
docker run -d --name pg-practica -e POSTGRES_PASSWORD=*** \
  -v pgdata-practica:/var/lib/postgresql postgres:18-alpine
docker exec pg-practica psql -U postgres -tAc "SHOW data_directory;"
docker exec pg-practica psql -U postgres \
  -c "CREATE TABLE prueba(id serial primary key, nota text);" \
  -c "INSERT INTO prueba(nota) VALUES ('dato persistente AA2');"
docker rm -f pg-practica                       # se elimina el contenedor, no el volumen
docker run -d --name pg-practica -e POSTGRES_PASSWORD=*** \
  -v pgdata-practica:/var/lib/postgresql postgres:18-alpine
docker exec pg-practica psql -U postgres -c "SELECT * FROM prueba;"
docker volume inspect pgdata-practica
```

```text
Mounts:
  volume pgdata-practica -> /var/lib/postgresql   ← un único volumen
SHOW data_directory → /var/lib/postgresql/18/docker
CREATE TABLE
INSERT 0 1
pg-practica
 id |         nota
----+----------------------
  1 | dato persistente AA2
(1 row)
pgdata-practica local /var/lib/docker/volumes/pgdata-practica/_data
```

**Conclusión:** el dato sobrevivió a la eliminación y recreación del contenedor porque está en el volumen nombrado. La opción C es la más limpia: un solo volumen y compatible con `pg_upgrade`.

### Limpieza

```bash
docker rm -f pg-practica
docker volume rm pgdata-practica
```

No quedan contenedores de práctica (`web`, `pg-practica`) ni el volumen `pgdata-practica`.

## 5. AA3 — Imagen propia de la API (`api-app:1.0.0`)

### 5.1 Construcción (Dockerfile multi-etapa)

El `Dockerfile` tiene dos etapas:

- **builder** (`python:3.14-slim`): crea el entorno virtual `/opt/venv`, instala `app/requirements.txt` y luego desinstala `pip`.
- **runtime** (`python:3.14-slim`): copia solo `/opt/venv` y `app/`, crea `appuser` (UID/GID 1001, sin shell de login), ejecuta `USER appuser`, `EXPOSE 8000`, `HEALTHCHECK` contra `/health` y `CMD uvicorn`.

`.dockerignore` excluye `.git`, `.env`, `docs`, `__pycache__` y otros archivos que no necesita la imagen.

```text
$ docker build -t api-app:1.0.0 .
#10 [builder 4/4] RUN python -m venv /opt/venv && /opt/venv/bin/pip install -r requirements.txt && /opt/venv/bin/pip uninstall -y pip
#10 13.30 Successfully installed ... fastapi-0.142.2 ... psycopg-3.3.6 psycopg-binary-3.3.6 ... uvicorn-0.54.0 ...
#10 13.63   Successfully uninstalled pip-26.2.1
#11 [runtime 4/5] COPY --from=builder /opt/venv /opt/venv
#12 [runtime 5/5] COPY app/ ./app/
#13 naming to docker.io/library/api-app:1.0.0 done
(build con BuildKit: 19 s)

$ docker images | grep api-app
api-app:1.0.0        f622e63d649f        275MB           65MB

$ docker run --rm api-app:1.0.0 id
uid=1001(appuser) gid=1001(appuser) groups=1001(appuser)
```

Comprobaciones adicionales: `/build` (la etapa builder) **no existe** en la imagen final y el venv de runtime no contiene `pip`. Con el contenedor sin base de datos, `/health` responde `{"status":"ok"}`. La API arranca aunque falten las variables de la BD y lo registra como advertencia: `No se pudo inicializar el esquema: Faltan variables de entorno: DB_NAME, DB_ADMIN_PASSWORD`.

### 5.2 Capas (`docker history api-app:1.0.0`)

```text
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
f622e63d649f   3 seconds ago    CMD ["uvicorn" "app.main:app" "--host" "0.0.…   0B        buildkit.dockerfile.v0
<missing>      3 seconds ago    HEALTHCHECK {Test:[CMD python -c import urll…   0B        buildkit.dockerfile.v0
<missing>      3 seconds ago    EXPOSE [8000/tcp]                               0B        buildkit.dockerfile.v0
<missing>      3 seconds ago    USER appuser                                    0B        buildkit.dockerfile.v0
<missing>      3 seconds ago    COPY app/ ./app/ # buildkit                     24.6kB    buildkit.dockerfile.v0
<missing>      3 seconds ago    COPY /opt/venv /opt/venv # buildkit             66.8MB    buildkit.dockerfile.v0
<missing>      17 seconds ago   WORKDIR /srv                                    4.1kB     buildkit.dockerfile.v0
<missing>      17 seconds ago   RUN /bin/sh -c groupadd --system --gid 1001 …   41kB      buildkit.dockerfile.v0
<missing>      17 seconds ago   ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFER…   0B        buildkit.dockerfile.v0
<missing>      17 seconds ago   LABEL org.opencontainers.image.title=docker-…   0B        buildkit.dockerfile.v0
<missing>      2 days ago       CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      2 days ago       RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      2 days ago       RUN /bin/sh -c set -eux;   savedAptMark="$(a…   42MB      buildkit.dockerfile.v0
<missing>      2 days ago       ENV PYTHON_SHA256=c2215904f02b175596dc493515…   0B        buildkit.dockerfile.v0
<missing>      2 days ago       ENV PYTHON_VERSION=3.14.8                       0B        buildkit.dockerfile.v0
<missing>      2 days ago       RUN /bin/sh -c set -eux;  apt-get update;  a…   13.2MB    buildkit.dockerfile.v0
<missing>      2 days ago       ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      2 weeks ago      # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.6MB    debuerreotype 0.17
```

Lectura de la tabla: las capas propias del proyecto suman **≈ 67 MB**, casi todo el venv. El resto pertenece a la imagen base `python:3.14-slim`. La capa `USER appuser` confirma que el proceso no se ejecuta como root.

### 5.3 Ciclo de vida de la imagen (AA3, paso 3)

```text
$ docker tag api-app:1.0.0 api-app:latest          # etiquetar/versionar (solo práctica local)
$ docker images api-app
IMAGE            ID             DISK USAGE   CONTENT SIZE
api-app:1.0.0    f622e63d649f        275MB           65MB
api-app:latest   f622e63d649f        275MB           65MB      ← misma imagen, dos etiquetas
api-app:single   616a57d1c5e3        780MB          206MB

$ docker system df
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          5         0         1.381GB   1.179GB (85%)
Containers      0         0         0B        0B
Local Volumes   0         0         0B        0B
Build Cache     18        0         938.5MB   591.5MB

$ docker rmi api-app:single                         # eliminar la imagen que no se usa
Untagged: api-app:single
Deleted: sha256:616a57d1c5e35887089d0d947630773cba011662c0bece1ac12560a619c81300
$ docker rmi api-app:latest
Untagged: api-app:latest

$ docker system df
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          4         0         791.1MB   588.8MB (74%)
```

### 5.4 Comparación: multi-etapa frente a una sola etapa

Para comparar se construyó una imagen equivalente **sin multi-etapa** (`api-app:single`): una sola etapa sobre `python:3.14-slim` que instala `build-essential` y las dependencias con la caché de pip, y ejecuta como root. Se eliminó al terminar y no forma parte del repositorio.

| Imagen | Etapas | Tamaño en disco | Tamaño comprimido (descarga) | Usuario |
|---|---|---:|---:|---|
| `api-app:1.0.0` | 2 (builder + runtime) | **275 MB** | **65 MB** | appuser (1001) |
| `api-app:single` | 1 | 780 MB | 206 MB | root |
| **Reducción** | | **−65 %** | **−68 %** | |

La guía espera una imagen de «decenas de MB». La imagen comprimida que se descarga del registry pesa **65 MB**, pero en disco ocupa 275 MB, porque la base `python:3.14-slim` ya ocupa 192 MB descomprimida. Bajar de esa cifra exigiría otra base (por ejemplo, *distroless* o Alpine con musl), y eso pierde las *wheels* glibc de `psycopg[binary]`.
