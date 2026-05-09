import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL из файла .env
DATABASE_URL = os.getenv("DATABASE_URL") 

# создаём движок подключение  к базе данных
engine = create_engine(DATABASE_URL)

# создаётся создатель сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# базовый класс для моделей
Base = declarative_base()


# dependency для FastAPI
def get_db():
    """
    Генератор (dependency) для FastAPI, предоставляющий сессию базы данных.
    
    Принимает:
        (нет аргументов, используется как зависимость FastAPI)
    
    Что делает:
        - Создаёт новую сессию базы данных с помощью SessionLocal.
        - Передаёт (yield) сессию в эндпоинт или другую зависимость.
        - После завершения работы эндпоинта автоматически закрывает сессию в блоке finally.
    
    Возвращает (yield):
        Session: Объект сессии SQLAlchemy, через который выполняются запросы к БД.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
