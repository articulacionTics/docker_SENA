# AA2 — Administración de imágenes

Fecha: 2026-10-03 · Host: Ubuntu 24.04.1 (WSL2) · Docker Engine 28.0.1.

Se usan **etiquetas explícitas** y nunca `latest`, para que el despliegue sea reproducible: la misma etiqueta siempre resuelve a la misma versión mayor/menor. Para fijar una imagen exacta byte a byte se puede usar el *digest* (`imagen@sha256:...`), que se registra abajo.

## 1. Descarga

```bash
docker pull postgres:18-alpine
docker pull python:3.14-slim
docker pull nginx:1.30-alpine
docker images
```

Resultado de `docker images` (filtrado):

```text
REPOSITORY   TAG           IMAGE ID       SIZE      CREATED
python       3.14-slim     284cda8648f5   128MB     2 days ago
nginx        1.30-alpine   43d9d8c1f896   62.4MB    11 days ago
postgres     18-alpine     c293117fcecd   304MB     2 weeks ago
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

## 5. Imagen propia de la API (`api-app:1.0.0`)

PENDIENTE: se completará en AA3 con `docker build`, `docker images` y `docker history api-app:1.0.0`.
