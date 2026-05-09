from celery import Celery
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

REDIS_URL = os.getenv("REDIS_URL") # Адрес Redis (брокер и бэкенд результатов)

celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.preprocess_task",   # модули, в которых находятся Celery-задачи
        "app.tasks.inference_task"    
    ]
)
# Маршрутизация задач по разным очередям
celery.conf.task_routes = {
    "app.tasks.preprocess_task.*": {"queue": "preprocess_queue"},
    "app.tasks.inference_task.*": {"queue": "inference_queue"}
}

celery.autodiscover_tasks(["app.tasks"])


from app.models.user import User
from app.models.prediction import Prediction
from app.models.promocodes import Promocode
from app.models.transaction import Transaction
from app.models.usages import PromocodeUsage
