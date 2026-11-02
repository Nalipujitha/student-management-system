"""
Command-line interface for Student Management System.
"""

import argparse
import sys
from student_manager.models import Student, ValidationError
from student_manager.manager import StudentManager, DuplicateStudentError, StudentNotFoundError


def parse_args():
    parser = argparse.ArgumentParser(
        description="Student Management System - DevOps Edition"
    )
    parser.add_argument("--storage", default="data/students.json", help="Path to JSON storage file")
    parser.add_argument("--seed", action="store_true", help="Seed sample data")
    parser.add_argument("--list", action="store_true", help="List all students")
    parser.add_argument("--search", help="Search query (name, ID, email, course)")
    parser.add_argument("--dept", help="Filter students by department")
    parser.add_argument("--stats", action="store_true", help="Display summary statistics")
    parser.add_argument("--add", action="store_true", help="Add a new student")
    parser.add_argument("--id", help="Student ID")
    parser.add_argument("--name", help="Student Name")
    parser.add_argument("--email", help="Student Email")
    parser.add_argument("--department", help="Student Department")
    parser.add_argument("--attendance", type=float, default=100.0, help="Attendance percentage")
    parser.add_argument("--delete", help="Delete student by ID")
    return parser.parse_args()


def print_table(students):
    if not students:
        print("No student records found.")
        return

    header = f"{'ID':<10} | {'Name':<20} | {'Department':<20} | {'GPA':<5} | {'Attendance':<10} | {'Status':<16}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    for s in students:
        print(
            f"{s.student_id:<10} | {s.name:<20} | {s.department:<20} | "
            f"{s.calculate_gpa():<5.2f} | {s.attendance:<10.1f}% | {s.get_academic_status():<16}"
        )
    print("-" * len(header))


def main():
    args = parse_args()
    manager = StudentManager(storage_path=args.storage)

    if args.seed:
        manager.seed_sample_data()
        print("✓ Sample student records successfully seeded.")

    if args.add:
        if not (args.id and args.name and args.email and args.department):
            print("Error: Adding a student requires --id, --name, --email, and --department.")
            sys.exit(1)
        try:
            student = Student(
                student_id=args.id,
                name=args.name,
                email=args.email,
                department=args.department,
                attendance=args.attendance,
            )
            manager.add_student(student)
            print(f"✓ Student '{student.name}' ({student.student_id}) successfully added.")
        except (ValidationError, DuplicateStudentError) as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.delete:
        try:
            manager.delete_student(args.delete)
            print(f"✓ Student '{args.delete}' successfully deleted.")
        except StudentNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.stats:
        stats = manager.get_overall_summary()
        print("\n=== Academic System Statistics ===")
        print(f"Total Students:        {stats['total_students']}")
        print(f"Class Average GPA:     {stats['average_gpa']:.2f} / 4.0")
        print(f"Dean's List Honors:    {stats['deans_list_count']}")
        print(f"Good Standing:         {stats['good_standing_count']}")
        print(f"Academic Probation:    {stats['probation_count']}")
        print("\nDepartment Breakdown:")
        for dept, data in stats["department_stats"].items():
            print(f"  • {dept:<22}: {data['count']} students (Avg GPA: {data['avg_gpa']:.2f})")
        print("==================================\n")

    elif args.list or args.search or args.dept:
        students = manager.list_students(department=args.dept, search=args.search)
        print_table(students)

    else:
        # Default action: if no flags, list students or show brief help
        students = manager.list_students()
        if not students:
            print("No students in database. Run with --seed to populate initial records or --help for commands.")
        else:
            print_table(students)


if __name__ == "__main__":
    main()
