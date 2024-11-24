pipeline{
    agent all
    stages{
        stage("hello world"){
            steps{
                script{
                    sh 'echo hello world'
                }
            }
        }
    }
    post{
        always{
            echo "========always========"
        }
        success{
            echo "========pipeline executed successfully ========"
        }
        failure{
            echo "========pipeline execution failed========"
        }
    }
}