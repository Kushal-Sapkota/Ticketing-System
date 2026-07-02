pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = 'dockerhub-credentials'
        BACKEND_IMAGE = "kushal81/ticketing-backend"
        FRONTEND_IMAGE = "kushal81/ticketing-frontend"
        IMAGE_TAG = "v${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Backend') {
            steps {
                sh "docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} ./backend"
            }
        }

        stage('Build Frontend') {
            steps {
                sh "docker build --build-arg VITE_API_URL=http://localhost:8000/api/v1 -t ${FRONTEND_IMAGE}:${IMAGE_TAG} ./frontend"
            }
        }

        stage('Push Images') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_HUB_CREDENTIALS}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
                        docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                        docker tag ${BACKEND_IMAGE}:${IMAGE_TAG} ${BACKEND_IMAGE}:latest
                        docker tag ${FRONTEND_IMAGE}:${IMAGE_TAG} ${FRONTEND_IMAGE}:latest
                        docker push ${BACKEND_IMAGE}:latest
                        docker push ${FRONTEND_IMAGE}:latest
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                sh """
                    docker compose down || true
                    IMAGE_TAG=${IMAGE_TAG} docker compose up -d
                """
            }
        }
    }

    post {
        success {
            echo "Build ${IMAGE_TAG} deployed successfully"
        }
        failure {
            echo "Build ${IMAGE_TAG} failed"
        }
        always {
            sh "docker logout || true"
        }
    }
}
