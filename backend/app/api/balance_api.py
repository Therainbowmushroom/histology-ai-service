from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.transaction import Transaction
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/balance")

@router.get("/transactions")
def get_transactions(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.username == current_user).first()

    transactions = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    result = []
    for t in transactions:
        result.append({
            "amount": t.amount,
            "type": t.type,
            "description": t.description
        })
    return result


router = APIRouter(prefix="/balance")

@router.get("/me")
def get_balance(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    return {"username": user.username, "balance": user.balance}