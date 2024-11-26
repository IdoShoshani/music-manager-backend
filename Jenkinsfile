pipeline {
    agent {
        kubernetes {
            defaultContainer 'docker'
            yamlFile 'jenkins-pod.yaml'
        }
    }
    environment {
        IMAGE_NAME = 'idoshoshani123/music-app-backend'
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
                    def registryNamespace = env.IMAGE_NAME.split('/')[0]

                    withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            cd ${HELM_CHART_PATH}

                            # Update appVersion to Docker Image version
                            sed -i "s/^appVersion:.*/appVersion: ${VERSION}/" Chart.yaml

                            # Log in to OCI Registry
                            echo "$DOCKER_PASS" | helm registry login registry-1.docker.io -u "$DOCKER_USER" --password-stdin

                            # Get version from chart.yaml
                            CHART_VERSION=$(sed -n 's/^version: *//p' Chart.yaml)

                            # Package Helm Chart
                            helm package .

                            # Debug files
                            ls -la 

                            # Push Helm Chart to OCI Registry
                            helm push music-app-backend-$CHART_VERSION.tgz oci://registry-1.docker.io/idoshoshani123
                        '''
                    }
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
