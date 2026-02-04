"""
Хранилище сессий в памяти с очисткой по таймауту.
"""
import uuid
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

from .config import settings
from .models import DialogState

class SessionStore:
    """Хранилище диалоговых сессий в оперативной памяти."""

    def __init__(self):
        self.sessions: Dict[str, DialogState] = {}
        self.timeout_minutes = settings.session_timeout_minutes

    def create_session(self) -> str:
        """Создаёт новую сессию и возвращает её ID."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = DialogState(
            session_id=session_id,
            user_type=None,
            current_step="welcome",
            collected_data={},
            completed=False
        )
        return session_id

    def get_session(self, session_id: str) -> Optional[DialogState]:
        """Получает сессию по ID, проверяя таймаут."""
        if session_id not in self.sessions:
            return None

        # Здесь можно добавить проверку таймаута по времени создания
        # Пока просто возвращаем сессию
        return self.sessions[session_id]

    def update_session(self, session_id: str, updates: dict):
        """Обновляет данные сессии."""
        if session_id in self.sessions:
            for key, value in updates.items():
                setattr(self.sessions[session_id], key, value)

    def delete_session(self, session_id: str):
        """Удаляет сессию."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_expired(self):
        """Очищает просроченные сессии."""
        current_time = datetime.now()
        expired = []

        for session_id, session in self.sessions.items():
            # Здесь добавим логику проверки времени
            pass

        for session_id in expired:
            del self.sessions[session_id]


# Глобальный экземпляр хранилища
session_store = SessionStore()