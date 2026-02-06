"""
Ленивая загрузка настроек.
"""
from backend.core.config import Settings

# Ленивая загрузка настроек
_settings_instance = None

def get_settings() -> Settings:
    """Возвращает экземпляр настроек (синглтон)."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance