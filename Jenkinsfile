pipeline {
  agent any

  environment {
    // Cambia si quieres. Defaults útiles.
    REGISTRY = "docker.io"
    IMAGE_NAME = "saulgpro/tfb-devops"   // <- CAMBIA a tu usuario/repo si hace falta
    IMAGE_TAG = "${env.GIT_COMMIT?.take(7) ?: env.BUILD_NUMBER ?: 'local'}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Prep / Info') {
      steps {
        sh 'docker --version || true'
        sh 'docker-compose --version || true'
      }
    }

    stage('Build & Test') {
      steps {
        // Usa el docker-compose para CI que ya tienes
        sh 'docker-compose -f docker-compose.ci.yml down --volumes --remove-orphans || true'
        sh 'docker-compose -f docker-compose.ci.yml build --no-cache'
        sh 'docker-compose -f docker-compose.ci.yml up -d db'
        // wait & check
        sh '''
          echo "Waiting for Postgres..."
          for i in $(seq 1 30); do
            docker-compose -f docker-compose.ci.yml exec -T db pg_isready -U postgres && break || true
            sleep 1
          done
        '''
        // Run tests inside web container
        sh 'docker-compose -f docker-compose.ci.yml run --rm web pytest -q'
      }
      post {
        always {
          sh 'docker-compose -f docker-compose.ci.yml down --volumes --remove-orphans || true'
        }
      }
    }

    stage('Build Image for Deploy') {
      steps {
        script {
          // Build imagen local
          sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."

          // Login to Docker Hub using credenciales en Jenkins
          withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh "echo \$DOCKER_PASS | docker login ${REGISTRY} -u \$DOCKER_USER --password-stdin"
          }

          // Tag y push
          sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
          sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        }
      }
    }
  }

  post {
    always {
      // limpieza básica
      sh 'docker-compose -f docker-compose.ci.yml down --volumes --remove-orphans || true'
    }
    success {
      echo "Pipeline finished OK. Image pushed: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    }
    failure {
      echo "Pipeline FAILED"
    }
  }
}
