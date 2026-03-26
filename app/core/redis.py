import redis
from app.core.config import redis_settings

redis_client = redis.Redis(
    host=redis_settings.HOST,
    port=redis_settings.PORT,
    decode_responses=True
)
