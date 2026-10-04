# Manual técnico — Docker Multiservice Lab

- **Proyecto:** despliegue de una aplicación web multiservicio en contenedores Docker.
- **Programa:** SENA 22810024 · Competencia 220501086 (RA1 y RA2).
- **Autora:** Lily Pardo (ficha 3602390).
- **Repositorio:** https://github.com/articulacionTics/docker_SENA

## 1. Arquitectura

![Arquitectura](arquitectura.png)

```text
Cliente ──HTTP :8080──► proxy (Nginx :80) ──HTTP──► api (FastAPI :8000) ──TCP──► db (PostgreSQL :5432)
                        └──────────────────────── red bridge "interna" ────────────────────────┘
                                                                                   db ──► volumen pgdata
```

Hay un único punto de entrada: el proxy. La API y la base de datos no son accesibles desde fuera del host Docker. La comunicación interna se hace por **nombre de servicio**, gracias al DNS embebido de Docker, nunca por IP ni por `localhost`.

## 2. Componentes

| Servicio | Imagen | Rol | Healthcheck | Límite de memoria | Reinicio |
|---|---|---|---|---:|---|
| `proxy` | `nginx:1.30-alpine` + `nginx/default.conf` (montado `:ro`) | Reverse proxy hacia `http://api:8000`; agrega `X-Real-IP`, `X-Forwarded-For` y `X-Forwarded-Proto` | (depende de api *healthy*) | 64 MiB | `unless-stopped` |
| `api` | `api-app:1.0.0` / `ghcr.io/articulaciontics/docker_sena` | FastAPI + Uvicorn. Endpoints `/health`, `/api/status`, `/api/notas` | `GET /health` cada 15 s | 256 MiB | `unless-stopped` |
| `db` | `postgres:18-alpine` | PostgreSQL 18.6, `shared_buffers=32MB`, `max_connections=20` | `pg_isready` cada 10 s | 512 MiB | `unless-stopped` |

**Imagen de la API (Dockerfile multi-etapa).** La etapa *builder* instala las dependencias fijadas en un venv y elimina `pip`. La etapa *runtime* copia solo el venv y `app/`, y ejecuta como `appuser` (UID 1001). Ocupa 275 MB en disco (65 MB comprimida), frente a 780 MB de la variante de una sola etapa (`docs/imagenes.md` §5).

**Orden de arranque:** `db` (healthy) → `api` (healthy) → `proxy`, mediante `depends_on: condition: service_healthy`.

## 3. Puertos

| Servicio | Puerto interno | Publicado en el host | Acceso |
|---|---:|---|---|
| proxy | 80 | **8080** (local) / `PROXY_PORT` (servidor) | Público |
| api | 8000 | — | Solo desde la red `interna` |
| db | 5432 | — | Solo desde la red `interna` |

## 4. Redes

| Red | Driver | Subred (asignada por Docker) | Miembros |
|---|---|---|---|
| `docker-sena_interna` | bridge | p. ej. 172.18.0.0/16 | proxy, api, db |

Solo el proxy tiene un mapeo de puerto hacia el host. Verificación: `docs/pruebas.md` P4 y P6.

## 5. Volúmenes

| Volumen | Montaje | Contenido | Ciclo de vida |
|---|---|---|---|
| `docker-sena_pgdata` | `db:/var/lib/postgresql` | Datos de PostgreSQL (`/var/lib/postgresql/18/docker`) | Sobrevive a `down`; se borra solo con `down -v` |

Respaldo sugerido: `docker compose exec db pg_dump -U "$DB_USER" "$DB_NAME" > respaldo.sql`.

## 6. Seguridad

- **Aislamiento de red:** solo el proxy expone un puerto; la BD y la API no tienen `ports` (RI-02).
- **Privilegio mínimo:** la API se ejecuta como `appuser` (UID 1001), sin shell de login. El código es propiedad de root y de solo lectura para ese usuario. La imagen final no contiene `pip` ni herramientas de compilación.
- **Secretos:** las credenciales llegan por variables de entorno desde `.env`, que no se versiona (`.gitignore`). El repositorio solo contiene `.env.example`, con valores ficticios. En CI se usa el `GITHUB_TOKEN` temporal; los datos del servidor van en *GitHub Secrets* y se pasan por `env:`, para que no aparezcan en el registro.
- **Reproducibilidad:** imágenes base con etiqueta explícita (sin `latest`), dependencias de Python fijadas y etiquetas inmutables (`sha-…`, `x.y.z`) en producción.
- **Configuración en solo lectura:** `nginx/default.conf` se monta con `:ro`.

