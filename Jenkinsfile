pipeline {
    agent { label 'prod' }
    stages {
        stage('Stop') {
            steps{
                script {
                    sh('sudo systemctl stop telegram-bot.service -l')
                }
            }
        }
        stage('Pull') {
            steps{
                script {
                   dir("/home/centos/prod") {
                        sh "git pull"
                    }
                }
            }
        }
        stage('Start') {
            steps{
                script {
                    sh('sudo systemctl start telegram-bot.service')
                }
            }
        }
    }
}
