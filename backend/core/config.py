"""
Конфигурация приложения.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Основные настройки
    app_name: str = "BBKinvest AI Consultant"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "your-secret-key-here-change-in-production"

    # База данных
    database_url: str = "sqlite:///./database/bbk_ai.db"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_enabled: bool = True

    # Email
    email_enabled: bool = False
    email_host: str = ""
    email_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_from: str = ""
    email_to: str = "7504020@bk.ru"

    # Безопасность
    data_retention_hours: int = 24
    session_timeout_minutes: int = 15

    # CORS
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()