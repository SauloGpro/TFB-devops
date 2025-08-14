pipeline {
    agent any

    environment {
        // Aquí podrías usar credenciales de Jenkins si quieres más seguridad
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
                    // Crear .env
                    writeFile file: '.env', text: """
FLASK_ENV=${FLASK_ENV}
SECRET_KEY=${SECRET_KEY}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
DATABASE_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
"""
                }
                sh 'docker-compose down --volumes --remove-orphans'
                sh 'docker-compose up --build -d'
                sh 'docker exec tfb-web-1 pytest -q'
            }
        }

        stage('Build Image for Deploy') {
            steps {
                sh 'docker build -t tfb-app .'
            }
        }
    }

    post {
        always {
            sh 'docker-compose down --volumes --remove-orphans || true'
        }
    }
}
