import sys
import os
from datetime import datetime

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app import models, auth

def seed_db():
    print("Creating tables...")
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("Checking for existing test user...")
    user = db.query(models.User).filter(models.User.email == "test@example.com").first()
    
    if user:
        print("Test user already exists. Dropping database and recreating for a fresh seed...")
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
    
    # 1. Create User
    print("Creating Test User: test@example.com / password123")
    hashed_pw = auth.get_password_hash("password123")
    user = models.User(email="test@example.com", password_hash=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)

    # 2. Create Accounts
    print("Creating Accounts...")
    acc_mono = models.Account(user_id=user.id, name="Monobank", type="cash")
    acc_cash = models.Account(user_id=user.id, name="Cash", type="cash")
    acc_jar = models.Account(user_id=user.id, name="Mono Banka", type="savings")
    db.add_all([acc_mono, acc_cash, acc_jar])
    db.commit()

    # 3. Create Categories
    print("Creating Categories...")
    cat_salary = models.Category(user_id=user.id, name="Salary", type="income")
    cat_rent = models.Category(user_id=user.id, name="Rent", type="expense")
    cat_food = models.Category(user_id=user.id, name="Food", type="expense")
    db.add_all([cat_salary, cat_rent, cat_food])
    db.commit()

    # 4. Create Current Month (e.g., this month)
    today = datetime.now()
    current_month_key = f"{today.year}-{today.month:02d}"
    print(f"Creating Month data for {current_month_key}...")
    
    month = models.Month(user_id=user.id, month_key=current_month_key, start_bal=10.0) # Started with 10k
    db.add(month)
    db.commit()
    db.refresh(month)

    # 5. Add Entries to Month
    entry1 = models.MonthEntry(month_id=month.id, category_id=cat_salary.id, forecast_val=50.0, actual_val=50.0, note="Monthly Salary")
    entry2 = models.MonthEntry(month_id=month.id, category_id=cat_rent.id, forecast_val=20.0, actual_val=20.0, note="Apartment")
    entry3 = models.MonthEntry(month_id=month.id, category_id=cat_food.id, forecast_val=15.0, actual_val=5.0, note="Groceries so far")
    db.add_all([entry1, entry2, entry3])
    db.commit()

    # 6. Create a Balance Snapshot (Recorded today)
    print("Creating a Balance Snapshot...")
    balance = models.Balance(user_id=user.id, date=today.strftime("%Y-%m-%d"), total_amount=35.0)
    db.add(balance)
    db.commit()
    db.refresh(balance)

    # Breakdown of that balance
    b_acc1 = models.BalanceAccount(balance_id=balance.id, account_id=acc_mono.id, amount=30.0)
    b_acc2 = models.BalanceAccount(balance_id=balance.id, account_id=acc_cash.id, amount=5.0)
    db.add_all([b_acc1, b_acc2])
    db.commit()

    print("✅ Database successfully seeded!")
    db.close()

if __name__ == "__main__":
    seed_db()