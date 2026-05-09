from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.api.auth_api import router as auth_router
from app.api.prediction_api import router as prediction_router
from app.api.promocode_api import router as promocode_router
from app.api.balance_api import router as balance_router

# создаём таблицы в базе данных согласно моделям (если их ещё нет)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# подключаем роутеры с префиксами, определёнными внутри каждого модуля
app.include_router(auth_router)
app.include_router(prediction_router)
app.include_router(promocode_router)

# добавляем CORS middleware для разрешения кросс-доменных запросов с любых источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # разрешённые источники (все)
    allow_credentials=True,  # разрешить отправку куки/авторизационных заголовков
    allow_methods=["*"],     
    allow_headers=["*"],
)
app.include_router(balance_router)
