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
            when {
                branch 'main'
            }
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
            when {
                branch 'main'
            }            
            steps {
                sh "helm lint ${env.HELM_CHART_PATH}"
            }
        }
        stage('Update & Push Helm Chart') {
            when {
                branch 'main'
            }            
            steps {
                script {
                    def registryNamespace = env.IMAGE_NAME.split('/')[0]
                    withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            cd ${env.HELM_CHART_PATH}
                            
                            # Update appVersion to Docker Image version with quotes
                            sed -i "s/^appVersion:.*/appVersion: \\"${VERSION}\\"/" Chart.yaml
                            
                            # Update tag to Docker Image version with quotes
                            sed -i "s/^  tag: .*/  tag: \\"${VERSION}\\"/" values.yaml
                            
                            # Update chart version
                            CURRENT_VERSION=\$(grep 'version:' Chart.yaml | awk '{print \$2}')
                            MAJOR=\$(echo \$CURRENT_VERSION | cut -d. -f1)
                            MINOR=\$(echo \$CURRENT_VERSION | cut -d. -f2)
                            PATCH=\$(echo \$CURRENT_VERSION | cut -d. -f3)
                            NEW_PATCH=\$((\$PATCH + 1))
                            NEW_VERSION="\$MAJOR.\$MINOR.\$NEW_PATCH"
                            sed -i "s/^version:.*/version: \$NEW_VERSION/" Chart.yaml
                            
                            # Log in to OCI Registry
                            echo "\${DOCKER_PASS}" | helm registry login registry-1.docker.io -u "\${DOCKER_USER}" --password-stdin
                            
                            # Get version from chart.yaml
                            CHART_VERSION=\$(sed -n 's/^version: *//p' Chart.yaml)
                            
                            # Package Helm Chart
                            helm package .
                            
                            # Debug files
                            ls -la
                            
                            # Push Helm Chart to OCI Registry
                            helm push music-app-backend-\${CHART_VERSION}.tgz oci://registry-1.docker.io/idoshoshani123
                        """
                    }
                }
            }
        }
        stage('Push Changes to GitLab') {
            when { branch 'main' }            
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'gitlab-creds', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                        sh '''
                            set -e
                            
                            # Configure git
                            git config --global --add safe.directory "${WORKSPACE}"
                            git config --global user.email "jenkins@example.com"
                            git config --global user.name "Jenkins"
                            
                            git config --global credential.helper '!f() { echo "username=${USERNAME}"; echo "password=${PASSWORD}"; }; f'
                            
                            cd "${WORKSPACE}"
                            
                            # Set remote with credentials
                            git remote set-url origin "https://${USERNAME}:${PASSWORD}@gitlab.com/sela-tracks/1109/students/idosh/final_project/application/music-manager-backend.git"
                            
                            git fetch origin
                            git add charts/Chart.yaml
                            git add charts/values.yaml
                            
                            if git diff --staged --quiet; then
                                echo "No changes to commit"
                            else
                                git commit -m "ci: Update image tag to ${BUILD_NUMBER}"
                                # Push to the current branch
                                git push origin HEAD:main
                            fi
                        '''
                    }
                }
            }
        }
    }
    post {
        always {
            sh 'helm registry logout registry-1.docker.io || true'
        }
    }
}