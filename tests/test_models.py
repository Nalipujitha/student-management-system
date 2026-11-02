"""
Unit tests for Student model validations, GPA calculations, and serialization.
"""

import pytest
from student_manager.models import Student, ValidationError


class TestStudentModel:
    """Test suite for Student data model and domain rules."""

    def test_valid_student_creation(self):
        """Test creating a student with valid fields."""
        student = Student(
            student_id="STD-001",
            name="John Doe",
            email="john.doe@example.com",
            department="Computer Science",
            attendance=95.0,
        )
        assert student.student_id == "STD-001"
        assert student.name == "John Doe"
        assert student.email == "john.doe@example.com"
        assert student.department == "Computer Science"
        assert student.attendance == 95.0
        assert student.courses == []
        assert student.grades == {}

    def test_invalid_email_raises_validation_error(self):
        """Test that invalid email format raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid email address"):
            Student(
                student_id="STD-002",
                name="Jane Doe",
                email="not-an-email",
                department="Data Science",
            )

    def test_empty_student_id_or_name_raises_error(self):
        """Test that empty student_id or short name raises ValidationError."""
        with pytest.raises(ValidationError, match="Student ID cannot be empty"):
            Student(
                student_id="",
                name="Jane",
                email="jane@example.com",
                department="Physics",
            )

        with pytest.raises(ValidationError, match="at least 2 characters"):
            Student(
                student_id="STD-003",
                name="J",
                email="jane@example.com",
                department="Physics",
            )

    def test_invalid_attendance_range_raises_error(self):
        """Test that attendance outside 0-100 raises ValidationError."""
        with pytest.raises(ValidationError, match="Attendance must be between 0.0 and 100.0"):
            Student(
                student_id="STD-004",
                name="Alex Smith",
                email="alex@example.com",
                department="Math",
                attendance=105.0,
            )

        with pytest.raises(ValidationError, match="Attendance must be between 0.0 and 100.0"):
            Student(
                student_id="STD-005",
                name="Alex Smith",
                email="alex@example.com",
                department="Math",
                attendance=-5.0,
            )

    def test_gpa_calculation_with_varied_grades(self):
        """Test 4.0 scale GPA calculation."""
        student = Student(
            student_id="STD-006",
            name="Robert Frost",
            email="robert@example.com",
            department="Literature",
            grades={
                "Poetry": 95.0,   # 4.0
                "Drama": 85.0,    # 3.5
                "Prose": 75.0,    # 2.5
            },
        )
        # Expected average = (4.0 + 3.5 + 2.5) / 3 = 10.0 / 3 = 3.33
        assert student.calculate_gpa() == 3.33

    def test_academic_status_distinctions(self):
        """Test distinction between Dean's List, Good Standing, and Academic Probation."""
        # Dean's List: GPA >= 3.7 and attendance >= 85
        honors_student = Student(
            student_id="STD-007",
            name="Honor Student",
            email="honor@example.com",
            department="Engineering",
            grades={"Math": 95.0, "Physics": 92.0},
            attendance=90.0,
        )
        assert honors_student.get_academic_status() == "Dean's List"

        # Academic Probation: GPA < 2.5
        probation_student = Student(
            student_id="STD-008",
            name="Struggling Student",
            email="struggling@example.com",
            department="Engineering",
            grades={"Math": 55.0, "Physics": 62.0},
            attendance=80.0,
        )
        assert probation_student.get_academic_status() == "Academic Probation"

    def test_student_serialization_roundtrip(self):
        """Test serialization to dict and deserialization from dict."""
        original = Student(
            student_id="STD-009",
            name="Sarah Connor",
            email="sarah@example.com",
            department="Robotics",
            courses=["AI", "Cybernetics"],
            grades={"AI": 98.0, "Cybernetics": 94.0},
            attendance=97.5,
        )
        as_dict = original.to_dict()
        assert as_dict["student_id"] == "STD-009"
        assert as_dict["gpa"] == 4.0
        assert as_dict["status"] == "Dean's List"

        reconstructed = Student.from_dict(as_dict)
        assert reconstructed.student_id == original.student_id
        assert reconstructed.name == original.name
        assert reconstructed.email == original.email
        assert reconstructed.calculate_gpa() == original.calculate_gpa()
