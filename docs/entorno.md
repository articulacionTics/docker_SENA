# AA2 — Entorno de trabajo

Fecha de verificación: 2026-10-03. Todos los valores provienen de comandos ejecutados en el equipo de trabajo.

## 1. Resumen

| Elemento | Valor | Comando |
|---|---|---|
| Sistema anfitrión | Windows 11 Pro 10.0.26200 | — |
| WSL | 2.7.14.0 (kernel 6.18.33.2-2, WSLg 1.0.73.2) | `wsl --version` (PowerShell) |
| Distribución usada | **Ubuntu 24.04.1 LTS (noble)**, WSL versión 2, nombre `Ubuntu` | `wsl -l -v`, `lsb_release -a` |
| Kernel | 6.18.33.2-microsoft-standard-WSL2 | `uname -r` |
| Arquitectura | x86_64 | `uname -a`, `docker info` |
| Init | systemd (`/etc/wsl.conf` → `[boot] systemd=true`) | `ps -p 1 -o comm=` |
| Docker Engine | 28.0.1 (Docker CE, paquete `docker-ce` del repositorio oficial de Docker) | `docker --version` |
| Docker Compose | v2.33.1 (plugin `docker-compose-plugin`) | `docker compose version` |
| Buildx | v0.21.1 | `docker buildx version` |
| Recursos | 16 CPU · 19.34 GiB RAM · 931 GB libres en `/` | `docker info`, `df -h ~` |
| Cgroups | v2, driver systemd | `docker info` |
| Contexto Docker | `default` → `unix:///var/run/docker.sock` (Engine local, **no** Docker Desktop) | `docker context ls` |
| Ruta del proyecto | `/home/liya/docker-multiservice-lab` (sistema de archivos Linux, no `/mnt/c`) | `pwd` |
| Git | 2.43.0 | `git --version` |

## 2. Salidas de verificación

```text
$ docker --version
Docker version 28.0.1, build 068a01e

$ docker compose version
Docker Compose version v2.33.1

$ docker run --rm hello-world
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

`docker info` (sección *Server*, recortada):

```text
Server:
 Containers: 5
  Running: 0
  Paused: 0
  Stopped: 5
 Images: 50
 Server Version: 28.0.1
 Storage Driver: overlay2
  Backing Filesystem: extfs
 Logging Driver: json-file
 Cgroup Driver: systemd
 Cgroup Version: 2
 Plugins:
  Volume: local
  Network: bridge host ipvlan macvlan null overlay
 Swarm: inactive
 Default Runtime: runc
 runc version: v1.2.4-0-g6c52b3f
 Security Options:
  seccomp
   Profile: builtin
  cgroupns
 Kernel Version: 6.18.33.2-microsoft-standard-WSL2
 Operating System: Ubuntu 24.04.1 LTS
 OSType: linux
 Architecture: x86_64
 CPUs: 16
 Total Memory: 19.34GiB
 Docker Root Dir: /var/lib/docker
```

`Operating System: Ubuntu 24.04.1 LTS` confirma que el daemon es Docker Engine dentro de Ubuntu. Con Docker Desktop se mostraría `Docker Desktop`.

## 3. Instalación utilizada

Docker Engine se instaló dentro de Ubuntu desde el repositorio oficial `download.docker.com`. Paquetes presentes (`dpkg -l | grep docker`):

```text
docker-ce 5:28.0.1-1~ubuntu.24.04~noble
docker-ce-cli 5:28.0.1-1~ubuntu.24.04~noble
docker-buildx-plugin 0.21.1-1~ubuntu.24.04~noble
docker-compose-plugin 2.33.1-1~ubuntu.24.04~noble
containerd.io 1.7.25-1
```

El usuario `liya` pertenece al grupo `docker`, así que no necesita `sudo`. El servicio está gestionado por systemd (`systemctl is-active docker` → `active`).

Procedimiento de referencia para una instalación limpia en Ubuntu (documentación oficial de Docker):

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER   # cerrar y reabrir la sesión
```

## 4. Problemas encontrados y soluciones

| # | Problema | Causa | Impacto | Solución aplicada |
|---|---|---|---|---|
| 1 | La distribución WSL por defecto (`Ubuntu-20.04`) no tiene `docker compose` (`'compose' is not a docker command`). | Solo tiene `docker.io` 26.1.3 de los repositorios de Ubuntu, sin el plugin Compose v2. | No permite ejecutar el proyecto. | Se usa la distribución `Ubuntu` (24.04) de forma explícita: `wsl -d Ubuntu`. |
| 2 | Docker Desktop está instalado en Windows (distro `docker-desktop`, `docker.exe` en el PATH de Windows). | Instalación previa. | Riesgo de usar el daemon equivocado. | Docker Desktop permanece **detenido**. Dentro de Ubuntu, `which docker` → `/usr/bin/docker` (va antes que `/mnt/c/...`) y el contexto es `default` → `unix:///var/run/docker.sock`. |
| 3 | `docker info` muestra advertencias `Plugin "/usr/local/lib/docker/cli-plugins/docker-*" is not valid`. | Enlaces simbólicos rotos que dejó la integración WSL de Docker Desktop. | Solo son advertencias. Compose y Buildx funcionan desde los paquetes `docker-*-plugin`. | Se documentan. Corrección opcional: `sudo rm /usr/local/lib/docker/cli-plugins/docker-*` (verificar antes con `ls -l` que sean enlaces rotos). |
| 4 | Junto a `docker-ce` siguen instalados `docker.io` 26.1.3 y `docker-compose` 1.29.2 (Compose v1). | Instalaciones anteriores desde los repositorios de Ubuntu. | El binario activo es `docker-ce` 28.0.1. Ejecutar `docker-compose` (con guion) llamaría a la versión v1, que es obsoleta. | Se usa siempre `docker compose` (v2, con espacio). |
| 5 | En `postgres:18-alpine` el montaje `-v vol:/var/lib/postgresql/data` hace que el contenedor termine con `Exited (1)`. | Desde PostgreSQL 18, la imagen oficial usa `PGDATA=/var/lib/postgresql/18/docker` y declara `VOLUME /var/lib/postgresql`. | El montaje clásico de versiones ≤17 no funciona. | Se verificaron alternativas (ver `docs/imagenes.md` §4). |
