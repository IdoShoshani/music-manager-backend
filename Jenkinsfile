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
        UNIQUE_DOCKERFILE = 'Dockerfile.helm.chart'
    }
    stages {
        stage('Checkout') {
            steps {
                script {
                    checkout scm
                }
            }
        }
        stage('Python Linter') {
            steps {
                container('python') {
                    script {
                        sh 'pip install -r test_requirements.txt'
                        sh 'pylint -E app.py'
                    }
                }
            }
        }
        stage('Unit Test') {
            steps {
                container('python') {
                    script {
                        sh 'pip install -r test_requirements.txt'
                        sh 'pytest --cov=app tests/'
                    }
                }
            }
        }
        stage('Build Application Image') {
            steps {
                script {
                    app = docker.build("${env.IMAGE_NAME}:${env.BUILD_NUMBER}")
                }
            }
        }
        stage('Push Application Image') {
            steps {
                script {
                    docker.withRegistry("${env.REGISTRY_URL}", "${env.DOCKER_CREDS_ID}") {
                        app.push("${env.BUILD_NUMBER}")
                        app.push("latest")
                    }
                }
            }
        }
        stage('Helm Package') {
            steps {
                script {
                    def helmOutput = sh(
                        script: 'helm package charts -d ./packages',
                        returnStdout: true
                    ).trim()
                    def chartFile = helmOutput.split(':')[1].trim()
                    env.CHART_FILE = chartFile
                    echo "Helm chart packaged: ${env.CHART_FILE}"
                }
            }
        }
        stage('Create Unique Dockerfile') {
            steps {
                script {
                    // Create a unique Dockerfile for the Helm chart
                    sh """
                    echo "FROM alpine:latest" > ${env.UNIQUE_DOCKERFILE}
                    echo "COPY ${env.CHART_FILE} /charts/" >> ${env.UNIQUE_DOCKERFILE}
                    """
                    echo "Unique Dockerfile created: ${env.UNIQUE_DOCKERFILE}"
                }
            }
        }

        stage('Build Helm Chart Docker Image') {
            steps {
                script {
                    def chartImage = docker.build(
                        "${env.IMAGE_NAME}-chart:${env.BUILD_NUMBER}",
                        "-f ${env.UNIQUE_DOCKERFILE} ."
                    )
                    env.CHART_IMAGE = chartImage.id
                }
            }
        }
        stage('Push Helm Chart Image') {
            steps {
                script {
                    docker.withRegistry("${env.REGISTRY_URL}", "${env.DOCKER_CREDS_ID}") {
                        def chartImage = docker.image("${env.IMAGE_NAME}-chart:${env.BUILD_NUMBER}")
                        chartImage.push("${env.BUILD_NUMBER}")
                        chartImage.push("latest")
                    }
                }
            }
        }
    }
}
