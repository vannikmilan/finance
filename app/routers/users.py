from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(tags=["Users & Auth"])

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, password_hash=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Find user
    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # 2. Verify password and check for rehash
    is_valid, needs_rehash = auth.verify_password(form_data.password, db_user.password_hash)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # 3. Transparently upgrade the hash if Argon2 parameters have changed and save to db
    if needs_rehash:
        db_user.password_hash = auth.get_password_hash(form_data.password)
        db.commit()

    # 4. Generate JWT
    access_token = auth.create_access_token(data={"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """Returns the profile of the currently logged-in user."""
    return current_user

@router.put("/me", response_model=schemas.UserOut)
def update_user_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Update the currently logged-in user's email or password."""
    # 1. Update Email (if provided)
    if user_update.email and user_update.email != current_user.email:
        #check if email is not taken
        existing_user = db.query(models.User).filter(models.User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email is already in use")
        current_user.email = user_update.email

    # 2. Update Password (if provided)
    if user_update.password:
        current_user.password_hash = auth.get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user