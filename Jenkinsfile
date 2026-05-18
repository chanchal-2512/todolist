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
                // Using 'bat' instead of 'sh' for Windows environments
                bat '''
                    pip install flake8 --quiet
                    flake8 . --max-line-length=120 --exit-zero > code-quality-report.txt
                '''
                archiveArtifacts artifacts: 'code-quality-report.txt', allowEmptyArchive: true
            }
        }

        stage('3. Vulnerability Scanning') {
            steps {
                echo 'Scanning dependencies for vulnerabilities with Trivy...'
                // Using Windows style paths for Docker volume mounting
                bat 'docker run --rm -v "%cd%:/apps" aquasec/trivy fs /apps > trivy-report.txt'
                archiveArtifacts artifacts: 'trivy-report.txt', allowEmptyArchive: true
            }
        }

        stage('4. Build Docker Image') {
            steps {
                echo 'Building Docker Image...'
                script {
                    appImage = docker.build("${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}")
                    bat "docker tag ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('5. Push to Docker Hub') {
            steps {
                echo 'Pushing Image to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    // Moving the pipe directly against the variable prevents trailing space injection
                    bat "echo %PASS%| docker login -u %USER% --password-stdin"
                    bat "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
                    bat "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('6. Deploy to Render') {
            steps {
                echo 'Triggering Deployment on Render...'
                // Bypasses the Windows-specific certificate revocation check quirk
                bat "curl --ssl-no-revoke -X POST \"${RENDER_DEPLOY_HOOK}\""
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