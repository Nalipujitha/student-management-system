# 🎓 Student Management System — DevOps CI/CD Platform

A DevOps-ready Python application designed with automated testing, Docker containerization, and a Jenkins CI/CD declarative pipeline with JUnit test reporting and GitHub webhook triggers.

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Application Architecture](#-application-architecture)
3. [Local Development & Setup](#-local-development--setup)
4. [Automated Testing with Pytest](#-automated-testing-with-pytest)
5. [Containerization with Docker](#-containerization-with-docker)
6. [Jenkins CI/CD Pipeline Setup](#-jenkins-cicd-pipeline-setup)
7. [GitHub Repository & Version Control Guide](#-github-repository--version-control-guide)
8. [API Reference & Endpoints](#-api-reference--endpoints)

---

## 🌟 Project Overview

This repository demonstrates the end-to-end DevOps lifecycle for a Python-based **Student Management System**:
- **Application Core**: Python 3.12 dataclasses, validation engine, GPA calculator, and persistent storage.
- **Web Dashboard & API**: Flask application featuring a modern glassmorphic dashboard and REST API.
- **CLI Utility**: Command-line management script for scripting, data seeding, and system monitoring.
- **Automated Testing**: 23 comprehensive tests using Pytest with JUnit XML output generation.
- **Docker Containerization**: Lean, non-root `python:3.12-slim` container with healthchecks and compose orchestration.
- **CI/CD Automation**: Cross-platform Jenkinsfile declarative pipeline with test reports visualization and automatic SCM triggers.

---

## 🏛 Application Architecture

```
student-management-system/
│
├── student_manager/
│   ├── __init__.py           # Package exports & version
│   ├── models.py             # Student dataclass, field validation & GPA logic
│   ├── manager.py            # StudentManager service: CRUD, search & analytics
│   ├── app.py                # Flask Web UI server & REST API
│   ├── cli.py                # Command-line interface
│   ├── templates/
│   │   └── index.html        # Glassmorphic Web Dashboard
│   └── static/
│       ├── css/style.css     # Responsive dark-mode styling
│       └── js/app.js         # Asynchronous AJAX client
│
├── tests/
│   ├── __init__.py
│   ├── test_models.py        # Model validation & GPA tests
│   ├── test_manager.py       # CRUD & business logic unit tests
│   └── test_api.py           # Flask REST API integration tests
│
├── Dockerfile                # Production multi-stage Dockerfile
├── .dockerignore             # Docker build ignore rules
├── docker-compose.yml        # Multi-container orchestration
├── Jenkinsfile               # Declarative Jenkins CI/CD pipeline
├── requirements.txt          # Production & testing dependencies
├── .gitignore                # Git repository ignore rules
└── README.md                 # Complete documentation
```

---

## 💻 Local Development & Setup

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git 2.40+
- Docker Desktop (optional, for containerization)

### 1. Clone & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/<your-username>/student-management-system.git
cd student-management-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (cmd/PowerShell):
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
python -m student_manager.app
```
Access the application dashboard in your web browser at: **`http://localhost:5000`**

### 3. Use the CLI Tool
```bash
# Seed initial sample data
python -m student_manager.cli --seed

# List all students
python -m student_manager.cli --list

# View academic statistics
python -m student_manager.cli --stats

# Add a student via CLI
python -m student_manager.cli --add --id "STD-106" --name "Sarah Miller" --email "s.miller@univ.edu" --department "Data Science" --attendance 96.5

# Search records
python -m student_manager.cli --search "Sarah"
```

---

## 🧪 Automated Testing with Pytest

The project includes unit and integration tests covering data validation, GPA calculation, error handling, file persistence, and HTTP endpoints.

### Run All Tests
```bash
python -m pytest -v
```

### Run Tests and Generate JUnit XML Report (Used by Jenkins)
```bash
python -m pytest -v --junitxml=reports/test-results.xml tests/
```

### Test Coverage Breakdown
- `tests/test_models.py`:
  - Valid student instantiation
  - Email format validation (regex)
  - ID and name length validation
  - Attendance boundary checks (0% - 100%)
  - Grade range checks (0 - 100)
  - 4.0 scale GPA calculation
  - Academic status categorization ("Dean's List", "Good Standing", "Academic Probation")
  - JSON serialization & deserialization
- `tests/test_manager.py`:
  - CRUD operations (Create, Read, Update, Delete)
  - Duplicate student ID rejection
  - Duplicate email address rejection
  - Search and filter by department and text query
  - Class average GPA and department aggregation
  - JSON export and load persistence
- `tests/test_api.py`:
  - `/health` endpoint status
  - `/api/students` GET listing
  - `/api/students` POST creation & validation
  - Duplicate student 400 error handling
  - `/api/students/<id>` DELETE handling
  - `/api/stats` metrics summary

---

## 🐳 Containerization with Docker

The `Dockerfile` is optimized using `python:3.12-slim` with a dedicated non-root security user and integrated container health checks.

### 1. Build the Docker Image
```bash
docker build -t student-management-system:latest .
```

### 2. Run the Container
```bash
docker run -d -p 5000:5000 --name student_app student-management-system:latest
```

### 3. Check Container Health
```bash
docker ps
curl http://localhost:5000/health
```

### 4. Run with Docker Compose
```bash
docker-compose up -d --build
```
To stop the services:
```bash
docker-compose down
```

---

## ⚙️ Jenkins CI/CD Pipeline Setup

### 1. Install & Launch Jenkins

#### Option A: Run Jenkins via Docker (Recommended)
```bash
docker run -d \
  --name jenkins-server \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

#### Option B: Run Jenkins via WAR on Windows (Native Java)
1. Download `jenkins.war` from [https://www.jenkins.io/download/](https://www.jenkins.io/download/).
2. Run in terminal:
   ```cmd
   java -jar jenkins.war --httpPort=8080
   ```
3. Open `http://localhost:8080` in your browser.
4. Retrieve the initial admin password shown in the console or located at:
   `C:\Users\<user>\.jenkins\secrets\initialAdminPassword`
5. Select **Install Suggested Plugins**.

### 2. Install Required Jenkins Plugins
Navigate to **Manage Jenkins** ➔ **Plugins** ➔ **Available plugins** and ensure these plugins are installed:
- **Git plugin** (fetches source code from GitHub)
- **Pipeline** (executes `Jenkinsfile`)
- **JUnit Plugin** (renders graphical test results and trends)
- **Docker Pipeline** (optional, for Docker builds inside pipeline)

### 3. Configure the Pipeline Job in Jenkins
1. On the Jenkins dashboard, click **New Item**.
2. Enter item name: `Student-Management-Pipeline`.
3. Select **Pipeline** and click **OK**.
4. In the configuration page, scroll down to the **Pipeline** section:
   - **Definition**: Select `Pipeline script from SCM`.
   - **SCM**: Select `Git`.
   - **Repository URL**: Enter your GitHub repository URL (e.g., `https://github.com/<your-username>/student-management-system.git`).
   - **Credentials**: Add your GitHub Personal Access Token or SSH credentials if private.
   - **Branch Specifier**: `*/main`.
   - **Script Path**: `Jenkinsfile`.
5. Under **Build Triggers**:
   - Check **GitHub hook trigger for GITScm polling** (for instant webhook triggers).
   - Alternatively, check **Poll SCM** with schedule `H/5 * * * *` (polls every 5 minutes).
6. Click **Save**.

### 4. Configure GitHub Webhook for Automatic Builds
1. In your GitHub repository, go to **Settings** ➔ **Webhooks** ➔ **Add webhook**.
2. **Payload URL**: `http://<your-jenkins-ip-or-ngrok-url>:8080/github-webhook/`
3. **Content type**: `application/json`
4. **Which events would you like to trigger this webhook?**: Select `Just the push event`.
5. Click **Add webhook**.
*(Now, every time you `git push` new code to GitHub, Jenkins will automatically start the build!)*

### 5. View Test Results in Jenkins
When the pipeline executes:
- Jenkins parses `reports/test-results.xml` generated by pytest.
- A **Test Result Trend** graph appears on the pipeline dashboard showing passed, skipped, and failed tests over time.
- Click **Latest Test Result** to drill down into test execution duration, classes, and individual assertions.

---

## 🚀 GitHub Repository & Version Control Guide

Follow these steps to upload this project to your GitHub account:

### 1. Create a New Repository on GitHub
1. Go to [https://github.com/new](https://github.com/new).
2. Repository name: `student-management-system`
3. Visibility: Choose **Public** or **Private**.
4. Do **not** initialize with README, `.gitignore`, or license (we already created them locally).
5. Click **Create repository**.

### 2. Link Local Git Repository and Push
Run the following commands in this directory:
```bash
# 1. Verify git status
git status

# 2. Add remote GitHub URL (replace with your actual GitHub repo URL)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/student-management-system.git

# 3. Rename branch to main (if not already main)
git branch -M main

# 4. Push code to GitHub
git push -u origin main
```

---

## 📡 API Reference & Endpoints

| Method | Endpoint | Description | Sample Response Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Web Management Dashboard | `200 OK` |
| `GET` | `/health` | Container & Service Healthcheck | `200 OK` |
| `GET` | `/api/students` | List students (query params: `dept`, `status`, `search`) | `200 OK` |
| `POST` | `/api/students` | Register new student record | `201 Created` / `400 Bad Request` |
| `GET` | `/api/students/<id>` | Retrieve specific student | `200 OK` / `404 Not Found` |
| `PUT` | `/api/students/<id>` | Update student information | `200 OK` / `400 / 404` |
| `DELETE` | `/api/students/<id>`| Remove student record | `200 OK` / `404 Not Found` |
| `GET` | `/api/stats` | Academic analytics & KPI metrics | `200 OK` |
| `POST` | `/api/seed` | Populate starter demonstration data | `200 OK` |

DevOps CI/CD automatic polling verification.

Final Jenkins CI/CD automatic build verification.