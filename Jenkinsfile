pipeline {
    agent any
    
    environment {
        // Replace with your actual Docker Hub username and repo name
        DOCKER_HUB_USER = 'chanchal2512' 
        IMAGE_NAME      = 'todo-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        
        // Render Deploy Hook URL (From your Render service settings)
        RENDER_DEPLOY_HOOK = 'https://api.render.com/deploy/srv-xxxxxxxxxxxxxxx?key=xxxxxxxxx'
    }

    stages {
        stage('1. Fetch Source Code') {
            steps {
                checkout scm
            }
        }

        stage('2. Code Quality Analysis') {
            steps {
                echo 'Running Python Static Code Analysis via Flake8...'
                sh '''
                    pip install flake8 --quiet
                    flake8 . --max-line-length=120 --exit-zero > code-quality-report.txt
                '''
                archiveArtifacts artifacts: 'code-quality-report.txt', allowEmptyArchive: true
            }
        }

        stage('3. Vulnerability Scanning') {
            steps {
                echo 'Scanning dependencies for vulnerabilities with Trivy...'
                sh 'docker run --rm -v $(pwd):/apps aquasec/trivy fs /apps > trivy-report.txt'
                archiveArtifacts artifacts: 'trivy-report.txt', allowEmptyArchive: true
            }
        }

        stage('4. Build Docker Image') {
            steps {
                echo 'Building Docker Image...'
                script {
                    appImage = docker.build("${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}")
                    sh "docker tag ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('5. Push to Docker Hub') {
            steps {
                echo 'Pushing Image to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh "echo \$PASS | docker login -u \$USER --password-stdin"
                    sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('6. Deploy to Render') {
            steps {
                echo 'Triggering Deployment on Render...'
                sh "curl -X POST '${RENDER_DEPLOY_HOOK}'"
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution finished.'
            cleanWs()
        }
    }
}