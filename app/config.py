from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class PostgresSettings(BaseSettings):
    DB: str
    USER: str
    PASSWORD: str

    model_config = SettingsConfigDict(env_prefix='POSTGRES_')


class JWTSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(env_prefix="JWT_")


class CelerySettings(BaseSettings):
    BROKER_URL: str
    RESULT_BACKEND: str

    model_config = SettingsConfigDict(env_prefix="CELERY_")


class Settings(BaseSettings):
    DATABASE_URL: str
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
