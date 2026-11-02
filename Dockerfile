# =========================================================================
# Multi-Stage / Production Dockerfile for Student Management System
# =========================================================================

# Step 1: Base runtime environment
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# Install essential system dependencies (curl for container healthcheck)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data directory
COPY student_manager/ ${APP_HOME}/student_manager/
COPY tests/ ${APP_HOME}/tests/

# Create application data directory and non-privileged user for security
RUN mkdir -p ${APP_HOME}/data \
    && useradd -u 1000 -m -s /bin/bash appuser \
    && chown -R appuser:appuser ${APP_HOME}

# Switch to unprivileged user
USER appuser

# Expose standard application port
EXPOSE 5000

# Container Healthcheck (polls the /health REST endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Launch the Flask application
CMD ["python", "-m", "student_manager.app"]
