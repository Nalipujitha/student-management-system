pipeline {
    agent any

    environment {
        APP_NAME     = 'student-management-system'
        DOCKER_IMAGE = 'student-management-system'
        IMAGE_TAG    = "${env.BUILD_NUMBER}"
        REPORTS_DIR  = 'reports'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
        timestamps()
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo '=================================================='
                echo "Fetching source code from repository: ${env.BRANCH_NAME ?: 'main'}"
                echo '=================================================='
                checkout scm
            }
        }

        stage('Environment & Dependencies') {
            steps {
                echo 'Setting up Python runtime and installing dependencies...'
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv venv || python -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                            python -m venv venv
                            call venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            python -m pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Syntax & Quality Verification') {
            steps {
                echo 'Verifying Python syntax and code integrity...'
                script {
                    if (isUnix()) {
                        sh '''
                            . venv/bin/activate
                            python3 -m compileall student_manager tests
                        '''
                    } else {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            python -m compileall student_manager tests
                        '''
                    }
                }
            }
        }

        stage('Automated Testing') {
            steps {
                echo 'Executing automated test suite and generating JUnit XML report...'
                script {
                    if (isUnix()) {
                        sh '''
                            . venv/bin/activate
                            mkdir -p reports
                            pytest -v --junitxml=reports/test-results.xml tests/
                        '''
                    } else {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            if not exist reports mkdir reports
                            python -m pytest -v --junitxml=reports/test-results.xml tests/
                        '''
                    }
                }
            }
        }

        stage('Container Build') {
            steps {
                echo "Building Docker container image: ${DOCKER_IMAGE}:${IMAGE_TAG}..."
                script {
                    if (isUnix()) {
                        sh """
                            docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} -t ${DOCKER_IMAGE}:latest .
                        """
                    } else {
                        bat """
                            docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} -t ${DOCKER_IMAGE}:latest .
                        """
                    }
                }
            }
        }

        stage('Container Verification & Smoke Test') {
            steps {
                echo 'Running container smoke test to verify /health endpoint...'
                script {
                    if (isUnix()) {
                        sh """
                            docker run -d --name temp_smoke_test -p 5001:5000 ${DOCKER_IMAGE}:${IMAGE_TAG}
                            sleep 4
                            curl -f http://localhost:5001/health || exit 1
                            docker stop temp_smoke_test
                            docker rm temp_smoke_test
                        """
                    } else {
                        bat """
                            docker run -d --name temp_smoke_test -p 5001:5000 ${DOCKER_IMAGE}:${IMAGE_TAG}
                            timeout /t 4 /nobreak
                            curl -f http://localhost:5001/health
                            docker stop temp_smoke_test
                            docker rm temp_smoke_test
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Publishing automated test results to Jenkins...'
            junit testResults: 'reports/test-results.xml', allowEmptyResults: false
            cleanWs(cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    notFailBuild: true,
                    patterns: [[pattern: 'venv/**', type: 'EXCLUDE']])
        }
        success {
            echo "=========================================================="
            echo "CI/CD Pipeline Build #${env.BUILD_NUMBER} SUCCEEDED!"
            echo "Artifact Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
            echo "=========================================================="
        }
        failure {
            echo "=========================================================="
            echo "CI/CD Pipeline Build #${env.BUILD_NUMBER} FAILED!"
            echo "Check console logs and JUnit test reports for failure diagnostics."
            echo "=========================================================="
        }
    }
}
