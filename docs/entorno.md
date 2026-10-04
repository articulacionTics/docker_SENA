# AA2 — Entorno de trabajo

Equipo de **un integrante**: Lily Pardo (ficha 3602390). Los valores de este documento salen de comandos ejecutados en el equipo de trabajo. Última verificación: 2026-10-03.

**Ruta de instalación elegida: 2B — Windows 11 + WSL2 + Ubuntu + Docker Engine** (no Docker Desktop).

## 1. Diagnóstico del equipo (actividad 3.2b)

Ejecutado en PowerShell:

| Dato | Valor | Comando |
|---|---|---|
| Sistema operativo | Microsoft Windows 11 Pro, versión 10.0.26200 (build 26200), 64 bits | `winver` / `Get-CimInstance Win32_OperatingSystem` |
| Memoria física total | 40 567 MB | `systeminfo \| findstr /C:"Memoria fisica total"` |
| Virtualización | Hipervisor detectado; seguridad basada en virtualización en ejecución | `systeminfo \| findstr /C:"Hyper-V"` |
| Disco C: | 393.6 GB usados · 82.3 GB libres | `Get-PSDrive C` |
| WSL | 2.7.14.0 (kernel 6.18.33.2-2, WSLg 1.0.73.2) | `wsl --version` |

Cumple los mínimos de la guía: 4 GB de RAM, 15 GB libres y virtualización habilitada.

## 2. Resumen del entorno

| Elemento | Valor | Comando |
|---|---|---|
| Distribución usada | **Ubuntu 24.04.1 LTS (noble)** en WSL **versión 2**, nombre `Ubuntu` | `wsl -l -v`, `lsb_release -a` |
| Kernel | 6.18.33.2-microsoft-standard-WSL2, x86_64 | `uname -a` |
| systemd | Activo (`/etc/wsl.conf` → `[boot] systemd=true`) | `ps -p 1 -o comm=` |
| Docker Engine | **29.8.2** (Docker CE, repositorio oficial `download.docker.com`) | `docker --version` |
| Docker Compose | **v5.6.0** (plugin `docker-compose-plugin`, subcomando `docker compose`) | `docker compose version` |
| Buildx / BuildKit | v0.37.1 | `docker buildx version` |
| containerd | 2.3.6 | `dpkg -l containerd.io` |
| Almacén de imágenes | containerd snapshotter (`overlayfs`), el valor por defecto de Engine 29 en una instalación limpia | `docker info` |
| Cgroups | v2, driver systemd | `docker info` |
| Contexto Docker | `default *` → `unix:///var/run/docker.sock` | `docker context ls` |
| Ruta del proyecto | `/mnt/c/LProyectos/cl/contenedor` (ver la decisión D1, §5) | `pwd` |
| Git | 2.43.0 | `git --version` |

> La guía se refiere a «Compose v2» porque es la generación de Compose que funciona como plugin (`docker compose`, con espacio) y reemplazó al antiguo `docker-compose` v1. El plugin oficial continuó su numeración y hoy reporta v5.6.0; el subcomando y el formato del archivo son los mismos.

## 3. Salidas de verificación (guía AA2, paso 3)

```text
$ docker --version
Docker version 29.8.2, build 7fc2dff

$ docker compose version
Docker Compose version v5.6.0

$ docker info | head -20
Client: Docker Engine - Community
 Version:    29.8.2
 Context:    default
 Debug Mode: false
 Plugins:
  buildx: Docker Buildx (Docker Inc.)
    Version:  v0.37.1
    Path:     /usr/libexec/docker/cli-plugins/docker-buildx
  compose: Docker Compose (Docker Inc.)
    Version:  v5.6.0
    Path:     /usr/libexec/docker/cli-plugins/docker-compose

Server:
 Containers: 0
  Running: 0
  Paused: 0
  Stopped: 0
 Images: 4
 Server Version: 29.8.2
 Storage Driver: overlayfs
  driver-type: io.containerd.snapshotter.v1
 Logging Driver: json-file
 Cgroup Driver: systemd
 Cgroup Version: 2

$ docker info --format '{{.OperatingSystem}}'
Ubuntu 24.04.1 LTS          ← el daemon es Docker Engine dentro de Ubuntu (no "Docker Desktop")

$ docker context ls
NAME        DESCRIPTION                               DOCKER ENDPOINT               ERROR
default *   Current DOCKER_HOST based configuration   unix:///var/run/docker.sock

$ docker run --rm hello-world
Hello from Docker!
```

