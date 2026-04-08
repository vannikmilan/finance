# app/routers/balances.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(tags=["Balances"])

@router.get("/balances", response_model=List[schemas.BalanceOut])
def get_all_balances(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Get all balance snapshots for the History dropdown."""
    return db.query(models.Balance).filter(models.Balance.user_id == current_user.id).order_by(models.Balance.date.desc()).all()

@router.get("/balances/{date}", response_model=schemas.BalanceOut)
def get_balance_by_date(date: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Fetch the specific balance snapshot for a day."""
    balance = db.query(models.Balance).filter(models.Balance.date == date, models.Balance.user_id == current_user.id).first()
    if not balance: raise HTTPException(status_code=404, detail="Balance not found")
    return balance

@router.post("/balances", response_model=schemas.BalanceOut)
def create_balance(balance_data: schemas.BalanceCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Save a new balance snapshot. Calculates the total_amount server-side."""

    # 1. Check if a balance for this date already exists to prevent duplicates
    existing = db.query(models.Balance).filter(models.Balance.date == balance_data.date, models.Balance.user_id == current_user.id).first()
    if existing: raise HTTPException(status_code=400, detail="Balance for date exists. Use PUT.")

    # 2. Calculate the total
    total_calculated = sum([acc.amount for acc in balance_data.accounts])
    
    # 3. Create the parent Balance record
    new_balance = models.Balance(user_id=current_user.id, date=balance_data.date, total_amount=total_calculated)
    db.add(new_balance)
    db.flush()

    # 4. Create the child BalanceAccount records
    for acc in balance_data.accounts:
        new_b_acc = models.BalanceAccount(balance_id=new_balance.id, account_id=acc.account_id, amount=acc.amount)
        db.add(new_b_acc)
        
    db.commit()
    db.refresh(new_balance)
    return new_balance

@router.put("/balances/{balance_id}", response_model=schemas.BalanceOut)
def update_balance(balance_id: str, balance_data: schemas.BalanceUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Update an existing balance snapshot (overwrites the old account breakdown)."""
    balance = db.query(models.Balance).filter(models.Balance.id == balance_id, models.Balance.user_id == current_user.id).first()
    if not balance: raise HTTPException(status_code=404, detail="Balance not found")

    # 1. Delete the old breakdown
    db.query(models.BalanceAccount).filter(models.BalanceAccount.balance_id == balance_id).delete()
    
    # 2. Recalculate total
    total_calculated = sum([acc.amount for acc in balance_data.accounts])
    balance.total_amount = total_calculated

    # 3. Insert the new breakdown
    for acc in balance_data.accounts:
        new_b_acc = models.BalanceAccount(balance_id=balance.id, account_id=acc.account_id, amount=acc.amount)
        db.add(new_b_acc)
        
    db.commit()
    db.refresh(balance)
    return balance

@router.delete("/balances/{balance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_balance(balance_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Delete a balance snapshot (cascades and deletes the child accounts too)."""
    balance = db.query(models.Balance).filter(models.Balance.id == balance_id, models.Balance.user_id == current_user.id).first()
    if not balance: raise HTTPException(status_code=404, detail="Balance not found")
    db.delete(balance)
    db.commit()