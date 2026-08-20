# Finance Team API

Internal API for the finance team: users, accounts, transfers and transaction
search. FastAPI + SQLAlchemy (SQLite).

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```

Docs: http://127.0.0.1:8000/docs

Seeded logins: `alice/password1`, `bob/hunter2`, `admin/admin`.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/register` | Create a user |
| POST | `/login` | Get a JWT |
| POST | `/accounts` | Create an account |
| GET | `/accounts/{id}` | Read an account |
| POST | `/transfer` | Move money between accounts |
| GET | `/transactions/search?q=` | Search transactions |
| GET | `/admin/users` | List users |

## Tests

```bash
pytest
```

`tests/test_finance.py` covers the happy path. `tests/test_security.py`
holds pending cases for hardening still on the backlog.
