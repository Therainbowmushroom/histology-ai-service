import logging
import os
from app.tasks.celery_app import celery
from ml.predict import predict_tiles
from app.database import SessionLocal
from app.models.prediction import Prediction

logger = logging.getLogger(__name__)

@celery.task
def predict_task(prediction_id: int, tile_dir: str):
    """
    Задача Celery, выполняющая предсказание по тайлам.

    Args:
        prediction_id (int): ID записи Prediction в БД.
        tile_dir (str): Путь к папке, содержащей тайлы (изображения).

    Returns:
        None (результат сохраняется в БД).
    """
    logger.info(f"=== INFERENCE TASK STARTED === id={prediction_id}, tile_dir={tile_dir}")
    db = SessionLocal()
    prediction_db = None
    try:
        # Проверка наличия директории с нарезанными слайдами
        if not os.path.exists(tile_dir):
            raise FileNotFoundError(f"Tile directory {tile_dir} does not exist")
        logger.info(f"Tile dir exists, files count: {len(os.listdir(tile_dir))}")
        # Получение записи предсказания
        prediction_db = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if not prediction_db:
            raise ValueError(f"Prediction {prediction_id} not found")
        logger.info(f"Prediction found, current status: {prediction_db.status}")
        # Обновление статуса на "INFERENCE"
        prediction_db.status = "INFERENCE"
        db.commit()
        logger.info("Status set to INFERENCE, calling predict_tiles...")

        result = predict_tiles(tile_dir)
        logger.info(f"predict_tiles returned: {result}")
        # Сохраняем предсказание в базу данных
        prediction_db.result = result["prediction"]
        prediction_db.confidence = result["confidence"]
        prediction_db.status = "SUCCESS"
        db.commit()
        logger.info("Task completed successfully, status SUCCESS")

    except Exception as e:
        logger.exception(f"!!! ERROR in inference task: {e}") # В случае ошибки – помечаем предсказание как FAILED
        if prediction_db:
            try:
                prediction_db.status = "FAILED"
                prediction_db.error_message = str(e)
                db.commit()
                logger.info(f"Saved FAILED status for prediction {prediction_id}")
            except Exception as db_err:
                logger.error(f"Failed to update DB: {db_err}")
    finally:
        db.close()
        logger.info("Database session closed")
