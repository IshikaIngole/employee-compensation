import logging

from flask import Flask, jsonify, request

from services.employee_service import EmployeeService
from services.compensation_service import CompensationService

app = Flask(__name__)

employee_service = EmployeeService()
compensation_service = CompensationService()


# -------------------------
# Employee CRUD
# -------------------------

@app.route("/api/employees", methods=["POST"])
def create_employee():
    try:
        data = request.get_json()
        if data is None:
            raise ValueError("Request body must contain valid JSON.")

        employee = employee_service.create_employee(data)
        return jsonify(employee), 201

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logging.exception("Error creating employee")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/employees/<employee_id>", methods=["GET"])
def get_employee(employee_id):
    try:
        employee_id = int(employee_id)
        employee = employee_service.get_employee(employee_id)

        if employee is None:
            return jsonify({"error": "Employee not found."}), 404

        return jsonify(employee)

    except ValueError:
        return jsonify({"error": "Employee ID must be an integer."}), 400
    except Exception:
        logging.exception("Error retrieving employee")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/employees", methods=["GET"])
def get_employees():
    try:
        department_id = request.args.get("departmentId")

        if department_id is not None:
            department_id = int(department_id)

        employees = employee_service.get_employees(department_id)

        return jsonify({
            "count": len(employees),
            "employees": employees
        })

    except ValueError:
        return jsonify({"error": "departmentId must be an integer."}), 400
    except Exception:
        logging.exception("Error retrieving employees")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/employees/<employee_id>", methods=["PUT"])
def update_employee(employee_id):
    try:
        employee_id = int(employee_id)

        data = request.get_json()
        if data is None:
            raise ValueError("Request body must contain valid JSON.")

        employee = employee_service.update_employee(employee_id, data)

        if employee is None:
            return jsonify({"error": "Employee not found."}), 404

        return jsonify(employee)

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logging.exception("Error updating employee")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/employees/<employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    try:
        employee_id = int(employee_id)

        deleted = employee_service.delete_employee(employee_id)

        if not deleted:
            return jsonify({"error": "Employee not found."}), 404

        return "", 204

    except ValueError:
        return jsonify({"error": "Employee ID must be an integer."}), 400
    except Exception:
        logging.exception("Error deleting employee")
        return jsonify({"error": "Internal server error."}), 500


# -------------------------
# Compensation reports
# -------------------------

@app.route("/api/reports/total-bonus", methods=["GET"])
def total_bonus():
    try:
        return jsonify(compensation_service.total_bonus())
    except Exception:
        logging.exception("Error calculating total bonus")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/reports/no-bonus", methods=["GET"])
def employees_without_bonus():
    try:
        employees = compensation_service.employees_without_bonus()

        return jsonify({
            "count": len(employees),
            "employees": employees
        })

    except Exception:
        logging.exception("Error retrieving employees without bonus")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/reports/bonus-percentage", methods=["GET"])
def bonus_percentage():
    try:
        rows = compensation_service.bonus_percentage()

        return jsonify({
            "count": len(rows),
            "employees": rows
        })

    except Exception:
        logging.exception("Error calculating bonus percentage")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/reports/department-bonus", methods=["GET"])
def department_bonus():
    try:
        rows = compensation_service.departments_bonus_exceeds_average_salary()

        return jsonify({
            "count": len(rows),
            "departments": rows
        })

    except Exception:
        logging.exception("Error calculating department bonus report")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/reports/bonus-ranking", methods=["GET"])
def bonus_ranking():
    try:
        rows = compensation_service.bonus_ranking()

        return jsonify({
            "count": len(rows),
            "employees": rows
        })

    except Exception:
        logging.exception("Error calculating bonus ranking")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/reports/highest-salary", methods=["GET"])
def highest_salary():
    try:
        return jsonify(
            compensation_service.highest_salary_vs_total_compensation()
        )

    except Exception:
        logging.exception("Error calculating highest salary report")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Employee Compensation API",
        "status": "running"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
