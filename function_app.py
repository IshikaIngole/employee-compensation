import json
import logging
from decimal import Decimal

import azure.functions as func

from services.employee_service import EmployeeService
from services.compensation_service import CompensationService

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

employee_service = EmployeeService()
compensation_service = CompensationService()


def response(body, status_code=200):
    return func.HttpResponse(
        body=json.dumps(body, default=str),
        status_code=status_code,
        mimetype="application/json",
    )


def get_json(req):
    try:
        return req.get_json()
    except ValueError:
        raise ValueError("Request body must contain valid JSON.")


# -------------------------
# Employee CRUD
# -------------------------

@app.route(route="employees", methods=["POST"])
def create_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = get_json(req)
        employee = employee_service.create_employee(data)
        return response(employee, 201)
    except ValueError as exc:
        return response({"error": str(exc)}, 400)
    except Exception:
        logging.exception("Error creating employee")
        return response({"error": "Internal server error."}, 500)


@app.route(route="employees/{employee_id}", methods=["GET"])
def get_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        employee_id = int(req.route_params["employee_id"])
        employee = employee_service.get_employee(employee_id)

        if employee is None:
            return response({"error": "Employee not found."}, 404)

        return response(employee)
    except ValueError:
        return response({"error": "Employee ID must be an integer."}, 400)
    except Exception:
        logging.exception("Error retrieving employee")
        return response({"error": "Internal server error."}, 500)


@app.route(route="employees", methods=["GET"])
def get_employees(req: func.HttpRequest) -> func.HttpResponse:
    try:
        department_id = req.params.get("departmentId")
        if department_id is not None:
            department_id = int(department_id)

        employees = employee_service.get_employees(department_id)
        return response({"count": len(employees), "employees": employees})
    except ValueError:
        return response({"error": "departmentId must be an integer."}, 400)
    except Exception:
        logging.exception("Error retrieving employees")
        return response({"error": "Internal server error."}, 500)


@app.route(route="employees/{employee_id}", methods=["PUT"])
def update_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        employee_id = int(req.route_params["employee_id"])
        data = get_json(req)

        employee = employee_service.update_employee(employee_id, data)

        if employee is None:
            return response({"error": "Employee not found."}, 404)

        return response(employee)
    except ValueError as exc:
        return response({"error": str(exc)}, 400)
    except Exception:
        logging.exception("Error updating employee")
        return response({"error": "Internal server error."}, 500)


@app.route(route="employees/{employee_id}", methods=["DELETE"])
def delete_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        employee_id = int(req.route_params["employee_id"])
        deleted = employee_service.delete_employee(employee_id)

        if not deleted:
            return response({"error": "Employee not found."}, 404)

        return func.HttpResponse(status_code=204)
    except ValueError:
        return response({"error": "Employee ID must be an integer."}, 400)
    except Exception:
        logging.exception("Error deleting employee")
        return response({"error": "Internal server error."}, 500)


# -------------------------
# Compensation reports
# -------------------------

@app.route(route="reports/total-bonus", methods=["GET"])
def total_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        return response(compensation_service.total_bonus())
    except Exception:
        logging.exception("Error calculating total bonus")
        return response({"error": "Internal server error."}, 500)


@app.route(route="reports/no-bonus", methods=["GET"])
def employees_without_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        employees = compensation_service.employees_without_bonus()
        return response({"count": len(employees), "employees": employees})
    except Exception:
        logging.exception("Error retrieving employees without bonus")
        return response({"error": "Internal server error."}, 500)


@app.route(route="reports/bonus-percentage", methods=["GET"])
def bonus_percentage(req: func.HttpRequest) -> func.HttpResponse:
    try:
        rows = compensation_service.bonus_percentage()
        return response({"count": len(rows), "employees": rows})
    except Exception:
        logging.exception("Error calculating bonus percentage")
        return response({"error": "Internal server error."}, 500)


@app.route(route="reports/department-bonus", methods=["GET"])
def department_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        rows = compensation_service.departments_bonus_exceeds_average_salary()
        return response({"count": len(rows), "departments": rows})
    except Exception:
        logging.exception("Error calculating department bonus report")
        return response({"error": "Internal server error."}, 500)


@app.route(route="reports/bonus-ranking", methods=["GET"])
def bonus_ranking(req: func.HttpRequest) -> func.HttpResponse:
    try:
        rows = compensation_service.bonus_ranking()
        return response({"count": len(rows), "employees": rows})
    except Exception:
        logging.exception("Error calculating bonus ranking")
        return response({"error": "Internal server error."}, 500)


@app.route(route="reports/highest-salary", methods=["GET"])
def highest_salary(req: func.HttpRequest) -> func.HttpResponse:
    try:
        return response(compensation_service.highest_salary_vs_total_compensation())
    except Exception:
        logging.exception("Error calculating highest salary report")
        return response({"error": "Internal server error."}, 500)
