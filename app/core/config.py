from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class PostgresSettings(BaseSettings):
    DB: str
    USER: str
    PASSWORD: str
    model_config = SettingsConfigDict(env_prefix='POSTGRES_', env_file=BASE_DIR / ".env" , extra="ignore")


class JWTSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    model_config = SettingsConfigDict(env_prefix="JWT_", env_file=BASE_DIR / ".env" , extra="ignore")


class CelerySettings(BaseSettings):
    BROKER_URL: str
    RESULT_BACKEND: str
    model_config = SettingsConfigDict(env_prefix="CELERY_", env_file=BASE_DIR / ".env" , extra="ignore")


class Settings(BaseSettings):
    DATABASE_URL: str
    WEBHOOK_KEY: str
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8" , extra="ignore")


class RedisSettings(BaseSettings):
    HOST: str
    PORT: str
    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=BASE_DIR / ".env" , extra="ignore")

settings = Settings()
postgres_settings = PostgresSettings()
jwt_settings = JWTSettings()
celery_settings = CelerySettings()
redis_settings = RedisSettings()
