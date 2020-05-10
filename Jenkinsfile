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
        stage('Requirements') {
            steps{
                script {
                   dir("/home/centos/prod") {
                        sh "pip3 install -r requirements.txt"
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
