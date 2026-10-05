from database.db import get_connection


class CompensationService:

    def total_bonus(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COALESCE(SUM(Bonus), 0)
                FROM Employee
                """
            )
            total = cursor.fetchone()[0]

            return {"totalBonus": float(total or 0)}

    def employees_without_bonus(self):
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
                WHERE Bonus IS NULL
                ORDER BY EmployeeID
                """
            )

            return [self._employee_row(row) for row in cursor.fetchall()]

    def bonus_percentage(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    EmployeeID,
                    FirstName,
                    LastName,
                    Salary,
                    Bonus,
                    ROUND((Bonus / NULLIF(Salary, 0)) * 100, 2)
                        AS BonusPercentage
                FROM Employee
                WHERE Bonus IS NOT NULL
                  AND Salary > 0
                ORDER BY EmployeeID
                """
            )

            return [
                {
                    "employeeId": row[0],
                    "firstName": row[1],
                    "lastName": row[2],
                    "salary": float(row[3]),
                    "bonus": float(row[4]),
                    "bonusPercentage": float(row[5]),
                }
                for row in cursor.fetchall()
            ]

    def departments_bonus_exceeds_average_salary(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    d.DepartmentID,
                    d.DepartmentName,
                    d.Location,
                    COALESCE(SUM(e.Bonus), 0) AS TotalBonus,
                    AVG(e.Salary) AS AverageSalary
                FROM Department d
                INNER JOIN Employee e
                    ON e.DepartmentID = d.DepartmentID
                GROUP BY
                    d.DepartmentID,
                    d.DepartmentName,
                    d.Location
                HAVING COALESCE(SUM(e.Bonus), 0) > AVG(e.Salary)
                ORDER BY d.DepartmentID
                """
            )

            return [
                {
                    "departmentId": row[0],
                    "departmentName": row[1],
                    "location": row[2],
                    "totalBonus": float(row[3]),
                    "averageSalary": float(row[4]),
                }
                for row in cursor.fetchall()
            ]

    def bonus_ranking(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    EmployeeID,
                    FirstName,
                    LastName,
                    Salary,
                    Bonus,
                    ROW_NUMBER() OVER (
                        ORDER BY
                            CASE WHEN Bonus IS NULL THEN 1 ELSE 0 END,
                            Bonus DESC,
                            EmployeeID
                    ) AS BonusRank
                FROM Employee
                ORDER BY
                    CASE WHEN Bonus IS NULL THEN 1 ELSE 0 END,
                    Bonus DESC,
                    EmployeeID
                """
            )

            return [
                {
                    "rank": int(row[5]),
                    "employeeId": row[0],
                    "firstName": row[1],
                    "lastName": row[2],
                    "salary": float(row[3]),
                    "bonus": float(row[4]) if row[4] is not None else None,
                }
                for row in cursor.fetchall()
            ]

    def highest_salary_vs_total_compensation(self):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT TOP 1
                    EmployeeID,
                    FirstName,
                    LastName,
                    Salary,
                    Bonus,
                    Salary + COALESCE(Bonus, 0) AS TotalCompensation
                FROM Employee
                ORDER BY Salary DESC, EmployeeID
                """
            )
            highest_salary = cursor.fetchone()

            cursor.execute(
                """
                SELECT TOP 1
                    EmployeeID,
                    FirstName,
                    LastName,
                    Salary,
                    Bonus,
                    Salary + COALESCE(Bonus, 0) AS TotalCompensation
                FROM Employee
                ORDER BY
                    Salary + COALESCE(Bonus, 0) DESC,
                    EmployeeID
                """
            )
            highest_compensation = cursor.fetchone()

            if highest_salary is None:
                return {
                    "highestBaseSalaryEmployee": None,
                    "highestTotalCompensationEmployee": None,
                    "samePerson": False,
                }

            salary_employee = self._compensation_row(highest_salary)
            compensation_employee = self._compensation_row(highest_compensation)

            return {
                "highestBaseSalaryEmployee": salary_employee,
                "highestTotalCompensationEmployee": compensation_employee,
                "samePerson": (
                    salary_employee["employeeId"]
                    == compensation_employee["employeeId"]
                ),
            }

    @staticmethod
    def _employee_row(row):
        return {
            "employeeId": row[0],
            "firstName": row[1],
            "lastName": row[2],
            "departmentId": row[3],
            "salary": float(row[4]),
            "bonus": float(row[5]) if row[5] is not None else None,
            "hireDate": row[6].isoformat() if row[6] else None,
        }

    @staticmethod
    def _compensation_row(row):
        return {
            "employeeId": row[0],
            "firstName": row[1],
            "lastName": row[2],
            "salary": float(row[3]),
            "bonus": float(row[4]) if row[4] is not None else None,
            "totalCompensation": float(row[5]),
        }
