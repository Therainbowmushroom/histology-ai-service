import redis
import os

# Подключение к Redis через URL из переменной окружения
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def check_daily_limit(user_id: int):
    """
    Проверяет, не превысил ли пользователь дневной лимит запросов (10 в сутки).

    Args:
        user_id (int): ID пользователя.

    Returns:
        bool: True – если лимит не превышен (можно выполнить запрос),
              False – если лимит уже достигнут.
    """
    key = f"user:{user_id}:daily_requests"
    current = redis_client.get(key)
    if current is None:
        redis_client.setex(key, 86400, 1)

        return True

    current = int(current)

    if current >= 10:

        return False

    redis_client.incr(key)
    return True
