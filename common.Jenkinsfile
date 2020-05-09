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
    }
}
