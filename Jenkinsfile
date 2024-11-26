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

                            sed -i "s/^tag:.*/tag: ${VERSION}/" values.yaml

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
        stage('Push Changes to GitLab') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'gitlab-creds', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                        sh '''
                            set -e
                            
                            # Configure git
                            git config --global --add safe.directory "${WORKSPACE}"
                            git config --global user.email "jenkins@example.com"
                            git config --global user.name "Jenkins"
                            
                            # Set git credentials helper
                            git config --global credential.helper '!f() { echo "username=${USERNAME}"; echo "password=${PASSWORD}"; }; f'
                            
                            # Ensure we're in the right directory
                            cd "${WORKSPACE}"
                            
                            # Setup remote with auth
                            git remote set-url origin "https://${USERNAME}:${PASSWORD}@gitlab.com/sela-tracks/1109/students/idosh/final_project/application/music-manager-backend.git"
                            
                            # Ensure we're on the right branch
                            git fetch origin
                            git checkout -B 6-create-jenkins-pipeline-for-backend origin/6-create-jenkins-pipeline-for-backend || git checkout -b 6-create-jenkins-pipeline-for-backend
                            
                            # Stage and commit changes
                            git add charts/Chart.yaml
                            git add charts/values.yaml
                            git add charts/*.tgz
                            
                            # Only commit if there are changes
                            if git diff --staged --quiet; then
                                echo "No changes to commit"
                            else
                                git commit -m "ci: Update image tag to ${BUILD_NUMBER}"
                                git push origin HEAD:6-create-jenkins-pipeline-for-backend
                            fi
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