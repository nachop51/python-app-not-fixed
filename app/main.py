from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Team API", debug=True)


@app.get("/")
def root():
    return {"service": "finance-api", "status": "ok"}


@app.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = models.User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_admin=payload.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login")
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(user), "token_type": "bearer"}


@app.post("/accounts", response_model=schemas.AccountOut)
def create_account(
    payload: schemas.AccountCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    account = models.Account(name=payload.name, balance=payload.balance, owner_id=user.id)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@app.get("/accounts/{account_id}", response_model=schemas.AccountOut)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.post("/transfer", response_model=schemas.TransactionOut)
def transfer(
    payload: schemas.TransferRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    src = db.query(models.Account).filter(models.Account.id == payload.from_account_id).first()
    dst = db.query(models.Account).filter(models.Account.id == payload.to_account_id).first()
    if not src or not dst:
        raise HTTPException(status_code=404, detail="Account not found")

    src.balance -= payload.amount
    dst.balance += payload.amount

    txn = models.Transaction(
        account_id=src.id,
        amount=-payload.amount,
        description=f"Transfer to account {dst.id}",
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


@app.get("/transactions/search")
def search_transactions(
    q: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    sql = f"SELECT id, account_id, amount, description FROM transactions WHERE description LIKE '%{q}%'"
    rows = db.execute(text(sql)).fetchall()
    return [dict(r._mapping) for r in rows]


@app.get("/admin/users", response_model=list[schemas.UserOut])
def list_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()
