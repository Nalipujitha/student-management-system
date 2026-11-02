"""
Integration tests for Flask web routes and REST API endpoints.
"""

import json
import pytest
from student_manager.app import create_app


@pytest.fixture
def client(tmp_path):
    """Provides a Flask test client with an isolated temporary storage file."""
    temp_storage = str(tmp_path / "test_students.json")
    app = create_app(storage_path=temp_storage)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestApiEndpoints:
    """Test suite for HTTP REST API."""

    def test_health_check_endpoint(self, client):
        """Test GET /health returns 200 with status healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "student-management-system"

    def test_get_students_list(self, client):
        """Test GET /api/students returns seeded list."""
        response = client.get("/api/students")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_create_student_success(self, client):
        """Test POST /api/students successfully creates a student."""
        payload = {
            "student_id": "STD-999",
            "name": "Integration Test Student",
            "email": "integration@test.edu",
            "department": "Computer Science",
            "attendance": 92.0,
            "courses": ["DevOps", "Testing"],
            "grades": {"DevOps": 95.0, "Testing": 90.0},
        }
        response = client.post(
            "/api/students",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["student_id"] == "STD-999"
        assert data["name"] == "Integration Test Student"
        assert data["gpa"] == 4.0

    def test_create_duplicate_student_fails(self, client):
        """Test POST /api/students with duplicate ID returns 400 Bad Request."""
        payload = {
            "student_id": "STD-101",  # Existing seeded ID
            "name": "Duplicate Student",
            "email": "dup@test.edu",
            "department": "Computer Science",
        }
        response = client.post(
            "/api/students",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_get_single_student_and_delete(self, client):
        """Test GET and DELETE for a specific student."""
        # Query existing student
        response = client.get("/api/students/STD-101")
        assert response.status_code == 200
        assert response.get_json()["name"] == "Alice Johnson"

        # Delete student
        del_response = client.delete("/api/students/STD-101")
        assert del_response.status_code == 200

        # Query again, should be 404
        query_response = client.get("/api/students/STD-101")
        assert query_response.status_code == 404

    def test_stats_endpoint(self, client):
        """Test GET /api/stats returns analytics summary."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        stats = response.get_json()
        assert "total_students" in stats
        assert "average_gpa" in stats
        assert "department_stats" in stats
