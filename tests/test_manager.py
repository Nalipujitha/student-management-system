"""
Unit tests for StudentManager business logic, storage, search, and analytics.
"""

import os
import tempfile
import pytest
from student_manager.models import Student
from student_manager.manager import (
    StudentManager,
    DuplicateStudentError,
    StudentNotFoundError,
)


@pytest.fixture
def empty_manager():
    """Provides a fresh, empty StudentManager instance without persistent storage."""
    return StudentManager()


@pytest.fixture
def populated_manager():
    """Provides a StudentManager loaded with sample data."""
    manager = StudentManager()
    manager.seed_sample_data()
    return manager


class TestStudentManager:
    """Test suite for StudentManager service."""

    def test_add_and_get_student_success(self, empty_manager):
        """Test adding and retrieving a student."""
        student = Student(
            student_id="S-100",
            name="Grace Hopper",
            email="grace@navy.mil",
            department="Computer Science",
        )
        empty_manager.add_student(student)

        retrieved = empty_manager.get_student("S-100")
        assert retrieved.name == "Grace Hopper"
        assert retrieved.email == "grace@navy.mil"

    def test_get_nonexistent_student_raises_error(self, empty_manager):
        """Test that querying a nonexistent student raises StudentNotFoundError."""
        with pytest.raises(StudentNotFoundError):
            empty_manager.get_student("NONEXISTENT")

    def test_duplicate_student_id_raises_error(self, empty_manager):
        """Test that duplicate student ID is rejected."""
        s1 = Student(student_id="S-101", name="User One", email="one@test.com", department="CS")
        s2 = Student(student_id="S-101", name="User Two", email="two@test.com", department="IT")
        empty_manager.add_student(s1)

        with pytest.raises(DuplicateStudentError, match="already exists"):
            empty_manager.add_student(s2)

    def test_duplicate_student_email_raises_error(self, empty_manager):
        """Test that duplicate student email is rejected."""
        s1 = Student(student_id="S-102", name="User One", email="same@test.com", department="CS")
        s2 = Student(student_id="S-103", name="User Two", email="same@test.com", department="IT")
        empty_manager.add_student(s1)

        with pytest.raises(DuplicateStudentError, match="already exists"):
            empty_manager.add_student(s2)

    def test_update_student_details(self, empty_manager):
        """Test updating student details."""
        student = Student(
            student_id="S-104",
            name="Alan Turing",
            email="alan@cambridge.ac.uk",
            department="Mathematics",
            attendance=90.0,
        )
        empty_manager.add_student(student)

        updated = empty_manager.update_student("S-104", name="Sir Alan Turing", attendance=98.0)
        assert updated.name == "Sir Alan Turing"
        assert updated.attendance == 98.0

    def test_delete_student_success(self, empty_manager):
        """Test deleting a student."""
        student = Student(
            student_id="S-105",
            name="Ada Lovelace",
            email="ada@analytical.org",
            department="Mathematics",
        )
        empty_manager.add_student(student)
        assert len(empty_manager.list_students()) == 1

        deleted = empty_manager.delete_student("S-105")
        assert deleted is True
        assert len(empty_manager.list_students()) == 0

    def test_filter_students_by_department(self, populated_manager):
        """Test filtering students by department."""
        cs_students = populated_manager.list_students(department="Computer Science")
        assert len(cs_students) == 2
        assert all(s.department == "Computer Science" for s in cs_students)

    def test_filter_students_by_search_query(self, populated_manager):
        """Test searching students by keyword."""
        results = populated_manager.list_students(search="Johnson")
        assert len(results) == 1
        assert results[0].name == "Alice Johnson"

    def test_overall_summary_statistics(self, populated_manager):
        """Test statistical analytics generation."""
        summary = populated_manager.get_overall_summary()
        assert summary["total_students"] == 5
        assert summary["average_gpa"] > 0.0
        assert summary["deans_list_count"] >= 1
        assert "Computer Science" in summary["department_stats"]

    def test_json_export_and_import(self, empty_manager):
        """Test data persistence through JSON export and load."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            s1 = Student(student_id="S-201", name="Nikola Tesla", email="nikola@ac.org", department="EE")
            s2 = Student(student_id="S-202", name="Marie Curie", email="marie@sorbonne.fr", department="Physics")
            empty_manager.add_student(s1)
            empty_manager.add_student(s2)

            empty_manager.export_to_json(tmp_path)
            assert os.path.exists(tmp_path)

            new_manager = StudentManager(storage_path=tmp_path)
            assert len(new_manager.list_students()) == 2
            assert new_manager.get_student("S-201").name == "Nikola Tesla"
            assert new_manager.get_student("S-202").name == "Marie Curie"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
