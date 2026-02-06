"""
Пакет интеграций для отправки уведомлений.
"""

# Экспортируем только классы, а не экземпляры
from .telegram_sender import TelegramSender
from .email_sender import EmailSender
from .notification_service import NotificationService

# Не создаем экземпляры здесь!