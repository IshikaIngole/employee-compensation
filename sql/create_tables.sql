-- Employee Compensation Service
-- SQL Server / Azure SQL

IF OBJECT_ID('dbo.Employee', 'U') IS NOT NULL
    DROP TABLE dbo.Employee;

IF OBJECT_ID('dbo.Department', 'U') IS NOT NULL
    DROP TABLE dbo.Department;

CREATE TABLE dbo.Department
(
    DepartmentID INT NOT NULL PRIMARY KEY,
    DepartmentName VARCHAR(100) NOT NULL,
    Location VARCHAR(100) NULL
);

CREATE TABLE dbo.Employee
(
    EmployeeID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    DepartmentID INT NOT NULL,
    Salary DECIMAL(12,2) NOT NULL,
    Bonus DECIMAL(12,2) NULL,
    HireDate DATE NULL,

    CONSTRAINT FK_Employee_Department
        FOREIGN KEY (DepartmentID)
        REFERENCES dbo.Department(DepartmentID),

    CONSTRAINT CK_Employee_Salary_NonNegative
        CHECK (Salary >= 0),

    CONSTRAINT CK_Employee_Bonus_NonNegative
        CHECK (Bonus IS NULL OR Bonus >= 0)
);
