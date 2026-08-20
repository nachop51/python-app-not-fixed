from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    password_hash: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class AccountCreate(BaseModel):
    name: str
    balance: float = 0.0


class AccountOut(BaseModel):
    id: int
    name: str
    balance: float
    owner_id: int

    class Config:
        from_attributes = True


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float


class TransactionOut(BaseModel):
    id: int
    account_id: int
    amount: float
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