## 4. Instalación realizada (apartados 2B + 2A de la guía)

1. **WSL2:** `wsl --version` → 2.7.14.0, con la distribución `Ubuntu` en VERSION 2 y systemd habilitado en `/etc/wsl.conf`.
2. **Docker Engine dentro de Ubuntu** desde el repositorio oficial (`/etc/apt/sources.list.d/docker.list`). La actualización a la serie 29 se hizo con:

```bash
sudo apt remove -y docker-compose docker-compose-v2 docker-doc podman-docker   # paquetes no oficiales
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
sudo systemctl enable --now docker
sudo usermod -aG docker $USER      # el usuario liya ya pertenecía al grupo docker
```

3. **Herramientas dentro de Ubuntu:** Git 2.43.0, con el remoto por SSH (`git@github-articulacion:articulacionTics/docker_SENA.git`).

Paquetes Docker instalados tras la actualización (`dpkg -l | grep -E 'docker|containerd'`):

```text
containerd.io              2.3.6-1~ubuntu.24.04~noble
docker-buildx-plugin       0.37.1-1~ubuntu.24.04~noble
docker-ce                  5:29.8.2-1~ubuntu.24.04~noble
docker-ce-cli              5:29.8.2-1~ubuntu.24.04~noble
docker-ce-rootless-extras  5:29.8.2-1~ubuntu.24.04~noble
docker-compose-plugin      5.6.0-1~ubuntu.24.04~noble
```

Control del motor en este entorno: arranca solo al abrir Ubuntu (systemd) y se detiene con `wsl --shutdown` desde PowerShell.

## 5. Problemas encontrados, decisiones y soluciones

