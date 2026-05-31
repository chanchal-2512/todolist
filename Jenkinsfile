pipeline {
    agent any
    
    environment {
        // Replace with your actual Docker Hub username and repo name
        DOCKER_HUB_USER = 'chanchal2512' 
        IMAGE_NAME      = 'todo-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
    }

    stages {
        stage('1. Fetch Source Code') {
            steps {
                checkout scm
            }
        }

        stage('2. Code Quality Analysis') {
            steps {
                echo 'Running Code Quality Analysis via SonarQube (SonarCloud)...'
                withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_KEY')]) {
                    // Spin up the official scanner container to read your code workspace
                    bat """
                        docker run --rm -v "%cd%:/usr/src" sonarsource/sonar-scanner-cli \
                        -Dsonar.projectKey=chanchal-2512_todolist \
                        -Dsonar.organization=chanchal-2512 \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=https://sonarcloud.io \
                        -Dsonar.token=%SONAR_KEY%
                    """
                }
            }
        }

        stage('3. Vulnerability Scanning') {
            steps {
                bat """
                    docker run --rm ^
                    -v /var/run/docker.sock:/var/run/docker.sock ^
                    aquasec/trivy image ^
                    --exit-code 0 ^
                    --format table ^
                    %DOCKER_HUB_USER%/%IMAGE_NAME%:%IMAGE_TAG% > trivy-report.txt 2>&1
                """
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
                withCredentials([string(credentialsId: 'RENDER_DEPLOY_HOOK', variable: 'RENDER_HOOK')]) {
                    // For Windows (bat) environments:
                    bat "curl --ssl-no-revoke -X POST \"%RENDER_HOOK%\""
                }
            }
        }
    } // Closes stages
    
    post {
        always {
            echo 'Pipeline execution finished.'
            cleanWs()
        }
    } // Closes post
} // Closes pipeline