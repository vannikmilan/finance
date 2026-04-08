from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(tags=["Settings"])

# --- ACCOUNTS ---
@router.get("/accounts", response_model=List[schemas.AccountOut])
def get_accounts(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Get all accounts for the logged-in user."""
    return db.query(models.Account).filter(models.Account.user_id == current_user.id).all()

@router.post("/accounts", response_model=schemas.AccountOut)
def create_account(account: schemas.AccountCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Create a new account (e.g., 'Monobank', 'Cash')."""
    new_account = models.Account(**account.model_dump(), user_id=current_user.id)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

@router.put("/accounts/{account_id}", response_model=schemas.AccountOut)
def update_account(account_id: str, account_data: schemas.AccountUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Update an existing account's name or type."""
    account = db.query(models.Account).filter(models.Account.id == account_id, models.Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account.name = account_data.name
    account.type = account_data.type
    db.commit()
    db.refresh(account)
    return account


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Delete an account."""
    account = db.query(models.Account).filter(models.Account.id == account_id, models.Account.user_id == current_user.id).first()
    if not account: 
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()

# --- CATEGORIES ---
@router.get("/categories", response_model=List[schemas.CategoryOut])
def get_categories(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Get all categories for the logged-in user."""
    return db.query(models.Category).filter(models.Category.user_id == current_user.id).all()

@router.post("/categories", response_model=schemas.CategoryOut)
def create_category(category: schemas.CategoryCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Create a new category (e.g., 'Salary', 'Rent')."""
    new_category = models.Category(**category.model_dump(), user_id=current_user.id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.put("/categories/{category_id}", response_model=schemas.CategoryOut)
def update_category(category_id: str, category_data: schemas.CategoryUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Update an existing category's name or type."""
    category = db.query(models.Category).filter(models.Category.id == category_id, models.Category.user_id == current_user.id).first()
    if not category: 
        raise HTTPException(status_code=404, detail="Category not found")
    
    category.name = category_data.name
    category.type = category_data.type
    db.commit()
    db.refresh(category)
    return category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Delete a category."""
    category = db.query(models.Category).filter(models.Category.id == category_id, models.Category.user_id == current_user.id).first()
    if not category: 
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()