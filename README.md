TFB — Entorno local y Pipeline CI (Jenkins)

Resumen corto: este repo implementa dos bloques del TFB:

Entorno local de desarrollo: app Flask + Postgres con docker compose, tests con pytest, cobertura, y linter.

Pipeline de CI: Jenkinsfile que ejecuta tests en CI, construye la imagen Docker y la sube a Docker Hub.

Índice

Estado actual

Estructura recomendada del repositorio

Archivos importantes (qué hacen)

Configuración obligatoria (no subir secretos)

Instrucciones paso a paso — entorno local

Instrucciones paso a paso — CI (reproducir Jenkins localmente)

Tests, coverage y flake8 (cómo ejecutar y qué hacer con errores)

Cómo ejecutar la pipeline manualmente desde PowerShell

Recomendaciones de entrega y checklist

Cambios / archivos que sugiero añadir

1 — Estado actual

Funcionalidad: App Flask con endpoints CRUD simples (/data), persistencia con SQLAlchemy.

Docker: Dockerfile y docker-compose.yml para desarrollo y docker-compose.ci.yml para CI.

Tests: tests/test_app.py (2 tests) que se ejecutan y pasan.

Cobertura: > 80% con coverage en tus ejecuciones locales.

CI: Jenkinsfile construido y probado (build, tests, push a Docker Hub).

Linter: flake8 configurado en requirements.txt, genera algunas advertencias que puedes resolver o ignorar por tests.

2 — Estructura recomendada (cómo debería verse el repo)
.
├─ README.md
├─ Dockerfile
├─ docker-compose.yml
├─ docker-compose.ci.yml
├─ jenkins.Dockerfile
├─ Jenkinsfile
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ .flake8
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ models.py
│  └─ routes.py
├─ tests/
│  ├─ __init__.py
│  ├─ conftest.py       # opcional (recomendado para evitar E402)
│  └─ test_app.py
└─ docs/
   ├─ architecture.md
   └─ deployment.md


Nota: en tu estructura actual ya están los archivos principales, abajo indico qué conviene añadir/corregir.

3 — Archivos importantes (qué hacen)

Dockerfile — imagen de la app para producción / CI.

docker-compose.yml — entorno development (mapea código, hot reload, incluye jenkins con profile: local).

docker-compose.ci.yml — entorno CI (no monta volúmenes, usa DB en contenedor para tests).

Jenkinsfile — pipeline declarativa (checkout → tests → build image → push).

jenkins.Dockerfile — imagen para correr Jenkins localmente con docker/docker-compose instalado.

app/ — código de la aplicación Flask.

tests/ — tests con pytest.

.env.example — variables de entorno de ejemplo (no subir .env).

.flake8 — configuración de flake8 (sugerida).

4 — Configuración obligatoria (seguridad)

NO subir .env ni claves ni *.pem.

Añade .env a .gitignore.

Usa Jenkins Credentials para Docker Hub (dockerhub-creds) y GitHub PAT (si lo necesitas).

README.md no debe contener contraseñas.

Ejemplo .env.example:

FLASK_ENV=development
SECRET_KEY=changeme123
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app_db
DATABASE_URI=postgresql://postgres:postgres@db:5432/app_db

5 — Instrucciones paso a paso — entorno local
Requisitos

Docker y Docker Compose v2 instalados.

(Opcional) Python 3.10+ si quieres ejecutar tests sin contenedores.

A. Preparar .env

Copia .env.example → .env

Ajusta valores si quieres (no subir .env).

cp .env.example .env
# editar .env con tus valores

B. Arrancar en modo dev (con live-reload)
# Con docker compose v2
docker compose --profile local up --build
# o si no quieres jenkins
docker compose up --build


La app estará en http://localhost:5000.

C. Parar / limpiar
docker compose down --volumes

6 — Instrucciones paso a paso — CI (reproducir lo que hace Jenkins)
Comandos (Linux / macOS)
# 1. limpiar antiguos recursos
docker compose -f docker-compose.ci.yml down --volumes --remove-orphans

