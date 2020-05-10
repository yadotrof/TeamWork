pipeline {
    agent { label 'prod' }
    stages {
        stage('Lint') {
            steps{
                script {
                    sh('pycodestyle --show-source *.py')
                }
            }
        }
        stage('Unit tests') {
            steps{
                script {
                    sh('cp config.example config.py')
                    sh('python3 test.py')
                }
            }
        }
    }
}

