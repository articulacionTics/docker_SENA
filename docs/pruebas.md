# AA5 — Pruebas de despliegue

- **Fecha:** 2026-10-04.
- **Entorno:** Windows 11 + WSL2 · Ubuntu 24.04.1 · Docker Engine 29.8.2 · Compose v5.6.0.
- **Código probado:** commit `665e376` de `main`. Se probó desde una copia de trabajo limpia (`git worktree`) con `cp .env.example .env`.

Todas las salidas son reales. Se recortan solo líneas de progreso.

## Resumen

| # | Prueba | Requisito | Resultado |
|---|---|---|---|
| P1 | Arranque desde cero con un solo comando | RI-01, RI-11 | **PASS** |
| P2 | `/health` a través del proxy Nginx | RI-10 | **PASS** |
| P3 | API → PostgreSQL | RI-09 | **PASS** |
| P4 | Red interna: resolución por nombre de servicio | RI-09 | **PASS** |
| P5 | Persistencia tras `down` + `up` | RI-03 | **PASS** |
| P6 | Aislamiento: solo el proxy expuesto | RI-02 | **PASS** |
| P7 | Volumen nombrado | RI-08 | **PASS** |
| P8 | Usuario sin privilegios y configuración por entorno | RI-07, RI-05 | **PASS** |
| P9 | Consumo de recursos (≤ 4 GB) | RI-04 | **PASS** |
| P10 | Secretos fuera de Git | RI-05 | **PASS** |
| P11 | Copia limpia desde GitHub | RI-12 | ver `docs/checklist-anexo-c.md` |

---

## P1 — Arranque desde cero (RI-01, RI-11)

`down -v` se usa **solo aquí**, para partir sin datos. No se usa en la prueba de persistencia.

```text
$ docker compose down -v
 Volume docker-sena_pgdata Removed
 Network docker-sena_interna Removed
$ docker compose up -d --build
 Image api-app:1.0.0 Built
 Network docker-sena_interna Created
 Volume docker-sena_pgdata Created
 Container docker-sena-db-1 Started
 Container docker-sena-db-1 Healthy
 Container docker-sena-api-1 Started
 Container docker-sena-api-1 Healthy
 Container docker-sena-proxy-1 Started
(listo en 36 s)
$ docker compose ps
NAME                  IMAGE                STATUS                    PORTS
docker-sena-api-1     api-app:1.0.0        Up 6 seconds (healthy)    8000/tcp
docker-sena-db-1      postgres:18-alpine   Up 16 seconds (healthy)   5432/tcp
docker-sena-proxy-1   nginx:1.30-alpine    Up Less than a second     0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

El orden de arranque lo garantizan los `healthcheck` y `depends_on: condition: service_healthy`: primero **db**; luego **api**, cuando db está *healthy*; y por último **proxy**, cuando api está *healthy*.

## P2 — `/health` a través del proxy (RI-10)

```text
$ curl -i http://localhost:8080/health
HTTP/1.1 200 OK
Server: nginx/1.30.5
{"status":"ok"}
```

La cabecera `Server: nginx/1.30.5` demuestra que la respuesta pasa por el reverse proxy. La API no tiene puerto propio en el host (P6).

## P3 — API → PostgreSQL (RI-09)

```text
$ curl http://localhost:8080/api/status
{"api":"ok","database":"connected","db_host":"db","db_ip":"172.18.0.2","db_name":"appdb","postgres_version":"18.6","api_hostname":"280da33235f8"}
```

## P4 — Red interna (RI-09)

```text
$ docker compose exec api python -c "import socket; print(socket.gethostbyname('db'))"
172.18.0.2
$ docker network inspect docker-sena_interna
driver=bridge subnet=172.18.0.0/16
docker-sena-api-1    172.18.0.3/16
docker-sena-db-1     172.18.0.2/16
docker-sena-proxy-1  172.18.0.4/16
```

La API resuelve `db` a una **IP privada de la red interna** gracias al DNS embebido de Docker. El código no contiene IPs fijas ni `localhost`.

## P5 — Persistencia (RI-03)

```text
$ curl -X POST -H 'Content-Type: application/json' -d '{"texto":"dato persistente AA5"}' http://localhost:8080/api/notas
{"id":1,"texto":"dato persistente AA5"}
$ curl http://localhost:8080/api/notas
[{"id":1,"texto":"dato persistente AA5","creado_en":"2026-10-04T04:55:43.073540+00:00"}]

$ docker compose down && docker compose up -d
 Container docker-sena-proxy-1 Removed
 Container docker-sena-api-1 Removed
 Container docker-sena-db-1 Removed
 Network docker-sena_interna Removed
 Container docker-sena-db-1 Started
 Container docker-sena-api-1 Started
 Container docker-sena-proxy-1 Started
$ docker volume ls --filter name=docker-sena
DRIVER    VOLUME NAME
local     docker-sena_pgdata                ← los contenedores se eliminaron; el volumen no

