-- Optional manual verification queries.

-- 1. Total bonus; NULL treated as zero.
SELECT COALESCE(SUM(Bonus), 0) AS TotalBonus
FROM Employee;

-- 2. Employees with no bonus.
SELECT *
FROM Employee
WHERE Bonus IS NULL;

-- 3. Bonus percentage.
SELECT
    EmployeeID,
    FirstName,
    LastName,
    ROUND((Bonus / NULLIF(Salary, 0)) * 100, 2) AS BonusPercentage
FROM Employee
WHERE Bonus IS NOT NULL
  AND Salary > 0;

-- 4. Departments where total bonus > average salary.
SELECT
    d.DepartmentID,
    d.DepartmentName,
    COALESCE(SUM(e.Bonus), 0) AS TotalBonus,
    AVG(e.Salary) AS AverageSalary
FROM Department d
JOIN Employee e
  ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentID, d.DepartmentName
HAVING COALESCE(SUM(e.Bonus), 0) > AVG(e.Salary);

-- 5. Bonus ranking; NULL bonuses last.
SELECT
    EmployeeID,
    FirstName,
    LastName,
    Bonus,
    ROW_NUMBER() OVER (
        ORDER BY
            CASE WHEN Bonus IS NULL THEN 1 ELSE 0 END,
            Bonus DESC,
            EmployeeID
    ) AS BonusRank
FROM Employee;

-- 6. Highest base salary.
SELECT TOP 1 *
FROM Employee
ORDER BY Salary DESC, EmployeeID;

-- Highest total compensation.
SELECT TOP 1
    EmployeeID,
    FirstName,
    LastName,
    Salary,
    Bonus,
    Salary + COALESCE(Bonus, 0) AS TotalCompensation
FROM Employee
ORDER BY Salary + COALESCE(Bonus, 0) DESC, EmployeeID;
