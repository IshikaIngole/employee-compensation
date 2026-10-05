-- Seed departments
INSERT INTO dbo.Department (DepartmentID, DepartmentName, Location)
VALUES
    (1, 'Engineering', 'Pune'),
    (2, 'Human Resources', 'Mumbai'),
    (3, 'Finance', 'Bengaluru'),
    (4, 'Sales', 'Delhi');

-- Seed employees
INSERT INTO dbo.Employee
    (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
VALUES
    ('Aarav', 'Sharma', 1, 900000.00, 150000.00, '2021-04-12'),
    ('Priya', 'Patel', 1, 750000.00, 50000.00, '2022-07-18'),
    ('Rahul', 'Mehta', 2, 600000.00, NULL, '2023-01-09'),
    ('Neha', 'Kulkarni', 2, 650000.00, 25000.00, '2020-11-20'),
    ('Vikram', 'Singh', 3, 1200000.00, 100000.00, '2019-05-06'),
    ('Ananya', 'Rao', 3, 800000.00, NULL, '2024-02-15'),
    ('Rohan', 'Desai', 4, 500000.00, 300000.00, '2022-09-01'),
    ('Sneha', 'Joshi', 4, 550000.00, NULL, '2025-03-10');
