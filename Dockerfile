# Dockerfile
FROM python:3.12-slim

# Variables de entorno para evitar warnings y buffers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos dependencias del sistema necesarias para psycopg2, etc.
RUN apt-get update && apt-get install -y build-essential libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements (si ya lo tienes en el repo)
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos el código
COPY . /app

# Puerto que usa Flask por defecto en tu run.py
EXPOSE 5000

# Comando por defecto (development). Si quieres usar gunicorn en prod:
# ENTRYPOINT ["gunicorn", "run:app", "-w", "4", "-b", "0.0.0.0:5000"]
CMD ["python", "run.py"]
