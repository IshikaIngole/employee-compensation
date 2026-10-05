from datetime import date

from database.db import get_connection


REQUIRED_FIELDS = [
    "firstName",
    "lastName",
    "departmentId",
    "salary",
    "hireDate",
]


def row_to_employee(row):
    return {
        "employeeId": row[0],
        "firstName": row[1],
        "lastName": row[2],
        "departmentId": row[3],
        "salary": float(row[4]),
        "bonus": float(row[5]) if row[5] is not None else None,
        "hireDate": row[6].isoformat() if row[6] else None,
    }


class EmployeeService:

    def create_employee(self, data):
        self._validate_employee_data(data, partial=False)

        first_name = data["firstName"].strip()
        last_name = data["lastName"].strip()
        department_id = int(data["departmentId"])
        salary = float(data["salary"])
        bonus = data.get("bonus")
        hire_date = data["hireDate"]

        if bonus is not None:
            bonus = float(bonus)

        with get_connection() as conn:
            cursor = conn.cursor()

            self._ensure_department_exists(cursor, department_id)

            cursor.execute(
                """
                INSERT INTO Employee
                    (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
                OUTPUT
                    INSERTED.EmployeeID,
                    INSERTED.FirstName,
                    INSERTED.LastName,
                    INSERTED.DepartmentID,
                    INSERTED.Salary,
                    INSERTED.Bonus,
                    INSERTED.HireDate
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                first_name,
                last_name,
                department_id,
                salary,
                bonus,
                hire_date,
            )

            row = cursor.fetchone()
            conn.commit()
            return row_to_employee(row)

    def get_employee(self, employee_id):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    EmployeeID,
                    FirstName,
                    LastName,
                    DepartmentID,
                    Salary,
                    Bonus,
                    HireDate
                FROM Employee
                WHERE EmployeeID = ?
                """,
                employee_id,
            )

            row = cursor.fetchone()
            return row_to_employee(row) if row else None

    def get_employees(self, department_id=None):
        with get_connection() as conn:
            cursor = conn.cursor()

            if department_id is None:
                cursor.execute(
                    """
                    SELECT
                        EmployeeID,
                        FirstName,
                        LastName,
                        DepartmentID,
                        Salary,
                        Bonus,
                        HireDate
                    FROM Employee
                    ORDER BY EmployeeID
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        EmployeeID,
                        FirstName,
                        LastName,
                        DepartmentID,
                        Salary,
                        Bonus,
                        HireDate
                    FROM Employee
                    WHERE DepartmentID = ?
                    ORDER BY EmployeeID
                    """,
                    department_id,
                )

            return [row_to_employee(row) for row in cursor.fetchall()]

    def update_employee(self, employee_id, data):
        self._validate_employee_data(data, partial=True)

        allowed = {
            "firstName": "FirstName",
            "lastName": "LastName",
            "departmentId": "DepartmentID",
            "salary": "Salary",
            "bonus": "Bonus",
            "hireDate": "HireDate",
        }

        if not data:
            raise ValueError("At least one field must be supplied for update.")

        assignments = []
        values = []

        for key, column in allowed.items():
            if key in data:
                value = data[key]

                if key in ("firstName", "lastName"):
                    value = value.strip()
                elif key in ("departmentId",):
                    value = int(value)
                elif key in ("salary", "bonus") and value is not None:
                    value = float(value)

                assignments.append(f"{column} = ?")
                values.append(value)

        with get_connection() as conn:
            cursor = conn.cursor()

            if "departmentId" in data:
                self._ensure_department_exists(cursor, int(data["departmentId"]))

            values.append(employee_id)

            cursor.execute(
                f"""
                UPDATE Employee
                SET {", ".join(assignments)}
                OUTPUT
                    INSERTED.EmployeeID,
                    INSERTED.FirstName,
                    INSERTED.LastName,
                    INSERTED.DepartmentID,
                    INSERTED.Salary,
                    INSERTED.Bonus,
                    INSERTED.HireDate
                WHERE EmployeeID = ?
                """,
                *values,
            )

            row = cursor.fetchone()

            if row is None:
                conn.rollback()
                return None

            conn.commit()
            return row_to_employee(row)

    def delete_employee(self, employee_id):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM Employee WHERE EmployeeID = ?",
                employee_id,
            )

            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted

    @staticmethod
    def _ensure_department_exists(cursor, department_id):
        cursor.execute(
            "SELECT 1 FROM Department WHERE DepartmentID = ?",
            department_id,
        )

        if cursor.fetchone() is None:
            raise ValueError(f"Department {department_id} does not exist.")

    @staticmethod
    def _validate_employee_data(data, partial):
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")

        if not partial:
            for field in REQUIRED_FIELDS:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

        if "firstName" in data:
            if not isinstance(data["firstName"], str) or not data["firstName"].strip():
                raise ValueError("firstName must be a non-empty string.")

        if "lastName" in data:
            if not isinstance(data["lastName"], str) or not data["lastName"].strip():
                raise ValueError("lastName must be a non-empty string.")

        if "departmentId" in data:
            try:
                if int(data["departmentId"]) <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                raise ValueError("departmentId must be a positive integer.")

        if "salary" in data:
            try:
                if float(data["salary"]) < 0:
                    raise ValueError
            except (TypeError, ValueError):
                raise ValueError("salary must be a non-negative number.")

        if "bonus" in data and data["bonus"] is not None:
            try:
                if float(data["bonus"]) < 0:
                    raise ValueError
            except (TypeError, ValueError):
                raise ValueError("bonus must be a non-negative number.")

        if "hireDate" in data:
            try:
                date.fromisoformat(data["hireDate"])
            except (TypeError, ValueError):
                raise ValueError("hireDate must use YYYY-MM-DD format.")
