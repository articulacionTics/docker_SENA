# AA5 — Publicación y despliegue automatizado

## 1. Cadena de integración y entrega continuas

```text
Desarrolladora ──git push──► main ──► GitHub Actions (runner limpio)
                                         │  checkout → Buildx → login GHCR (GITHUB_TOKEN)
                                         │  → etiquetas (latest, sha-xxxxxxx, x.y.z) → build + push
                                         ▼
                                  GHCR: ghcr.io/articulaciontics/docker_sena
                                         │  (pull de una etiqueta inmutable)
                                         ▼
                              Servidor remoto (Docker Engine)
                                docker compose pull → docker compose up -d → healthcheck /health
                                         │ si falla
                                         ▼
                              rollback: etiqueta anterior + docker compose up -d
```

## 2. Paso 1: publicación manual (una sola vez)

Antes de automatizar se publicó a mano, para entender qué repite después el flujo. Se usó un token personal (PAT) con permiso `write:packages`, que la usuaria introdujo de forma interactiva. **No está guardado en ningún archivo.**

```text
$ docker login ghcr.io -u articulacionTics          # contraseña = PAT (no se muestra)
Login Succeeded
$ docker tag api-app:1.0.0 ghcr.io/articulaciontics/docker_sena:1.0.0
$ docker push ghcr.io/articulaciontics/docker_sena:1.0.0
...
1.0.0: digest: sha256:24c0e65921e3b4bc23d4f99d930239f02bab873fc6edeb6bc67c2a5568ce1a59 size: 856
```

> El primer `push` se cortó con `net/http: timeout awaiting response headers` después de subir siete capas. Al reintentar, esas capas aparecieron como `Layer already exists` y el push terminó: los registries permiten reanudar subidas por capas.

El paquete se creó **privado** (comportamiento por defecto de GHCR). Se hizo **público** en *Package settings → Change visibility* y se dio rol **Write** al repositorio en *Manage Actions access*. Verificación sin credenciales:

```text
manifest 1.0.0 sin credenciales: HTTP 200
$ DOCKER_CONFIG=<vacío> docker pull ghcr.io/articulaciontics/docker_sena:1.0.0
Digest: sha256:24c0e65921e3b4bc23d4f99d930239f02bab873fc6edeb6bc67c2a5568ce1a59
$ docker run --rm ghcr.io/articulaciontics/docker_sena:1.0.0 id
uid=1001(appuser) gid=1001(appuser) groups=1001(appuser)
```

## 3. Paso 2: publicación automática con GitHub Actions

Archivo: [`.github/workflows/publicar-imagen.yml`](../.github/workflows/publicar-imagen.yml). Se dispara con `push` a `main` y con etiquetas `v*.*.*`.

| Pieza | Función |
|---|---|
| `on: push: branches: [main]` / `tags: ['v*.*.*']` | Disparadores |
| `runs-on: ubuntu-latest` | Runner limpio, creado y destruido en cada corrida |
| `permissions: packages: write` | Permite al token temporal escribir en GHCR |
| `secrets.GITHUB_TOKEN` | Credencial temporal que GitHub crea y revoca en cada corrida. No hay tokens en el repositorio |
| `docker/metadata-action` | Etiquetas: `latest` (solo la rama por defecto), `sha-xxxxxxx` (inmutable) y `x.y.z` (si hay tag `vx.y.z`) |
| `cache-from/cache-to: type=gha` | Reutiliza las capas entre corridas |

### Primera corrida en verde

- **Corrida:** https://github.com/articulacionTics/docker_SENA/actions/runs/37179035255
- **Commit:** `936efea` (`ci: publicar la imagen al integrar cambios en main`), evento `push`, rama `main`.
- **Duración:** de 05:08:55Z a 05:09:32Z (**37 s**).

| Job | Resultado |
|---|---|
| `construir-y-publicar` | ✅ success. Todos los pasos en éxito: checkout, Buildx, login, etiquetas, build y push |
| `desplegar` | ⏭️ skipped (desactivado a propósito: no hay servidor todavía, §5) |

Etiquetas publicadas, consultadas sin credenciales:

```text
{"name":"articulaciontics/docker_sena","tags":["1.0.0","latest","sha-936efea"]}
latest      -> sha256:d6e0d6dd801256f1fa1317b52f7f3f715dec9eba5d7557d2397bc50854cfd4b7
sha-936efea -> sha256:d6e0d6dd801256f1fa1317b52f7f3f715dec9eba5d7557d2397bc50854cfd4b7
```

Comprobación de la imagen construida por el runner:

```text
$ docker pull ghcr.io/articulaciontics/docker_sena:sha-936efea
$ docker run -d --name sena-ci-test ghcr.io/articulaciontics/docker_sena:sha-936efea
$ docker exec sena-ci-test python -c "...urlopen('http://127.0.0.1:8000/health')..."
{"status":"ok"}
$ docker exec sena-ci-test id
uid=1001(appuser) gid=1001(appuser) groups=1001(appuser)
$ docker image inspect ... org.opencontainers.image.revision / source
936efea5f7fda1a742a706d803470b2a769d9242 https://github.com/articulacionTics/docker_SENA
```

**Trazabilidad:** la etiqueta `sha-936efea` y la etiqueta OCI `revision` atan la imagen al commit exacto que la produjo.

### Efecto de la caché (segunda corrida)

La segunda corrida la disparó el commit `eedc2f7`, que agregó la documentación: https://github.com/articulacionTics/docker_SENA/actions/runs/37179196305 (✅ success).

