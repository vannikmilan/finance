from pydantic import BaseModel, EmailStr
from typing import List, Optional

# Auth Schemas & User
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: str
    email: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# --- Accounts ---
class AccountBase(BaseModel):
    name: str
    type: str # 'cash', 'savings', 'prepaid'

class AccountCreate(AccountBase):
    pass

class AccountOut(AccountBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True

class AccountUpdate(BaseModel):
    name: str
    type: str

# --- Categories ---
class CategoryBase(BaseModel):
    name: str
    type: str # 'income', 'savings', 'expense'

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True

class CategoryUpdate(BaseModel):
    name: str
    type: str

# --- Month Entries ---
class MonthEntryBase(BaseModel):
    category_id: str
    forecast_val: float = 0.0
    actual_val: float = 0.0
    note: Optional[str] = None

class MonthEntryCreate(MonthEntryBase):
    pass

class MonthEntryUpdate(BaseModel):
    forecast_val: Optional[float] = None
    actual_val: Optional[float] = None
    note: Optional[str] = None

class MonthEntryOut(MonthEntryBase):
    id: str
    month_id: str

    class Config:
        from_attributes = True

# --- Months ---
class MonthUpdate(BaseModel):
    milestone_note: Optional[str] = None

class MonthClose(BaseModel):
    end_bal: float

class MonthOut(BaseModel):
    id: str
    user_id: str
    month_key: str
    is_closed: bool
    start_bal: Optional[float]
    end_bal: Optional[float]
    milestone_note: Optional[str]
    entries: List[MonthEntryOut] = [] # Nests the entries automatically

    class Config:
        from_attributes = True

# --- Balance Accounts (The breakdown per account) ---
class BalanceAccountBase(BaseModel):
    account_id: str
    amount: float

class BalanceAccountCreate(BalanceAccountBase):
    pass

class BalanceAccountOut(BalanceAccountBase):
    id: str
    balance_id: str

    class Config:
        from_attributes = True

# --- Balances (The daily snapshot) ---
class BalanceCreate(BaseModel):
    date: str # 'YYYY-MM-DD'
    accounts: List[BalanceAccountCreate] # Array of account amounts sent by React

class BalanceUpdate(BaseModel):
    # Only need to send the updated array of accounts
    accounts: List[BalanceAccountCreate]

class BalanceOut(BaseModel):
    id: str
    user_id: str
    date: str
    total_amount: float
    balance_accounts: List[BalanceAccountOut] = [] # Nests the breakdown automatically

    class Config:
        from_attributes = True

# --- Summary / Now Calculator ---
class NowSummaryOut(BaseModel):
    month_key: str
    days_left: int
    cash_total: float
    inc_total: float
    sav_total: float
    exp_total: float
    unexplained: float
    free_to_spend: float
    kpd: float # Thousands per day