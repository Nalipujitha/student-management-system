"""
Flask Web Application and REST API for Student Management System.
"""

import os
from flask import Flask, jsonify, request, render_template
from student_manager.models import Student, ValidationError
from student_manager.manager import (
    StudentManager,
    DuplicateStudentError,
    StudentNotFoundError,
)


def create_app(storage_path: str = None) -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )

    if storage_path is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        storage_path = os.path.join(data_dir, "students.json")

    manager = StudentManager(storage_path=storage_path)

    # Automatically seed sample data if empty
    if len(manager.list_students()) == 0:
        manager.seed_sample_data()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "student-management-system",
            "version": "1.0.0",
            "students_count": len(manager.list_students()),
        }), 200

    @app.route("/api/students", methods=["GET"])
    def get_students():
        dept = request.args.get("dept")
        status = request.args.get("status")
        search = request.args.get("search")
        students = manager.list_students(department=dept, status=status, search=search)
        return jsonify([s.to_dict() for s in students]), 200

    @app.route("/api/students/<student_id>", methods=["GET"])
    def get_student(student_id):
        try:
            student = manager.get_student(student_id)
            return jsonify(student.to_dict()), 200
        except StudentNotFoundError as e:
            return jsonify({"error": str(e)}), 404

    @app.route("/api/students", methods=["POST"])
    def create_student():
        payload = request.get_json() or {}
        try:
            student = Student(
                student_id=payload.get("student_id", ""),
                name=payload.get("name", ""),
                email=payload.get("email", ""),
                department=payload.get("department", ""),
                courses=payload.get("courses", []),
                grades=payload.get("grades", {}),
                attendance=float(payload.get("attendance", 100.0)),
            )
            created = manager.add_student(student)
            return jsonify(created.to_dict()), 201
        except (ValidationError, DuplicateStudentError) as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/students/<student_id>", methods=["PUT"])
    def update_student(student_id):
        payload = request.get_json() or {}
        try:
            updated = manager.update_student(student_id, **payload)
            return jsonify(updated.to_dict()), 200
        except StudentNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except (ValidationError, DuplicateStudentError) as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/students/<student_id>", methods=["DELETE"])
    def delete_student(student_id):
        try:
            manager.delete_student(student_id)
            return jsonify({"message": f"Student '{student_id}' successfully deleted."}), 200
        except StudentNotFoundError as e:
            return jsonify({"error": str(e)}), 404

    @app.route("/api/stats", methods=["GET"])
    def get_stats():
        return jsonify(manager.get_overall_summary()), 200

    @app.route("/api/seed", methods=["POST"])
    def seed_data():
        manager.seed_sample_data()
        return jsonify({"message": "Sample data populated successfully."}), 200

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = create_app()
    print(f"Starting Student Management System on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
