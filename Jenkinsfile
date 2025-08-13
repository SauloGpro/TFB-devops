pipeline {
    agent any

    stages {
        stage('Build & Test') {
            steps {
                sh 'docker-compose down --volumes --remove-orphans'
                sh 'docker-compose build'
                sh 'docker-compose up -d db'
                sh 'sleep 10' // Esperar a que DB esté lista
                sh 'docker-compose up -d web'
                sh 'sleep 5' // Esperar a que web esté arriba
                sh 'docker-compose exec -T web pytest -q'
            }
        }

        stage('Build Image for Deploy') {
            steps {
                sh 'docker build -t tfb-app:latest .'
            }
        }
    }

    post {
        always {
            sh 'docker-compose down --volumes --remove-orphans'
        }
    }
}
