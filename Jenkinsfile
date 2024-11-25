pipeline {
    agent {
        kubernetes {
            defaultContainer 'docker'
            yamlFile 'jenkins-pod.yaml'
        }
    }
    environment {
        IMAGE_NAME = 'idoshoshani123/music-app-backend'
        DOCKER_CREDS = credentials('docker-creds')
        HELM_CHART_PATH = 'charts'
        VERSION = "${env.BUILD_NUMBER}"
    }
    options {
        timeout(time: 1, unit: 'HOURS')
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Python Linter') {
            steps {
                container('python') {
                    sh 'pip install -r test_requirements.txt'
                    sh 'pylint -E app.py'
                }
            }
        }
        stage('Unit Test') {
            steps {
                container('python') {
                    sh 'pip install -r test_requirements.txt'
                    sh 'pytest --cov=app tests/'
                }
            }
        }
        stage('Build Application Image') {
            steps {
                script {
                    app = docker.build("${env.IMAGE_NAME}:${env.VERSION}")
                }
            }
        }
        stage('Push Application Image') {
            steps {
                script {
                    docker.withRegistry("", 'docker-creds') {
                        app.push("${env.VERSION}")
                        app.push("latest")
                    }
                }
            }
        }
        stage('Verify Helm Chart') {
            steps {
                sh "helm lint ${env.HELM_CHART_PATH}"
            }
        }
        stage('Update & Push Helm Chart') {
            steps {
                script {
                    sh """
                        cd ${env.HELM_CHART_PATH}

                        # Update version and appVersion to the Docker Image version
                        sed -i 's/^version:.*/version: ${env.VERSION}/' Chart.yaml
                        sed -i 's/^appVersion:.*/appVersion: ${env.VERSION}/' Chart.yaml

                        # Update the tag in values.yaml to the Docker Image version
                        sed -i 's|tag:.*|tag: ${env.VERSION}|' values.yaml

                        # Connecting to the OCI Registry
                        echo "${env.DOCKER_CREDS_PSW}" | helm registry login registry-1.docker.io -u "${env.DOCKER_CREDS_USR}" --password-stdin

                        # Helm Chart packaging
                        helm package .

                        # Uploading the Helm Chart to the OCI Registry
                        helm push music-app-backend-${env.VERSION}.tgz oci://registry-1.docker.io/${env.IMAGE_NAME.split('/')[0]}
                    """
                }
            }
        }
    }
    post {
        always {
            sh 'helm registry logout registry-1.docker.io'
        }
    }
}
