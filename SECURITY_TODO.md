# Security TODO

Vulnerabilities found in scan. Check off as fixed. Most have a failing `xfail`
test in `tests/test_security.py` — flip it green (remove `xfail`) when done.

## Critical

- [ ] **SQL injection** — `app/main.py:106` — search `q` interpolated into raw SQL. Parameterize with bound `:pat`. _(test: `test_search_is_not_sql_injectable`)_
- [ ] **Privilege escalation on register** — `app/main.py:34`, `app/schemas.py:10` — `is_admin` trusted from request body. Drop from `UserCreate`, hardcode `False`. _(test: `test_cannot_self_register_as_admin`)_
- [ ] **Admin endpoint unauthenticated** — `app/main.py:111` `/admin/users` — no auth, no role check, leaks all users + hashes. Add auth dep + `is_admin` check. _(test: `test_admin_endpoint_requires_admin`)_
- [ ] **IDOR — account read** — `app/main.py:69` `/accounts/{id}` — no owner check, any user reads any account. Enforce `owner_id == user.id` (or admin). _(test: `test_cannot_read_other_users_account`)_
- [ ] **IDOR — transfer** — `app/main.py:81` `/transfer` — source account owner never verified, drains others' accounts. Check `src.owner_id == user.id`. _(test: `test_cannot_transfer_from_others_account`)_

## High

- [ ] **Password hash exposed** — `app/schemas.py:18` — `UserOut.password_hash` serialized on `/register` + `/admin/users`. Remove field. _(test: `test_password_hash_not_exposed`)_
- [ ] **MD5 password hashing** — `app/auth.py:16` — unsalted MD5, trivially cracked. Switch to bcrypt/argon2.
- [ ] **Hardcoded JWT secret** — `app/auth.py:11` — secret in source, anyone forges admin tokens. Load from env, fail if unset.
- [ ] **No token expiry** — `app/auth.py:23` — JWT has no `exp`, stolen token valid forever. Add + verify `exp`.

## Medium

- [ ] **Transfer negative / overdraft** — `app/main.py:86` — negative amount reverses direction, no balance check. Reject `amount <= 0` and `src.balance < amount`. _(test: `test_transfer_rejects_negative_and_overdraft`)_
- [ ] **Money as float** — `app/models.py:25,36` — `Float` balances drift off cent. Use `Numeric`/integer cents. _(test: `test_money_has_no_float_drift`)_
- [ ] **`debug=True` in prod** — `app/main.py:16` — leaks stack traces. Off / env-gated.
- [ ] **Token error leaks internals** — `app/auth.py:43` — `f"Token error: {e}"` returned to client. Generic message.
- [ ] **Transfer not atomic / no row lock** — `app/main.py:86-95` — concurrent transfers race. `SELECT..FOR UPDATE` on a real DB (SQLite masks it now).

---
Tally: 5 Critical, 4 High, 5 Medium. 8 have failing `xfail` tests in `tests/test_security.py`.
