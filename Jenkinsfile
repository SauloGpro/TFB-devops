pipeline {
    agent any

    environment {
        POSTGRES_USER = 'postgres'
        POSTGRES_PASSWORD = 'postgres'
        POSTGRES_DB = 'app_db'
        SECRET_KEY = 'changeme123'
        FLASK_ENV = 'development'
    }

    stages {
        stage('Prep / Info') {
            steps {
                script {
                    // Info debugging: verificar docker y docker-compose disponibles
                    sh 'docker --version || true'
                    sh 'docker-compose --version || true'
                    sh 'which docker-compose || true'
                }
                // crear .env en el workspace
                writeFile file: '.env', text: """
FLASK_ENV=${FLASK_ENV}
SECRET_KEY=${SECRET_KEY}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
DATABASE_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
"""
            }
        }

        stage('Build & Test') {
            steps {
                script {
                    // Usamos docker-compose (con guion) para compatibilidad con la imagen Jenkins que tiene docker-compose instalado.
                    sh 'docker-compose -f docker-compose.ci.yml down --volumes --remove-orphans || true'
                    sh 'docker-compose -f docker-compose.ci.yml build --no-cache'
                    sh 'docker-compose -f docker-compose.ci.yml up -d db'

                    // Esperar a que Postgres acepte conexiones (usa pg_isready dentro del contenedor db)
                    sh '''
                    set -e
                    echo "Waiting for Postgres to be ready..."
                    for i in $(seq 1 30); do
                      docker-compose -f docker-compose.ci.yml exec -T db pg_isready -U ${POSTGRES_USER} && { echo "Postgres ready"; break; } || true
                      sleep 1
                    done
                    '''

                    // Ejecutar tests: run crea un contenedor temporal a partir de la imagen web
                    sh 'docker-compose -f docker-compose.ci.yml run --rm web pytest -q'
                    // Build final de la imagen web si quieres
                    sh 'docker-compose -f docker-compose.ci.yml build web'
                }
            }
        }
    }

    post {
        always {
            sh 'docker-compose -f docker-compose.ci.yml down --volumes --remove-orphans || true'
        }
    }
}
