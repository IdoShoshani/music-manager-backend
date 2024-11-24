pipeline {
    agent {
        kubernetes {
            defaultContainer 'docker'
            yamlFile 'jenkins-pod.yaml'
        }
    }
    environment {
        IMAGE_NAME = 'idoshoshani123/music-app-backend'
        REGISTRY_URL = 'https://registry.hub.docker.com'
        DOCKER_CREDS_ID = 'docker-creds'
    }
    stages {
        stage('Checkout') {
            steps {
                script {
                    // Checkout the code from the repository
                    checkout scm
                }
            }
        }
        stage('Python Linter') {
            steps {
                container('python') {
                    script {
                        // Install requirements
                        sh  'pip install -r test_requirements.txt'
                        // Run pylint only for errors
                        sh 'pylint -E app.py'
                    }
                }
            }
        }
        stage('Unit Test') {
            steps {
                container('python') {
                    script {
                        // Install requirements
                        sh 'pip install -r test_requirements.txt'
                        // Run unit tests
                        sh 'pytest --cov=app tests/'
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    // Build the application
                    app = docker.build("${env.IMAGE_NAME}:${env.BUILD_NUMBER}")
                }
            }
        }

        stage('Push image') {
            steps {
                script {
                    docker.withRegistry("${env.REGISTRY_URL}", "${env.DOCKER_CREDS_ID}") {
                        // Push the image with the BUILD_NUMBER tag
                        app.push("${env.BUILD_NUMBER}")
                        // Push the image with the latest tag
                        app.push("latest")
                    }
                }
            }
        }
    }
}
