import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr

    ADMIN_GROUP_ID: SecretStr

    DB_URL: SecretStr
    DB_USER: SecretStr
    DB_NAME: SecretStr
    DB_PASSWORD: SecretStr

    PG_ADMIN_PASSWORD: SecretStr

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        env_file_encoding="utf-8"
    )


config = Settings()
