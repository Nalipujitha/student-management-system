"""
Data models for Student Management System.
"""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class ValidationError(ValueError):
    """Raised when model validation fails."""
    pass


@dataclass
class Student:
    """Represents a student in the management system."""
    student_id: str
    name: str
    email: str
    department: str
    courses: List[str] = field(default_factory=list)
    grades: Dict[str, float] = field(default_factory=dict)
    attendance: float = 100.0

    def __post_init__(self):
        self.student_id = str(self.student_id).strip()
        self.name = str(self.name).strip()
        self.email = str(self.email).strip().lower()
        self.department = str(self.department).strip()
        self.attendance = float(self.attendance)
        self.validate()

    def validate(self) -> None:
        """Validates student attributes."""
        if not self.student_id:
            raise ValidationError("Student ID cannot be empty.")

        if not re.match(r"^[A-Za-z0-9\-_]+$", self.student_id):
            raise ValidationError(
                f"Student ID '{self.student_id}' contains invalid characters. "
                "Only letters, numbers, hyphens, and underscores are allowed."
            )

        if not self.name or len(self.name) < 2:
            raise ValidationError("Student name must be at least 2 characters long.")

        if not EMAIL_REGEX.match(self.email):
            raise ValidationError(f"Invalid email address format: '{self.email}'.")

        if not self.department:
            raise ValidationError("Department cannot be empty.")

        if not (0.0 <= self.attendance <= 100.0):
            raise ValidationError(
                f"Attendance must be between 0.0 and 100.0. Got: {self.attendance}"
            )

        for course, grade in self.grades.items():
            if not isinstance(grade, (int, float)):
                raise ValidationError(f"Grade for '{course}' must be numeric.")
            if not (0.0 <= grade <= 100.0):
                raise ValidationError(
                    f"Grade for '{course}' must be between 0.0 and 100.0. Got: {grade}"
                )

    def calculate_gpa(self) -> float:
        """
        Calculates Grade Point Average on a 4.0 scale based on course percentages.
        Conversion scale:
            90-100: 4.0
            80-89:  3.0 - 3.9
            70-79:  2.0 - 2.9
            60-69:  1.0 - 1.9
            < 60:   0.0
        """
        if not self.grades:
            return 0.0

        total_points = 0.0
        for grade in self.grades.values():
            if grade >= 90:
                points = 4.0
            elif grade >= 80:
                points = 3.0 + (grade - 80) * 0.1
            elif grade >= 70:
                points = 2.0 + (grade - 70) * 0.1
            elif grade >= 60:
                points = 1.0 + (grade - 60) * 0.1
            else:
                points = 0.0
            total_points += points

        return round(total_points / len(self.grades), 2)

    def get_academic_status(self) -> str:
        """Determines academic status based on GPA and attendance."""
        gpa = self.calculate_gpa()
        if gpa >= 3.7 and self.attendance >= 85.0:
            return "Dean's List"
        elif gpa >= 2.5:
            return "Good Standing"
        else:
            return "Academic Probation"

    def add_course_grade(self, course: str, grade: float) -> None:
        """Adds or updates a grade for a course."""
        course_clean = course.strip()
        if not course_clean:
            raise ValidationError("Course name cannot be empty.")
        grade_float = float(grade)
        if not (0.0 <= grade_float <= 100.0):
            raise ValidationError(f"Grade must be between 0.0 and 100.0. Got: {grade_float}")

        if course_clean not in self.courses:
            self.courses.append(course_clean)
        self.grades[course_clean] = grade_float

    def to_dict(self) -> dict:
        """Serializes student to a dictionary."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "courses": list(self.courses),
            "grades": dict(self.grades),
            "attendance": self.attendance,
            "gpa": self.calculate_gpa(),
            "status": self.get_academic_status(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """Deserializes a dictionary into a Student instance."""
        return cls(
            student_id=data.get("student_id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            department=data.get("department", ""),
            courses=data.get("courses", []),
            grades=data.get("grades", {}),
            attendance=float(data.get("attendance", 100.0)),
        )
