# jenkins.Dockerfile
FROM jenkins/jenkins:lts

# Switch to root to install packages
USER root

# Instalar utilidades, docker cli y docker-compose
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates curl gnupg2 lsb-release iptables git docker.io \
    && rm -rf /var/lib/apt/lists/*

# Instalar docker-compose (v2.x como binario)
# Ajusta la versión si quieres otra
ARG DOCKER_COMPOSE_VERSION=2.20.2
RUN curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Asegurarnos de que jenkins pueda usar docker: dejamos en root por simplicidad local
# (en producción usar método de grupo docker y usuarios dedicados)
USER jenkins

# Exponer puerto (no es estrictamente necesario aquí)
EXPOSE 8080 50000
