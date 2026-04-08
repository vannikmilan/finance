from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import calendar
from .. import models, schemas, auth
from ..database import get_db
from ..utils import get_prev_month

router = APIRouter(tags=["Summary"])

@router.get("/summary/now", response_model=schemas.NowSummaryOut)
def get_now_summary(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """
    Calculates the live 'Now' dashboard metrics.
    Free to Spend = (Cash Opening + Income) - (Savings + Expenses + Unexplained)
    """
    today = datetime.now().date()
    current_month_key = f"{today.year}-{today.month:02d}"

    # 1. Calculate Days Left in the Month
    _, last_day = calendar.monthrange(today.year, today.month)
    days_left = last_day - today.day
    # If it's the last day, avoid division by zero later by treating it as 1 day left
    effective_days_left = days_left if days_left > 0 else 1 
    
    # 2. Get the Current Month (and its entries)
    month = db.query(models.Month).filter(models.Month.month_key == current_month_key, models.Month.user_id == current_user.id).first()

    inc_total, sav_total, exp_total, start_bal = 0.0, 0.0, 0.0, 0.0

    if month:
        start_bal = month.start_bal or 0.0
        for entry in month.entries:
            category = db.query(models.Category).filter(models.Category.id == entry.category_id).first()
            if category:
                # Actual + Forecast = Total Expected for that line item
                line_total = entry.actual_val + entry.forecast_val
                if category.type == "income": inc_total += line_total
                elif category.type == "savings": sav_total += line_total
                elif category.type == "expense": exp_total += line_total

    # 3. Get the Latest Balance (To calculate Unexplained & Free to Spend)
    latest_balance = db.query(models.Balance).filter(models.Balance.user_id == current_user.id).order_by(models.Balance.date.desc()).first()

    # 4. Get the Opening Balance (from the last day of the PREVIOUS month)
    # We need this to determine how much "Cash" they started with.
    prev_month_key = get_prev_month(current_month_key)
    prev_month_last_day = f"{prev_month_key}-{calendar.monthrange(int(prev_month_key.split('-')[0]), int(prev_month_key.split('-')[1]))[1]}"
    
    opening_balance = db.query(models.Balance).filter(models.Balance.date <= prev_month_last_day, models.Balance.user_id == current_user.id).order_by(models.Balance.date.desc()).first()

    # Determine Cash Opening
    cash_opening = start_bal
    if opening_balance:
        cash_opening = sum([b_acc.amount for b_acc in opening_balance.balance_accounts if db.query(models.Account).filter(models.Account.id == b_acc.account_id).first().type == "cash"])

    # Determine Current Cash Total (from latest balance)
    current_cash_total = 0.0
    if latest_balance:
        current_cash_total = sum([b_acc.amount for b_acc in latest_balance.balance_accounts if db.query(models.Account).filter(models.Account.id == b_acc.account_id).first().type == "cash"])

    # 5. Calculate "Unexplained"
    # The mathematical logic from the prototype:
    # Unexplained = (Start Bal + Actual Income - Actual Expenses) - Latest Bal
    unexplained = 0.0
    if latest_balance and month:
        actual_inc = sum([e.actual_val for e in month.entries if db.query(models.Category).filter(models.Category.id == e.category_id).first().type == "income"])
        actual_exp = sum([e.actual_val for e in month.entries if db.query(models.Category).filter(models.Category.id == e.category_id).first().type == "expense"])
        expected_balance = start_bal + actual_inc - actual_exp
        unexplained = expected_balance - latest_balance.total_amount

    # 6. Calculate Free to Spend
    # Free = Cash Opening + All Expected Income - All Expected Savings - All Expected Expenses - Unexplained
    free_to_spend = cash_opening + inc_total - sav_total - exp_total - unexplained

    # 7. Calculate Per Day
    kpd = free_to_spend / effective_days_left

    return schemas.NowSummaryOut(
        month_key=current_month_key,
        days_left=days_left,
        cash_total=current_cash_total,
        inc_total=inc_total,
        sav_total=sav_total,
        exp_total=exp_total,
        unexplained=unexplained,
        free_to_spend=free_to_spend,
        kpd=kpd
    )