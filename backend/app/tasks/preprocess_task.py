from app.tasks.celery_app import celery
from ml.preprocessing import preprocess_slide
from app.tasks.inference_task import predict_task

from app.database import SessionLocal
from app.models.prediction import Prediction


@celery.task
def preprocess_task(prediction_id: int, file_path: str):

    """
    Задача Celery, выполняющая предобработку слайда.

    Args:
        prediction_id (int): ID записи Prediction в БД.
        file_path (str): Путь к загруженному SVS-файлу.

    Returns:
        None (результат сохраняется в БД через вызов predict_task).
    """
        
    db = SessionLocal()

    try:
        print("TASK STARTED", flush=True)
        # Получаем запись предсказания из БД

        prediction_db = db.query(Prediction).filter(
            Prediction.id == prediction_id
        ).first()

        print("PREDICTION FOUND", flush=True)
        
        # Обновляем статус на "PREPROCESSING"
        prediction_db.status = "PREPROCESSING"

        print("COMMITTING STATUS", flush=True)

        db.commit()

        print("START PREPROCESS", flush=True)
        print(f"FILE PATH: {file_path}", flush=True)
        # Режем слайд
        tile_dir = preprocess_slide(
            slide_path=file_path,
            output_dir="/storage/tiles"
        )

        print("PREPROCESS DONE", flush=True)
        print(f"TILE DIR: {tile_dir}", flush=True)

        print("SENDING TO INFERENCE", flush=True) # пошла отправка на предикт

        predict_task.delay(prediction_id, tile_dir)

        print("TASK SENT", flush=True)

    except Exception as e:  # В случае ошибки – откат транзакции и установка статуса FAILED

        print("ERROR OCCURRED", flush=True)
        print(str(e), flush=True)

        db.rollback()

        prediction_db = db.query(Prediction).filter(
            Prediction.id == prediction_id
        ).first()

        prediction_db.status = "FAILED"
        prediction_db.error_message = str(e)

        db.commit()

    finally:
        print("CLOSING DB", flush=True)
        db.close()