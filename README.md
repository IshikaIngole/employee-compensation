# Employee Compensation Service

Python Azure Functions + Azure SQL implementation of the Employee Compensation Service assignment.

## Architecture

Client -> HTTP-triggered Azure Function -> Service layer -> SQL data access -> Azure SQL

Clients never access the database directly.

## Requirements

- Python 3.11/3.12 recommended for a straightforward Azure Functions setup
- Azure Functions Core Tools v4
- Azure CLI (for deployment)
- ODBC Driver 18 for SQL Server
- An Azure SQL Database

## Project structure

```text
function_app.py
database/db.py
services/employee_service.py
services/compensation_service.py
sql/create_tables.sql
sql/seed_data.sql
requirements.txt
host.json
local.settings.json
```

## Local setup

1. Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `local.settings.json.example` to `local.settings.json`.

4. Replace `SqlConnectionString` with your SQL Server/Azure SQL connection string.

5. Run `sql/create_tables.sql`, then `sql/seed_data.sql` against your database.

6. Start the Function App:

```bash
func start
```

The local base URL is normally:

```text
http://localhost:7071/api
```

## Endpoints

### CRUD

```text
POST   /api/employees
GET    /api/employees/{employeeId}
GET    /api/employees
GET    /api/employees?departmentId={departmentId}
PUT    /api/employees/{employeeId}
DELETE /api/employees/{employeeId}
```

### Reports

```text
GET /api/reports/total-bonus
GET /api/reports/no-bonus
GET /api/reports/bonus-percentage
GET /api/reports/department-bonus
GET /api/reports/bonus-ranking
GET /api/reports/highest-salary
```

## Example create request

```json
{
  "firstName": "John",
  "lastName": "Smith",
  "departmentId": 1,
  "salary": 700000,
  "bonus": 50000,
  "hireDate": "2026-01-15"
}
```

`bonus` may be omitted or set to `null`.

## Production configuration

Do not commit `local.settings.json`.

In Azure, configure `SqlConnectionString` as an Application Setting on the Function App. For stronger production security, Azure Key Vault / managed identity can be introduced as an enhancement.

## Optional 5% default bonus

This implementation does not persist a default 5% bonus. The assignment leaves this behavior optional. If implemented, calculating it at read time preserves the meaning of `Bonus = NULL` in the database.
