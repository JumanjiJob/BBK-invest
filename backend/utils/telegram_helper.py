"""
Помощник для работы с Telegram - создает экземпляры без циклических импортов.
"""
from backend.core.config import settings
from backend.integrations.telegram_sender import TelegramSender
from backend.integrations.email_sender import EmailSender
from backend.integrations.notification_service import NotificationService


def create_telegram_sender() -> TelegramSender:
    """Создает экземпляр TelegramSender."""
    return TelegramSender(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
        enabled=settings.telegram_enabled
    )


def create_email_sender() -> EmailSender:
    """Создает экземпляр EmailSender."""
    return EmailSender()


def create_notification_service() -> NotificationService:
    """Создает экземпляр NotificationService."""
    return NotificationService(
        telegram_sender=create_telegram_sender(),
        email_sender=create_email_sender()
    )