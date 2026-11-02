"""
Student Management System Package.
DevOps-Ready Python Application with automated testing, Docker containerization, and Jenkins CI/CD.
"""

from student_manager.models import Student
from student_manager.manager import StudentManager
from student_manager.app import create_app

__all__ = ["Student", "StudentManager", "create_app"]
__version__ = "1.0.0"
