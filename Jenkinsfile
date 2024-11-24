pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:20.10-dind
    command:
    - cat
    tty: true
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: docker-sock
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
            '''
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

        // Uncomment and modify the following stage if you want to run unit tests
        // stage('Unit Test') {
        //     steps {
        //         script {
        //             // Run unit tests
        //             sh 'make test'  // Modify this according to your test process
        //         }
        //     }
        // }
    }

    post {
        always {
            script {
                // Clean workspace after each build
                cleanWs()
            }
        }
    }
}
