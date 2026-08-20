"""Seed the database with demo users, accounts and transactions.

Run once before playing with the API:  python seed.py
"""
from app.database import Base, engine, SessionLocal
from app import models
from app.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(models.User).count() == 0:
    alice = models.User(username="alice", email="alice@finance.co",
                        password_hash=hash_password("password1"), is_admin=False)
    bob = models.User(username="bob", email="bob@finance.co",
                      password_hash=hash_password("hunter2"), is_admin=False)
    admin = models.User(username="admin", email="admin@finance.co",
                        password_hash=hash_password("admin"), is_admin=True)
    db.add_all([alice, bob, admin])
    db.commit()

    a1 = models.Account(name="Alice Checking", balance=1000.0, owner_id=alice.id)
    a2 = models.Account(name="Bob Payroll", balance=50000.0, owner_id=bob.id)
    db.add_all([a1, a2])
    db.commit()

    db.add_all([
        models.Transaction(account_id=a1.id, amount=-200.0, description="Office supplies"),
        models.Transaction(account_id=a2.id, amount=50000.0, description="Payroll deposit"),
    ])
    db.commit()
    print("Seeded: users alice/password1, bob/hunter2, admin/admin")
else:
    print("Already seeded.")

db.close()