## 7. Variables de entorno

| Variable | Servicio | Descripción |
|---|---|---|
| `DB_NAME` | db (`POSTGRES_DB`), api | Nombre de la base de datos |
| `DB_USER` | db (`POSTGRES_USER`), api | Usuario de PostgreSQL |
| `DB_ADMIN_PASSWORD` | db (`POSTGRES_PASSWORD`), api | Contraseña (secreta) |
| `DB_HOST` | api | Siempre `db` (nombre del servicio) |
| `DB_PORT` | api | `5432` |
| `API_TAG` | servidor | Etiqueta inmutable de la imagen a desplegar |
| `PROXY_PORT` | servidor | Puerto asignado en el servidor (por defecto 8080) |

## 8. Despliegue local

```bash
git clone https://github.com/articulacionTics/docker_SENA.git && cd docker_SENA
cp .env.example .env
docker compose up -d --build
docker compose ps
curl http://localhost:8080/health          # {"status":"ok"}
```

Operación: `docker compose logs -f api` · `docker compose exec api sh` · `docker stats` · `docker compose down` (conserva los datos) · `docker compose down -v` (borra los datos).

## 9. Despliegue remoto

**Estado: ✅ desplegado y funcionando** en **http://34.60.209.202:8080/health**. Es un servidor propio en Google Cloud, porque el servidor del instructor aún no estaba disponible. La VM estará encendida hasta el martes **2026-10-06**; después se elimina para no generar costos.

### 9.1 Servidor

| Dato | Valor |
|---|---|
| Proveedor | Google Cloud Compute Engine, nivel gratuito (*Always Free*): estimación de lista USD 6.11/mes, cubierta por el nivel gratuito; con presupuesto y alerta de USD 1 |
| Máquina | `e2-micro`: 2 vCPU compartidas, 1 GB de RAM y 1 GB de swap añadido |
| Disco | Disco persistente estándar de 30 GB |
| Sistema | Ubuntu 24.04 LTS (x86/64), Docker Engine y Compose desde el repositorio oficial (guía AA2, apartado 2A) |
| Firewall de VPC | `permitir-8080` (TCP 8080, para la aplicación) y `permitir-ssh` (TCP 22, para GitHub Actions) |
| Ruta de la aplicación | `/srv/app`, copia del repositorio |
| Arquitectura | x86/64, la misma que la imagen publicada en GHCR (`linux/amd64`) |

### 9.2 Procedimiento realizado

```bash
ssh <usuario>@<servidor>                          # en GCP: botón "SSH" de la consola
git clone https://github.com/articulacionTics/docker_SENA.git /srv/app && cd /srv/app
cp .env.example .env
sed -i "s/^DB_ADMIN_PASSWORD=.*/DB_ADMIN_PASSWORD=$(openssl rand -hex 16)/" .env   # contraseña propia
export API_TAG=1.0.0                              # etiqueta inmutable publicada en GHCR
export PROXY_PORT=8080
docker compose --env-file .env -f deploy/docker-compose.prod.yml pull
docker compose --env-file .env -f deploy/docker-compose.prod.yml up -d
docker compose --env-file .env -f deploy/docker-compose.prod.yml ps
curl http://localhost:$PROXY_PORT/health
```

En el servidor **no hay `build:`**: `deploy/docker-compose.prod.yml` usa `image: ghcr.io/articulaciontics/docker_sena:${API_TAG}` y se niega a arrancar si `API_TAG` no está definida. Así, producción ejecuta exactamente la imagen probada y trazable a un commit.

### 9.3 Verificación desde Internet (2026-10-04)

```text
$ curl -i http://34.60.209.202:8080/health
HTTP/1.1 200 OK
Server: nginx/1.30.5
{"status":"ok"}

$ curl http://34.60.209.202:8080/api/status
{"api":"ok","database":"connected","db_host":"db","db_ip":"172.18.0.2","db_name":"appdb","postgres_version":"18.6","api_hostname":"16660b3a4ebf"}

$ curl http://34.60.209.202:8080/docs        → «Docker Multiservice Lab API - Swagger UI»
$ curl --max-time 5 http://34.60.209.202:8000 → sin respuesta (correcto: la API no está expuesta)
$ curl --max-time 5 http://34.60.209.202:5432 → sin respuesta (correcto: la BD no está expuesta)
```