# 2. construir imagen para CI
docker compose -f docker-compose.ci.yml build --no-cache

# 3. levantar DB (detached)
docker compose -f docker-compose.ci.yml up -d db

# 4. esperar a que postgres acepte conexiones (replicando el loop del Jenkinsfile)
# (en shell bash)
for i in $(seq 1 30); do
  docker compose -f docker-compose.ci.yml exec -T db pg_isready -U postgres && break || true
  sleep 1
done

# 5. ejecutar tests dentro del servicio 'web' (igual que Jenkins)
docker compose -f docker-compose.ci.yml run --rm -e PYTHONPATH=/app -w /app web pytest -q

# 6. limpiar
docker compose -f docker-compose.ci.yml down --volumes --remove-orphans

Equivalente PowerShell (Windows)
docker compose -f docker-compose.ci.yml down --volumes --remove-orphans
docker compose -f docker-compose.ci.yml build --no-cache
docker compose -f docker-compose.ci.yml up -d db

for ($i=0; $i -lt 30; $i++) {
  $out = docker compose -f docker-compose.ci.yml exec -T db pg_isready -U postgres 2>$null
  if ($out -match "accepting connections") { Write-Output "Postgres listo"; break }
  Start-Sleep -Seconds 1
}

docker compose -f docker-compose.ci.yml run --rm -e PYTHONPATH=/app -w /app web pytest -q
docker compose -f docker-compose.ci.yml down --volumes --remove-orphans

Build & push (igual que el Jenkinsfile)
# tag por commit corto (ejemplo)
IMAGE_NAME="saulgpro/tfb-devops"
IMAGE_TAG=$(git rev-parse --short HEAD)

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
docker login docker.io     # te pedirá usuario/contraseña
docker tag ${IMAGE_NAME}:${IMAGE_TAG} docker.io/${IMAGE_NAME}:${IMAGE_TAG}
docker push docker.io/${IMAGE_NAME}:${IMAGE_TAG}

# actualizar latest
docker tag ${IMAGE_NAME}:${IMAGE_TAG} docker.io/${IMAGE_NAME}:latest
docker push docker.io/${IMAGE_NAME}:latest
docker logout

7 — Tests, coverage y flake8
Ejecutar tests (local, venv)
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install --upgrade pip setuptools wheel 
pip install -e .
pytest -q

Coverage
coverage run --source=app -m pytest
coverage report -m


Objetivo: >= 80%.

flake8
flake8 app tests

8 — Ejecutar la pipeline desde PowerShell (script resumido)

Guarda esto como ci-local.ps1 si quieres reproducir todo con un comando:

# ci-local.ps1 (ejecutar desde la raíz del repo)
docker compose -f docker-compose.ci.yml down --volumes --remove-orphans
docker compose -f docker-compose.ci.yml build --no-cache
docker compose -f docker-compose.ci.yml up -d db

for ($i=0; $i -lt 30; $i++) {
  $out = docker compose -f docker-compose.ci.yml exec -T db pg_isready -U postgres 2>$null
  if ($out -match "accepting connections") { Write-Output "Postgres listo"; break }
  Start-Sleep -Seconds 1
}

docker compose -f docker-compose.ci.yml run --rm -e PYTHONPATH=/app -w /app web pytest -q
docker compose -f docker-compose.ci.yml down --volumes --remove-orphans

# build y push (descomentar solo si quieres subir a Docker Hub)
# $IMAGE="saulgpro/tfb-devops"
# $TAG = git rev-parse --short HEAD
# docker build -t $IMAGE:$TAG .
# docker login
# docker tag $IMAGE:$TAG docker.io/$IMAGE:$TAG
# docker push docker.io/$IMAGE:$TAG
# docker tag $IMAGE:$TAG docker.io/$IMAGE:latest
# docker push docker.io/$IMAGE:latest