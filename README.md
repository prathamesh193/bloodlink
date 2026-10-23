# BloodLink

Blood Bank Management System with automated Software Quality Assurance (STQA academic project).

> **Educational demonstration only.** ABO/Rh matching alone does not establish clinical suitability for transfusion. BloodLink never authorizes a transfusion.

## Status
Milestone 3 (project setup) complete. Compatibility module (DT-1, DT-2) implemented and unit-tested. Database models, auth, donors, inventory and requests come in Milestone 4.

## Quick start (Docker)
```bash
cp .env.example .env        # then edit the passwords
docker compose up --build   # API at http://localhost:8000/docs
```

## Run tests locally
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
ruff check . && ruff format --check .
pytest --cov=app --cov-report=term-missing
```

## Layout
```
backend/app/domain/compatibility.py   educational ABO/Rh rules (DT-1, DT-2)
backend/app/config.py                 settings and policy parameters
backend/app/db.py                     SQLAlchemy engine and session
backend/alembic/                      migrations (first migration in Milestone 4)
backend/tests/unit/                   decision-table, boundary and equivalence tests
.github/workflows/ci.yml              lint + tests + coverage on every push
```

## Test markers
`unit` (no database), `integration` (uses PostgreSQL), `regression` (guards a fixed defect). Run one group with `pytest -m unit`.
