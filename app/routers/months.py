from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db
from ..utils import get_prev_month, get_next_month

router = APIRouter(tags=["Months & Entries"])

@router.get("/months", response_model=List[schemas.MonthOut])
def get_all_months(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Get all months for the history list."""
    return db.query(models.Month).filter(models.Month.user_id == current_user.id).order_by(models.Month.month_key.desc()).all()

@router.get("/months/{month_key}", response_model=schemas.MonthOut)
def get_or_create_month(month_key: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Fetch a month and its entries. Auto-create if it doesn't exist."""
    month = db.query(models.Month).filter(models.Month.month_key == month_key, models.Month.user_id == current_user.id).first()

    if not month:
        # Check previous month for start balance
        prev_key = get_prev_month(month_key)
        prev_month = db.query(models.Month).filter(models.Month.month_key == prev_key, models.Month.user_id == current_user.id).first()
        start_bal = prev_month.end_bal if (prev_month and prev_month.is_closed) else 0.0
        
        month = models.Month(user_id=current_user.id, month_key=month_key, start_bal=start_bal)
        db.add(month)
        db.commit()
        db.refresh(month)
    return month

@router.put("/months/{month_key}", response_model=schemas.MonthOut)
def update_month(month_key: str, month_data: schemas.MonthUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Update month metadata (like milestone notes)."""
    month = db.query(models.Month).filter(models.Month.month_key == month_key, models.Month.user_id == current_user.id).first()
    if not month: raise HTTPException(status_code=404, detail="Month not found")
    
    if month_data.milestone_note is not None:
        month.milestone_note = month_data.milestone_note
    db.commit()
    db.refresh(month)
    return month

@router.post("/months/{month_key}/close", response_model=schemas.MonthOut)
def close_month(month_key: str, close_data: schemas.MonthClose, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Lock the month and carry the ending balance to the next month."""
    month = db.query(models.Month).filter(models.Month.month_key == month_key, models.Month.user_id == current_user.id).first()
    if not month: raise HTTPException(status_code=404, detail="Month not found")
    
    month.is_closed = True
    month.end_bal = close_data.end_bal

    # Force update the NEXT month's start balance
    next_key = get_next_month(month_key)
    next_month = db.query(models.Month).filter(models.Month.month_key == next_key, models.Month.user_id == current_user.id).first()
    if next_month:
        next_month.start_bal = month.end_bal
    else:
        next_month = models.Month(user_id=current_user.id, month_key=next_key, start_bal=month.end_bal)
        db.add(next_month)
        
    db.commit()
    db.refresh(month)
    return month

# --- ENTRIES ---
@router.post("/months/{month_key}/entries", response_model=schemas.MonthEntryOut)
def create_month_entry(month_key: str, entry: schemas.MonthEntryCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Add a new line item (expense/income/savings) to a month."""
    month = db.query(models.Month).filter(models.Month.month_key == month_key, models.Month.user_id == current_user.id).first()
    if not month: raise HTTPException(status_code=404, detail="Month not found")
    if month.is_closed: raise HTTPException(status_code=400, detail="Month is closed")

    new_entry = models.MonthEntry(**entry.model_dump(), month_id=month.id)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@router.put("/entries/{entry_id}", response_model=schemas.MonthEntryOut)
def update_month_entry(entry_id: str, entry_data: schemas.MonthEntryUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Update a specific line item's values or notes."""
    # Join with Month to ensure the current_user owns this entry
    entry = db.query(models.MonthEntry).join(models.Month).filter(models.MonthEntry.id == entry_id, models.Month.user_id == current_user.id).first()
    if not entry: raise HTTPException(status_code=404, detail="Entry not found")
    if entry.month.is_closed: raise HTTPException(status_code=400, detail="Cannot edit entries in a closed month.")

    if entry_data.forecast_val is not None: entry.forecast_val = entry_data.forecast_val
    if entry_data.actual_val is not None: entry.actual_val = entry_data.actual_val
    if entry_data.note is not None: entry.note = entry_data.note

    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_month_entry(entry_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Remove a line item."""
    entry = db.query(models.MonthEntry).join(models.Month).filter(models.MonthEntry.id == entry_id, models.Month.user_id == current_user.id).first()
    if not entry: raise HTTPException(status_code=404, detail="Entry not found")
    if entry.month.is_closed: raise HTTPException(status_code=400, detail="Month is closed")
    db.delete(entry)
    db.commit()