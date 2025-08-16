pipeline {
  agent any

  environment {
    REGISTRY = "docker.io"
    IMAGE_NAME = "saulgpro/tfb-devops"   // ya está correcto y en minúsculas
    // NO calculamos IMAGE_TAG aquí: lo haremos dentro de 'Build Image for Deploy'
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
        sh 'which docker-compose || true'
      }
    }

    stage('Build & Test') {
      steps {
        sh 'docker-compose -f docker-compose.ci.yml down --volumes --remove-orphans || true'
        sh 'docker-compose -f docker-compose.ci.yml build --no-cache'
        sh 'docker-compose -f docker-compose.ci.yml up -d db'
        sh '''
          echo "Waiting for Postgres..."
          for i in $(seq 1 30); do
            docker-compose -f docker-compose.ci.yml exec -T db pg_isready -U postgres && break || true
            sleep 1
          done
        '''
        sh 'docker-compose -f docker-compose.ci.yml run --rm -e PYTHONPATH=/app -w /app web pytest -q'
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
          // CALCULA la tag *después* del checkout para asegurar que GIT_COMMIT esté disponible
          def computedTag = env.GIT_COMMIT?.take(7) ?: env.BUILD_NUMBER ?: 'local'
          env.IMAGE_TAG = computedTag  // opcional: exportarla al env para logs/post

          // Build imagen local
          sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."

          // Login to Docker Hub usando credenciales seguras (asegúrate que el ID coincide)
          withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh "echo \$DOCKER_PASS | docker login ${REGISTRY} -u \$DOCKER_USER --password-stdin"
          }

          // Tag y push (tag por commit/BUILD y también latest)
          sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
          sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

          // También actualizar 'latest' (opcional pero útil para despliegues que usan latest)
          sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest || true"
          sh "docker push ${REGISTRY}/${IMAGE_NAME}:latest || true"

          // Logout
          sh "docker logout ${REGISTRY} || true"
        }
      }
    }
  }

  post {
    always {
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