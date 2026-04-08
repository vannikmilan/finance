import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True) # Nullable for Google Auth later
    created_at = Column(DateTime, default=datetime.now)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False) # 'cash', 'savings', 'prepaid'

class Category(Base):
    __tablename__ = "categories"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False) # 'income', 'savings', 'expense'

class Month(Base):
    __tablename__ = "months"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    month_key = Column(String, nullable=False) # e.g., '2024-01'
    is_closed = Column(Boolean, default=False)
    start_bal = Column(Float, nullable=True)
    end_bal = Column(Float, nullable=True)
    milestone_note = Column(String, nullable=True)
    entries = relationship("MonthEntry", back_populates="month", cascade="all, delete-orphan")

class MonthEntry(Base):
    __tablename__ = "month_entries"
    id = Column(String, primary_key=True, default=generate_uuid)
    month_id = Column(String, ForeignKey("months.id"))
    category_id = Column(String, ForeignKey("categories.id"))
    forecast_val = Column(Float, default=0.0)
    actual_val = Column(Float, default=0.0)
    note = Column(String, nullable=True)
    month = relationship("Month", back_populates="entries")

class Balance(Base):
    __tablename__ = "balances"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    date = Column(String, nullable=False) # 'YYYY-MM-DD'
    total_amount = Column(Float, default=0.0)
    balance_accounts = relationship("BalanceAccount", back_populates="balance", cascade="all, delete-orphan")

class BalanceAccount(Base):
    __tablename__ = "balance_accounts"
    id = Column(String, primary_key=True, default=generate_uuid)
    balance_id = Column(String, ForeignKey("balances.id"))
    account_id = Column(String, ForeignKey("accounts.id"))
    amount = Column(Float, default=0.0)
    balance = relationship("Balance", back_populates="balance_accounts")