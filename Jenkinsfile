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
        stage('Build & Test') {
            steps {
                script {
                    // Crear .env en el workspace
                    writeFile file: '.env', text: """
FLASK_ENV=${FLASK_ENV}
SECRET_KEY=${SECRET_KEY}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
DATABASE_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
"""
                }

                // Usar docker compose específico para CI (sin puertos host)
                sh 'docker compose -f docker-compose.ci.yml down --volumes --remove-orphans || true'
                sh 'docker compose -f docker-compose.ci.yml build --no-cache'
                // Levantar solo la DB en background (sin mapear puertos)
                sh 'docker compose -f docker-compose.ci.yml up -d db'
                // Ejecutar tests en un contenedor efímero usando la imagen web (depende de db)
                sh 'docker compose -f docker-compose.ci.yml run --rm web pytest -q'

                // Opcional: construir una imagen final si los tests pasan
                sh 'docker compose -f docker-compose.ci.yml build web'
            }
        }

        stage('Build Image for Deploy') {
            steps {
                // Puedes añadir build/push aquí si quieres
                echo "Build Image stage (opcional)"
            }
        }
    }

    post {
        always {
            sh 'docker compose -f docker-compose.ci.yml down --volumes --remove-orphans || true'
        }
    }
}
