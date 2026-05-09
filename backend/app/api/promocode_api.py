from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.promocodes import Promocode
from app.models.usages import PromocodeUsage


router = APIRouter(
    prefix="/promocode",
    tags=["Promocodes"]
)


@router.post("/activate")
def activate_promocode(
    code: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # =========================
    # ищем пользователя
    # =========================

    user = db.query(User).filter(
        User.username == current_user
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # =========================
    # ищем промокод
    # =========================

    promocode = db.query(Promocode).filter(
        Promocode.code == code
    ).first()

    if not promocode:

        raise HTTPException(
            status_code=404,
            detail="Invalid promocode"
        )

    # =========================
    # проверка лимита использований
    # =========================

    if promocode.current_usages >= promocode.max_usages:

        raise HTTPException(
            status_code=400,
            detail="Promocode expired"
        )

    # =========================
    # проверяем, использовал ли пользователь
    # =========================

    used = db.query(PromocodeUsage).filter(
        PromocodeUsage.user_id == user.id,
        PromocodeUsage.promocode_id == promocode.id
    ).first()

    if used:

        raise HTTPException(
            status_code=400,
            detail="Promocode already used"
        )

    # =========================
    # создаём usage запись
    # =========================

    usage = PromocodeUsage(

        user_id=user.id,

        promocode_id=promocode.id
    )

    db.add(usage)

    # =========================
    # начисляем баланс
    # =========================

    user.balance += promocode.reward

    # =========================
    # увеличиваем счётчик
    # =========================

    promocode.current_usages += 1

    # =========================
    # сохраняем изменения
    # =========================

    db.commit()

    return {

        "message": "Promocode activated",
        "promocode": promocode.code,
        "reward": promocode.reward,
        "new_balance": user.balance
    }
