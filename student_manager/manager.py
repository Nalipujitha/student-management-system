"""
Business logic and storage management for students.
"""

import json
import os
from typing import Dict, List, Optional
from student_manager.models import Student, ValidationError


class DuplicateStudentError(ValueError):
    """Raised when attempting to add a student with an existing ID or email."""
    pass


class StudentNotFoundError(KeyError):
    """Raised when a student cannot be found."""
    pass


class StudentManager:
    """Manages collection of students with CRUD, analytics, and persistence."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self._students: Dict[str, Student] = {}

        if self.storage_path and os.path.exists(self.storage_path):
            self.load_from_json(self.storage_path)

    def add_student(self, student: Student) -> Student:
        """Adds a new student. Raises DuplicateStudentError if ID or email is taken."""
        if student.student_id in self._students:
            raise DuplicateStudentError(
                f"Student with ID '{student.student_id}' already exists."
            )

        for existing in self._students.values():
            if existing.email == student.email:
                raise DuplicateStudentError(
                    f"Student with email '{student.email}' already exists."
                )

        self._students[student.student_id] = student
        self._auto_save()
        return student

    def get_student(self, student_id: str) -> Student:
        """Retrieves a student by ID. Raises StudentNotFoundError if not found."""
        student_id_clean = str(student_id).strip()
        if student_id_clean not in self._students:
            raise StudentNotFoundError(f"Student with ID '{student_id_clean}' not found.")
        return self._students[student_id_clean]

    def update_student(self, student_id: str, **kwargs) -> Student:
        """Updates student fields and validates modifications."""
        student = self.get_student(student_id)

        # If email is being updated, verify uniqueness
        new_email = kwargs.get("email")
        if new_email:
            new_email_clean = str(new_email).strip().lower()
            for other_id, other in self._students.items():
                if other_id != student.student_id and other.email == new_email_clean:
                    raise DuplicateStudentError(f"Email '{new_email_clean}' is already in use.")

        current_dict = student.to_dict()
        for key, value in kwargs.items():
            if key in current_dict and key not in ("student_id", "gpa", "status"):
                current_dict[key] = value

        updated_student = Student.from_dict(current_dict)
        self._students[student_id] = updated_student
        self._auto_save()
        return updated_student

    def delete_student(self, student_id: str) -> bool:
        """Deletes a student by ID. Raises StudentNotFoundError if not found."""
        student_id_clean = str(student_id).strip()
        if student_id_clean not in self._students:
            raise StudentNotFoundError(f"Student with ID '{student_id_clean}' not found.")
        del self._students[student_id_clean]
        self._auto_save()
        return True

    def list_students(
        self,
        department: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Student]:
        """Lists students with optional department, status, and text search filters."""
        results = list(self._students.values())

        if department:
            dept_lower = department.strip().lower()
            results = [s for s in results if s.department.lower() == dept_lower]

        if status:
            status_lower = status.strip().lower()
            results = [s for s in results if s.get_academic_status().lower() == status_lower]

        if search:
            query = search.strip().lower()
            results = [
                s for s in results
                if query in s.name.lower()
                or query in s.student_id.lower()
                or query in s.email.lower()
                or any(query in c.lower() for c in s.courses)
            ]

        return results

    def calculate_class_average_gpa(self) -> float:
        """Calculates the overall average GPA of all registered students."""
        if not self._students:
            return 0.0
        gpas = [s.calculate_gpa() for s in self._students.values()]
        return round(sum(gpas) / len(gpas), 2)

    def get_department_statistics(self) -> dict:
        """Computes summary statistics grouped by department."""
        stats: Dict[str, dict] = {}
        for student in self._students.values():
            dept = student.department
            if dept not in stats:
                stats[dept] = {"count": 0, "total_gpa": 0.0, "deans_list_count": 0}

            stats[dept]["count"] += 1
            stats[dept]["total_gpa"] += student.calculate_gpa()
            if student.get_academic_status() == "Dean's List":
                stats[dept]["deans_list_count"] += 1

        for dept, data in stats.items():
            data["avg_gpa"] = round(data["total_gpa"] / data["count"], 2)
            del data["total_gpa"]

        return stats

    def get_overall_summary(self) -> dict:
        """Returns comprehensive summary analytics for dashboard/API."""
        total = len(self._students)
        deans_list = sum(1 for s in self._students.values() if s.get_academic_status() == "Dean's List")
        probation = sum(1 for s in self._students.values() if s.get_academic_status() == "Academic Probation")
        good_standing = total - deans_list - probation

        return {
            "total_students": total,
            "average_gpa": self.calculate_class_average_gpa(),
            "deans_list_count": deans_list,
            "good_standing_count": good_standing,
            "probation_count": probation,
            "department_count": len(set(s.department for s in self._students.values())),
            "department_stats": self.get_department_statistics(),
        }

    def export_to_json(self, filepath: str) -> None:
        """Exports all students to a JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        data = [s.to_dict() for s in self._students.values()]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_json(self, filepath: str) -> None:
        """Loads students from a JSON file, replacing current state."""
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._students = {item["student_id"]: Student.from_dict(item) for item in data}

    def _auto_save(self) -> None:
        """Persists to disk if storage_path was specified."""
        if self.storage_path:
            self.export_to_json(self.storage_path)

    def seed_sample_data(self) -> None:
        """Populates manager with realistic initial student records."""
        sample_students = [
            Student(
                student_id="STD-101",
                name="Alice Johnson",
                email="alice.j@university.edu",
                department="Computer Science",
                courses=["Algorithms", "Operating Systems", "Cloud Computing"],
                grades={"Algorithms": 95.0, "Operating Systems": 92.0, "Cloud Computing": 94.0},
                attendance=96.0,
            ),
            Student(
                student_id="STD-102",
                name="Bob Williams",
                email="bob.w@university.edu",
                department="Computer Science",
                courses=["Algorithms", "Databases"],
                grades={"Algorithms": 82.0, "Databases": 85.0},
                attendance=90.0,
            ),
            Student(
                student_id="STD-103",
                name="Catherine Davis",
                email="catherine.d@university.edu",
                department="Data Science",
                courses=["Machine Learning", "Statistics", "Data Mining"],
                grades={"Machine Learning": 98.0, "Statistics": 95.0, "Data Mining": 92.0},
                attendance=98.0,
            ),
            Student(
                student_id="STD-104",
                name="Daniel Miller",
                email="daniel.m@university.edu",
                department="Electrical Engineering",
                courses=["Circuits", "Signals"],
                grades={"Circuits": 68.0, "Signals": 64.0},
                attendance=75.0,
            ),
            Student(
                student_id="STD-105",
                name="Elena Rostova",
                email="elena.r@university.edu",
                department="Data Science",
                courses=["Deep Learning", "NLP"],
                grades={"Deep Learning": 88.0, "NLP": 89.0},
                attendance=92.0,
            ),
        ]
        for student in sample_students:
            if student.student_id not in self._students:
                self.add_student(student)