| Corrida | Commit | Job `construir-y-publicar` (inicio → fin) | Duración del job |
|---|---|---|---:|
| 1.ª (sin caché) | `936efea` | 05:08:58Z → 05:09:31Z | **33 s** |
| 2.ª (con caché `type=gha`) | `eedc2f7` | 05:12:09Z → 05:12:30Z | **21 s** |

La segunda corrida tardó un **36 % menos**. Las capas de dependencias (el venv de la etapa *builder*) no cambiaron, así que se recuperaron de la caché en lugar de reinstalarse. Como el cambio fue solo de documentación y `docs/` está en `.dockerignore`, ni siquiera cambió el contexto de construcción.

### Publicación de la versión `v1.0.0` (etiqueta semver)

```text
$ git tag -a v1.0.0 -m "primera version"
$ git push origin v1.0.0
 * [new tag]         v1.0.0 -> v1.0.0
```

| Corrida | Evento | Resultado |
|---|---|---|
| https://github.com/articulacionTics/docker_SENA/actions/runs/37179265278 | push a `main` (`734cdec`) | ✅ success |
| https://github.com/articulacionTics/docker_SENA/actions/runs/37179266818 | push de la etiqueta `v1.0.0` | ✅ success |

Etiquetas en GHCR después de la publicación:

```text
{"tags":["1.0.0","latest","sha-936efea","sha-eedc2f7","sha-734cdec"]}
1.0.0        sha256:618ff09892a7250cbc50cd9700854b7f08677352a29ad0f1e9efb6941754f789
latest       sha256:618ff09892a7250cbc50cd9700854b7f08677352a29ad0f1e9efb6941754f789
sha-734cdec  sha256:618ff09892a7250cbc50cd9700854b7f08677352a29ad0f1e9efb6941754f789
```

> **Observación:** la corrida de la etiqueta `v1.0.0` **volvió a publicar** `1.0.0`. Ahora apunta a la imagen construida por el runner (`618ff098…`) en lugar de la subida a mano (`24c0e659…`). Una etiqueta de versión puede reescribirse si alguien vuelve a publicarla; una etiqueta `sha-` corresponde a un único commit. Por eso, en producción se recomienda desplegar por `sha-…` o fijar el *digest* (`imagen@sha256:…`).

## 4. Cómo continúa la cadena hasta producción

El job **`desplegar`** ya está escrito en el mismo workflow. Solo se ejecuta si el anterior terminó bien (`needs:`), si el cambio está en `main` y si la variable de repositorio `DESPLIEGUE_HABILITADO` vale `true`. Usa `environment: produccion`, lo que permite exigir **aprobación humana** antes de desplegar.

Lo que hace en el servidor, por SSH:

```bash
cd /srv/app && git pull --ff-only
export API_TAG=sha-<commit>                       # etiqueta inmutable recién publicada
docker compose --env-file .env -f deploy/docker-compose.prod.yml pull
docker compose --env-file .env -f deploy/docker-compose.prod.yml up -d   # recrea solo lo que cambió
```

En el servidor **no se construye nada**: `deploy/docker-compose.prod.yml` usa `image: ghcr.io/articulaciontics/docker_sena:${API_TAG}`, sin `build:`, y exige que `API_TAG` esté definida. Nunca usa `latest`.

### Secretos necesarios

Se cargan en *Settings → Secrets and variables → Actions*, **nunca en el repositorio**:

| Nombre | Tipo | Contenido |
|---|---|---|
| `SERVIDOR_HOST` | Secret | IP o nombre del servidor |
| `SERVIDOR_USUARIO` | Secret | Usuario SSH del equipo |
| `SERVIDOR_SSH_KEY` | Secret | Clave privada SSH cuya pública está en `~/.ssh/authorized_keys` del servidor |
| `DESPLIEGUE_HABILITADO` | Variable | `true` para activar el job |

El workflow pasa los secretos por `env:` y no los escribe en el comando, para que no aparezcan en el registro de la corrida.

### Verificación y rollback

1. **Verificar:** `docker compose ps` (api *healthy*) y `curl http://localhost:$PROXY_PORT/health` → `{"status":"ok"}`.
2. **Revertir un despliegue fallido:** volver a la etiqueta anterior, que sigue en GHCR porque las etiquetas `sha-` son inmutables:

   ```bash
   export API_TAG=sha-<commit_anterior>     # o 1.0.0
   docker compose --env-file .env -f deploy/docker-compose.prod.yml up -d
   ```

   No hay que reconstruir nada. Esto es posible porque producción nunca apunta a `latest`.

### Despliegue a mano frente a automatizado

| Aspecto | A mano | Automatizado (este repositorio) |
|---|---|---|
| Quién construye | Una persona en su portátil | Un runner limpio, a partir de `main` |
| Qué se despliega | Lo que hubiera en la carpeta local | Exactamente el commit de `main` (`sha-…`) |
| Credenciales | PAT en el equipo de quien publica | `GITHUB_TOKEN` temporal y secretos cifrados del repositorio |
| Trazabilidad | Depende de anotarlo | Etiqueta `sha-` y registro de cada corrida |
| Rollback | Reconstruir y volver a subir | Cambiar `API_TAG` y ejecutar `up -d` |
| Riesgo | Un error humano llega directo a producción | Aprobación humana opcional (`environment: produccion`) |

## 5. Estado

| Elemento | Estado |
|---|---|
| Publicación manual (`1.0.0`) | ✅ Hecha |
| Workflow en verde | ✅ Corrida 37179035255 |
| Imagen pública con etiqueta inmutable | ✅ `sha-936efea`, `1.0.0` |
| Job `desplegar` | Escrito y desactivado. Se activa cuando el instructor entregue el servidor (en el curso, el servidor del aula es compartido y no se despliega sobre él sin autorización) |