| # | Problema | Causa | Impacto | Solución aplicada |
|---|---|---|---|---|
| P1 | La distribución por defecto (`Ubuntu-20.04`) no tiene `docker compose`. | Solo tiene `docker.io` 26.1 de Ubuntu, sin el plugin. | No permite ejecutar el proyecto. | Se usa la distribución `Ubuntu` (24.04) de forma explícita: `wsl -d Ubuntu`. |
| P2 | Docker Engine **28.0.1** instalado. | Instalación anterior. | La guía exige la serie 29: la 28 quedó sin soporte en mayo de 2026. | Actualizado a **29.8.2** desde el repositorio oficial (§4). |
| P3 | Paquetes no oficiales junto a Docker CE: `docker-compose` 1.29 (v1) y restos de `docker.io`. | Instalaciones antiguas desde los repositorios de Ubuntu. | Riesgo de usar Compose v1 (`docker-compose`). | Retirados (paso 1 del apartado 2A). |
| P4 | Docker Desktop instalado en Windows. Su integración WSL dejó enlaces rotos en `/usr/local/lib/docker/cli-plugins/` (→ `/mnt/wsl/docker-desktop/...`). | Instalación previa de Docker Desktop. | `docker build` usaba el **builder antiguo** (obsoleto) porque el enlace roto `docker-buildx` ocultaba el plugin válido, y `docker info` mostraba 11 advertencias. | Enlaces rotos eliminados (`sudo find /usr/local/lib/docker/cli-plugins -xtype l -delete`) e integración WSL de Desktop desactivada. Verificado: BuildKit activo y 0 advertencias. **Docker Desktop no debe estar abierto** mientras se trabaja: si arranca, publica sus propios contenedores en los puertos del host (P8). |
| P5 | Los contenedores no resolvían nombres DNS (`Temporary failure in name resolution`) y `pip install` fallaba dentro de `docker build`. | WSL2 con túnel DNS: Ubuntu usa `nameserver 10.255.255.254`, accesible solo desde el propio WSL, y los contenedores heredan ese valor. | No se podía construir la imagen de la API. | `/etc/docker/daemon.json` → `{ "dns": ["8.8.8.8", "1.1.1.1"] }` + `sudo systemctl restart docker`. Verificado: HTTPS 200 a pypi.org desde un contenedor. |
| P6 | En las redes definidas por el usuario (la red `interna` de Compose) el **TCP entre contenedores** fallaba: `/health` por el proxy devolvía `504 Gateway Time-out` y la API registraba `connection timeout expired` contra `db`. El ping (ICMP) sí funcionaba, y tampoco había salida a Internet. | **UFW activo en otra distribución (`Ubuntu-20.04`)** con `DEFAULT_FORWARD_POLICY="DROP"`. En WSL2 todas las distribuciones comparten la pila de red del kernel, así que al arrancar esa distro sus reglas (iptables-legacy, cadena `FORWARD` con política DROP) bloquean el tráfico reenviado del Docker de Ubuntu 24.04. Evidencia: el kernel registró `[UFW BLOCK] IN=br-7733d3b1c6cc ... SRC=172.19.0.3 DST=172.19.0.4 PROTO=TCP DPT=5432 SYN`, y `iptables-legacy -S` mostraba `-P FORWARD DROP` con las cadenas `ufw-*`. | Crítico: la solución no funcionaba (`api` no llegaba a `db` ni `proxy` a `api`). | En Ubuntu-20.04: `sudo ufw default allow routed` (UFW sigue protegiendo lo entrante y permite solo el tráfico reenviado). En PowerShell: `wsl --set-default Ubuntu` y `wsl --shutdown`. Verificado: `FORWARD ACCEPT`, HTTP entre contenedores OK, salida a Internet OK, `/health` 200 por Nginx, `/api/status` → `database: connected`. |
| P7 | Al ejecutar `sudo apt purge docker.io` el script de purga del paquete **borró `/var/lib/docker`** (`Nuking /var/lib/docker ...`): se perdieron las imágenes, los contenedores y los volúmenes de **otros proyectos de prueba** de esta distribución. | La guía indica `apt remove`, que conserva los datos; se usó `purge`, que ejecuta el `postrm` de `docker.io`. | Datos de prueba de otros proyectos (sin valor según la usuaria). Este proyecto no se afectó: su código está en Git. Engine 29 arrancó sobre un directorio vacío y por eso usa el almacén containerd. | **Lección:** para retirar `docker.io` usar `apt remove`, nunca `purge`, si hay datos en `/var/lib/docker`. Respaldar antes los volúmenes (`docker run --rm -v vol:/d -v $PWD:/b alpine tar czf /b/vol.tgz -C /d .`). |
| P8 | `failed to bind host port 0.0.0.0:8080 / 5432: address already in use`. | Docker Desktop se abrió y levantó contenedores de otro proyecto publicados en 8080 y 5432. Todas las distribuciones WSL2 y Windows comparten `localhost`. | Impide levantar el proxy (8080). | Docker Desktop cerrado. Comprobación: `Get-NetTCPConnection -State Listen -LocalPort 8080` no debe mostrar `com.docker.backend`. |
| P9 | La distribución WSL por defecto era `Ubuntu-20.04`, así que cualquier `wsl` sin `-d` la arrancaba, junto con su UFW (P6). | Configuración previa del equipo. | Riesgo de trabajar en la distro equivocada y de reactivar el bloqueo de P6. | `wsl --set-default Ubuntu`. Verificado: `wsl -l -v` marca `* Ubuntu`. |
| D1 | **Decisión:** el proyecto está en `/mnt/c/LProyectos/cl/contenedor` y no en `/home/<usuario>`. | Preferencia de la usuaria: tener los archivos en una carpeta de Windows. | La guía (p. 12, Anexo B) desaconseja `/mnt/c`: la E/S es más lenta, `/mnt/c` se monta sin `metadata` (todos los archivos aparecen con permisos 777) y hay riesgo de CRLF si se edita con herramientas de Windows. | Mitigaciones: `.gitattributes` (`* text=auto eol=lf`), `git config core.fileMode false`, edición con VS Code y comprobación `grep -rlI $'\r'` antes de cada commit. Verificado: el build (19 s) y el montaje `:ro` de `nginx/default.conf` funcionan desde `/mnt/c`. |

## 6. Otros sistemas operativos (referencia)

Este equipo tiene un solo integrante (Windows + WSL2). Para Ubuntu nativo (apartado 2A) y macOS con Colima (2C), el procedimiento de la guía queda resumido en el [README](../README.md#instalación-del-motor) y produce **el mismo Docker Engine y los mismos comandos**. Por eso el proyecto se comporta igual en los tres (requisitos RI-OS-01 a RI-OS-03 en `docs/requisitos.md`).
