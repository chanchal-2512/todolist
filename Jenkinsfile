pipeline {
    agent any
    
    environment {
        // Replace with your actual Docker Hub username and repo name
        DOCKER_HUB_USER = 'chanchal2512' 
        IMAGE_NAME      = 'todo-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        
        // Render Deploy Hook URL (We will get this in Step 4)
        RENDER_DEPLOY_HOOK = 'https://api.render.com/deploy/srv-xxxxxxxxxxxxxxx?key=xxxxxxxxx'
    }

    stages {
        stage('1. Fetch Source Code') {
            steps {
                // Fetches code from the repository that triggered the build
                checkout scm
            }
        }

        stage('2. Code Quality Analysis') {
            steps {
                echo 'Running Python Static Code Analysis...'
                // Install a linting tool and run it over your Python files, saving results to a log
                sh '''
                    pip install flake8 --quiet
                    flake8 . --max-line-length=120 --exit-zero > code-quality-report.txt
                '''
                // Archive the generated report as a lab deliverable artifact
                archiveArtifacts artifacts: 'code-quality-report.txt', allowEmptyArchive: true
            }
        }

        stage('3. Vulnerability Scanning') {
            steps {
                echo 'Scanning dependencies for vulnerabilities with Trivy...'
                // This runs a filesystem scan using Trivy via Docker
                sh 'docker run --rm -v $(pwd):/apps aquasec/trivy fs /apps > trivy-report.txt'
                // Archive it so it shows up in your Jenkins dashboard deliverables
                archiveArtifacts artifacts: 'trivy-report.txt', allowEmptyArchive: true
            }
        }

        stage('4. Build Docker Image') {
            steps {
                echo 'Building Docker Image...'
                script {
                    appImage = docker.build("${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}")
                    // Also tag it as latest
                    sh "docker tag ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('5. Push to Docker Hub') {
            steps {
                echo 'Pushing Image to Docker Hub...'
                // 'docker-hub-credentials' is the ID of credentials we will make in Step 3
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
                // Triggers Render's build mechanism using a silent curl request
                sh "curl -X POST '${RENDER_DEPLOY_HOOK}'"
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution finished.'
            cleanWs() // Clean workspace after completion
        }
    }
}
}