$ curl http://localhost:8080/api/notas
[{"id":1,"texto":"dato persistente AA5","creado_en":"2026-10-04T04:55:43.073540+00:00"}]
```

El registro sobrevive a la eliminación y recreación de los tres contenedores.

## P6 — Aislamiento (RI-02)

```text
$ docker compose port db 5432 || echo "correcto: la BD no publica ningun puerto"
:0
$ curl --max-time 3 http://localhost:5432 || echo "correcto: la BD no responde desde el host"
correcto: la BD no responde desde el host
$ docker compose port api 8000 || echo "correcto: la API no publica ningun puerto"
:0
$ curl --max-time 3 http://localhost:8000 || echo "correcto: la API no responde desde el host"
correcto: la API no responde desde el host
$ docker compose port proxy 80
0.0.0.0:8080
```

> Con Docker Compose v5, `docker compose port` sobre un puerto **no publicado** imprime `:0` (puerto 0, es decir, sin asignar) y termina sin error, por lo que el `|| echo` de la guía no llega a ejecutarse. El `curl` lo confirma: ni 5432 ni 8000 responden desde el host. Solo `proxy` tiene un mapeo real (`0.0.0.0:8080`). En `docker-compose.yml`, `db` y `api` **no tienen sección `ports`**.

| Destino | Desde el host | Resultado |
|---|---|---|
| `localhost:8080` (proxy) | permitido | 200 OK |
| `localhost:8000` (api) | no publicado | sin respuesta |
| `localhost:5432` (db) | no publicado | sin respuesta |

## P7 — Volumen (RI-08)

```text
$ docker volume inspect docker-sena_pgdata
Name=docker-sena_pgdata Driver=local Mountpoint=/var/lib/docker/volumes/docker-sena_pgdata/_data
$ docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SHOW data_directory;"'
/var/lib/postgresql/18/docker
```

El volumen está montado en `/var/lib/postgresql`, la ruta oficial para PostgreSQL 18+, y PostgreSQL escribe sus datos en el subdirectorio `18/docker`, dentro del volumen. En `docs/imagenes.md` §4 se explica por qué no se usa `/var/lib/postgresql/data`.

## P8 — Usuario sin privilegios y configuración (RI-07, RI-05)

```text
$ docker compose exec api id
uid=1001(appuser) gid=1001(appuser) groups=1001(appuser)
$ docker compose exec api sh -c 'echo DB_HOST=$DB_HOST'
DB_HOST=db
```

## P9 — Consumo de recursos (RI-04)

```text
$ docker stats --no-stream
NAME                  CPU %     MEM USAGE / LIMIT   MEM %
docker-sena-proxy-1   0.00%     13.57MiB / 64MiB    21.21%
docker-sena-api-1     0.11%     49.25MiB / 256MiB   19.24%
docker-sena-db-1      7.85%     17.93MiB / 512MiB   3.50%
```

**Observación:** con los tres servicios arriba, el consumo total es de **≈ 81 MiB**. La suma de los límites configurados es de 832 MiB, muy por debajo de los 4 GB del requisito. Es una medición puntual en reposo; con carga real el consumo crece, pero queda acotado por los límites de `deploy.resources.limits`.

## P10 — Secretos fuera de Git (RI-05)

```text
$ git ls-files | grep -x .env
(vacío: .env no versionado)
$ git check-ignore -v .env
.gitignore:2:.env	.env
$ grep -rnE 'cambiar_esta_clave|claveAdmin|password\s*=' app/
(sin credenciales en el código)
```

Las credenciales llegan a los contenedores como variables de entorno desde `.env`. El repositorio solo versiona `.env.example`, con valores ficticios.

## Registros de operación (`docker compose logs`)

```text
$ docker compose logs --tail 5 api
api-1  | INFO:     Application startup complete.
api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
api-1  | INFO:     127.0.0.1:52514 - "GET /health HTTP/1.1" 200 OK        ← healthcheck interno
api-1  | INFO:     172.18.0.1:0 - "GET /health HTTP/1.1" 200 OK
api-1  | INFO:     172.18.0.1:0 - "GET /api/notas HTTP/1.1" 200 OK
$ docker compose logs --tail 3 proxy
proxy-1  | 172.18.0.1 - - [04/Oct/2026:04:56:01 +0000] "GET /health HTTP/1.1" 200 15 "-" "curl/8.5.0" "-"
proxy-1  | 172.18.0.1 - - [04/Oct/2026:04:56:01 +0000] "GET /api/notas HTTP/1.1" 200 88 "-" "curl/8.5.0" "-"
```

## Incidencias encontradas durante las pruebas

Las pruebas detectaron un fallo real antes de pasar: con el UFW de otra distribución WSL activo, `/health` devolvía **504 Gateway Time-out** y la API no conectaba con `db`. Se corrigió en el entorno, sin cambiar el proyecto. Ver `docs/entorno.md`, problemas P6 y P9.
