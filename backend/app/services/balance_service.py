from sqlalchemy.orm import Session
from app.models.user import User
from app.models.transaction import Transaction

def add_balance(
    db: Session,
    user: User,
    amount: int,
    transaction_type: str,
    description: str
):
    """
    Увеличивает баланс пользователя и создаёт запись о транзакции (пополнение).

    Args:
        db (Session): Сессия базы данных.
        user (User): Объект пользователя.
        amount (int): Сумма пополнения (положительное число).
        transaction_type (str): Тип транзакции (например, "PROMOCODE", "RECHARGE").
        description (str): Описание транзакции.
    """
    user.balance += amount
    transaction = Transaction(

        user_id=user.id,
        amount=amount,
        type=transaction_type,
        description=description
    )

    db.add(transaction)

    db.commit()


def subtract_balance(
    db: Session,
    user: User,
    amount: int,
    description: str
):
    """
    Уменьшает баланс пользователя (списание) и создаёт запись о транзакции.

    Args:
        db (Session): Сессия базы данных.
        user (User): Объект пользователя.
        amount (int): Сумма списания (положительное число, на которое уменьшается баланс).
        description (str): Описание транзакции.

    Raises:
        Exception: Если у пользователя недостаточно средств.
    """
    if user.balance < amount:

        raise Exception("Not enough balance")

    user.balance -= amount
    transaction = Transaction(

        user_id=user.id,
        amount=-amount,
        type="PREDICTION_PAYMENT",
        description=description
    )

    db.add(transaction)

    db.commit()

def subtract_balance(db, user, amount: int, description: str):
    if user.balance >= amount:
        user.balance -= amount
        transaction = Transaction(
            user_id=user.id,
            amount=-amount,
            type="debit",
            description=description
        )
        db.add(transaction)
        db.commit()
    else:
        raise ValueError("Insufficient balance")