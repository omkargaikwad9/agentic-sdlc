pipeline {

    agent any

    options {
        disableConcurrentBuilds()
    }

    stages {

        stage('Show Issue Information') {
            steps {
                bat "echo Repository: %REPOSITORY_URL%"
                bat "echo Issue Number: %ISSUE_NUMBER%"
                bat "echo Issue Title: %ISSUE_TITLE%"
                bat "echo Issue Body: %ISSUE_BODY%"
            }
        }

        stage('Checkout Target Repository') {
            steps {
                dir('target') {
                    git branch: 'main',
                        url: "${params.REPOSITORY_URL}",
                        credentialsId: 'omkargaikwad9'
                }
            }
        }

        stage('Check Target Repository') {
            steps {
                dir('target') {
                    bat 'git status'
                    bat 'git branch'
                    bat 'dir'
                }
            }
        }

        stage('Create Agent Branch') {
            steps {
                dir('target') {
                    bat 'git checkout -B agent/issue-%ISSUE_NUMBER%'
                    bat 'git branch'
                }
            }
        }

        stage('Git Diff Check') {
            steps {
                bat '''
                    python -m utils.travers._git_diff target
                '''
            }
        }

    }
}