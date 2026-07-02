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
        withCredentials([
            string(credentialsId: 'ticketing-jwt-secret', variable: 'JWT_SECRET_KEY'),
            string(credentialsId: 'ticketing-db-password', variable: 'POSTGRES_PASSWORD')
        ]) {
            sh """
                cat > .env << EOF
POSTGRES_DB=helpdesk
POSTGRES_USER=helpdesk
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
DATABASE_URL=postgresql+psycopg://helpdesk:${POSTGRES_PASSWORD}@db:5432/helpdesk
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
DEFAULT_ADMIN_EMAIL=admin@company.local
DEFAULT_ADMIN_PASSWORD=ChangeMe123!
DEFAULT_ADMIN_NAME=Default Admin
VITE_API_URL=http://localhost:8000/api/v1
EOF
                docker compose down || true
                IMAGE_TAG=${IMAGE_TAG} docker compose up -d
            """
        }
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