### 9.4 Despliegue continuo (GitHub Actions → servidor)

| Paso | Evidencia |
|---|---|
| Configuración | Clave SSH dedicada (`deploy_github`, con su pública en `authorized_keys`); secretos del repositorio `SERVIDOR_HOST`, `SERVIDOR_USUARIO`, `SERVIDOR_SSH_KEY`; variable `DESPLIEGUE_HABILITADO=true`; *environment* `produccion` |
| Incidencia | La primera vez los secretos se crearon como *Variables* y no como *Secrets*: `ssh` recibió un destino vacío (`usage: ssh …`, código 255). Se agregó al workflow un paso que valida los secretos sin mostrarlos ([corrida 37225163601](https://github.com/articulacionTics/docker_SENA/actions/runs/37225163601): «Falta el secreto SERVIDOR_HOST…») y se corrigió la configuración |
| Primer despliegue automático | [Corrida 37225015773](https://github.com/articulacionTics/docker_SENA/actions/runs/37225015773) (intento 2): job `desplegar` en ✅ success |
| **Despliegue continuo demostrado** | El commit `f5d72ca` cambió `/health` de `{"status":"okis"}` (un cambio de prueba) a `{"status":"ok"}`. La [corrida 37225492900](https://github.com/articulacionTics/docker_SENA/actions/runs/37225492900) construyó y publicó `sha-f5d72ca` y luego, en `desplegar`: verificó los secretos ✅, ejecutó `git pull` + `docker compose pull` + `up -d` por SSH, y comprobó `/health` en el servidor ✅. **Sin entrar a la VM**, la URL pública pasó a responder `{"status":"ok"}` |

El detalle del flujo, los secretos y el rollback está en `docs/despliegue-automatizado.md`.

### 9.5 Apagado

Después de la evaluación, eliminar la VM y las reglas de firewall en la consola de GCP para dejar el costo en cero. Antes de eliminarla, si se quieren conservar los datos: `docker compose --env-file .env -f deploy/docker-compose.prod.yml exec db pg_dump -U postgres appdb > respaldo.sql`.

## 10. Pruebas

Resumen de `docs/pruebas.md`: las 10 pruebas en PASS.

| Prueba | Resultado |
|---|---|
| Arranque desde cero con un comando | 3 servicios arriba en 36 s |
| `/health` vía Nginx | 200 `{"status":"ok"}`, `Server: nginx/1.30.5` |
| API → PostgreSQL | `database: connected`, PostgreSQL 18.6 |
| Red interna | `db` → 172.18.0.2 (IP privada) |
| Persistencia | La nota sobrevive a `down` + `up` |
| Aislamiento | 5432 y 8000 sin respuesta desde el host; solo 8080 |
| Usuario | `uid=1001(appuser)` |
| Consumo | ≈ 81 MiB en total (requisito: ≤ 4 GB) |
| Secretos | `.env` no versionado; sin credenciales en `app/` |

---

## 11. Propuesta de escalamiento

### 11.1 Local frente a remoto

| Aspecto | Local (laboratorio) | Remoto (servidor / producción) |
|---|---|---|
| **Rutas** | Proyecto en `/mnt/c/LProyectos/cl/contenedor` (WSL2); `docker-compose.yml` con `build: .` | Copia del repositorio en `/srv/app`; `deploy/docker-compose.prod.yml` **sin build**, con la imagen de GHCR |
| **Puertos** | Proxy en `localhost:8080`, reenviado por WSL2 a Windows | Puerto asignado (`PROXY_PORT`) y, en producción real, 80/443 detrás de TLS. API y BD siguen sin puertos |
| **Imagen** | Construida en el portátil | Construida por GitHub Actions en un runner limpio; se despliega una etiqueta inmutable (`sha-…` o `x.y.z`) |
| **Secretos** | `.env` local con contraseña de laboratorio | `.env` propio del servidor (permisos 600) o *Docker secrets*; claves SSH y datos del host en *GitHub Secrets*; contraseñas distintas por entorno |
| **Disponibilidad** | Un solo equipo; se apaga con `wsl --shutdown` | Servicio 24/7: `restart: unless-stopped`, healthchecks, monitoreo de `/health`, respaldos programados de `pgdata` y rollback a la etiqueta anterior |
| **Datos** | Datos de prueba (`down -v` permitido) | Datos reales: nunca `down -v`; respaldos y restauración probados |

### 11.2 Qué movería a la nube y por qué

1. **Base de datos → servicio gestionado** (Amazon RDS / Azure Database for PostgreSQL / Cloud SQL), versión 18. Es el componente con estado y el más costoso de operar bien: respaldos automáticos con recuperación a un punto en el tiempo, réplicas, parches y cifrado en reposo incluidos. Los contenedores de la aplicación quedan sin estado (*stateless*) y se pueden recrear o replicar libremente. Solo cambian `DB_HOST` y las credenciales.
2. **API → orquestador de contenedores** (Azure Container Apps, AWS ECS/Fargate o Cloud Run) usando la **misma imagen de GHCR**. Permite tener varias réplicas detrás de un balanceador y escalar según la demanda, además de despliegues sin corte (*rolling*) y rollback por etiqueta. Como la API no tiene estado, escalar es agregar réplicas.
3. **Proxy → balanceador gestionado / CDN con TLS** (Application Gateway, ALB, Cloudflare): certificados HTTPS automáticos, WAF y protección DDoS. Nginx puede seguir como proxy interno o eliminarse.
4. **Registry:** se mantiene GHCR, o se replica en el registry del proveedor para reducir la latencia de los `pull`.
5. **Secretos → gestor de secretos** (Azure Key Vault, AWS Secrets Manager), inyectados en tiempo de ejecución, con rotación periódica.
6. **Se mantiene:** el flujo de GitHub Actions (build → GHCR → deploy) y las etiquetas inmutables. Solo cambia el paso `desplegar`.

**Por qué en ese orden:** primero lo que concentra riesgo (los datos), luego lo que limita la capacidad (la API) y por último el perímetro (TLS y balanceo). Una alternativa intermedia de bajo costo es una sola VM en la nube con Docker Engine y el mismo `deploy/docker-compose.prod.yml`: es idéntico al servidor del curso.

### 11.3 Protección de datos personales (Ley 1581 de 2012)

Hoy la aplicación de ejemplo no almacena datos personales. Si los almacenara (por ejemplo, nombres, documentos o correos de usuarios), la infraestructura debería apoyar el cumplimiento de la Ley 1581 de 2012 y su reglamentación (Decreto 1377 de 2013, incorporado en el Decreto 1074 de 2015). *Lo siguiente son consideraciones técnicas de infraestructura, no asesoría jurídica; la responsabilidad legal corresponde al responsable del tratamiento.*

- **Finalidad y autorización:** registrar el consentimiento del titular (fecha, versión de la política y finalidad) y recolectar solo los datos necesarios (minimización).
- **Seguridad (principio de seguridad, art. 4):**
  - cifrado en tránsito (TLS en el proxy o balanceador) y en reposo (disco o servicio de BD cifrado);
  - BD sin exposición pública (ya implementado);
  - acceso con privilegio mínimo;
  - secretos fuera del código (ya implementado);
  - registros de acceso;
  - respaldos cifrados.
- **Acceso y circulación restringida:** solo los servicios y personas autorizados acceden a la BD; nada de datos personales en logs, imágenes Docker ni en el repositorio Git.
- **Derechos del titular:** la API y la BD deben permitir consultar, actualizar, rectificar y suprimir los datos de un titular (art. 8) dentro de los plazos legales.
- **Transferencia internacional:** si la nube aloja los datos fuera de Colombia, verificar que el país ofrezca un nivel adecuado de protección o que exista la autorización o contrato que corresponda, y documentar la ubicación (región) elegida.
- **Retención:** definir un plazo de conservación y su eliminación segura, también en los respaldos.
- **Incidentes:** procedimiento para detectar, contener y reportar incidentes de seguridad a la Superintendencia de Industria y Comercio (SIC). Cuando aplique, registrar las bases de datos en el Registro Nacional de Bases de Datos (RNBD).
