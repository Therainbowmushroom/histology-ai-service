from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

import uuid
import shutil

from app.database import get_db
from app.models.prediction import Prediction
from app.tasks.preprocess_task import preprocess_task
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.services.balance_service import subtract_balance

router = APIRouter(
    prefix="/prediction"
)


PREDICTION_COST = 100   # стоимость одного предсказания

@router.post("/upload")
async def upload_svs(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)   # получаем имя пользователя из JWT
):
    # 1. Находим пользователя в БД
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Проверяем, хватает ли баланса
    if user.balance < PREDICTION_COST:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # 3. Списываем средства
    subtract_balance(db, user, PREDICTION_COST, "SVS prediction")

    # 4. Проверка расширения файла
    if not file.filename.endswith(".svs"):
        raise HTTPException(status_code=400, detail="Invalid file format")

    # 5. Сохраняем файл
    unique_name = f"{uuid.uuid4()}.svs"
    save_path = f"/storage/uploads/{unique_name}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 6. Создаём запись Prediction
    prediction = Prediction(
        original_filename=file.filename,
        file_path=save_path,
        status="PENDING"
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    # 7. Запускаем фоновую задачу
    preprocess_task.delay(prediction.id, save_path)

    return {
        "prediction_id": prediction.id,
        "status": "queued"
    }

@router.get("/{prediction_id}")
def get_prediction_status(
    prediction_id: int,
    db: Session = Depends(get_db)
):

    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id
    ).first()

    if not prediction:

        raise HTTPException(
            status_code=404,
            detail="Prediction not found"
        )

    return {

        "id": prediction.id,
        "status": prediction.status,
        "result": prediction.result,
        "confidence": prediction.confidence,
        "error": prediction.error_message
    }
