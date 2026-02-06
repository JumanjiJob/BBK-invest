"""
Отправка заявок в Telegram через Bot API.
"""
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TelegramSender:
    """Класс для отправки уведомлений в Telegram."""

    def __init__(self, bot_token: str, chat_id: str, enabled: bool = True):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = enabled
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        if not self.enabled:
            logger.warning("Отправка в Telegram отключена в настройках")

    def send_application(self, user_type: str, application_data: Dict[str, Any]) -> bool:
        """
        Отправляет заявку в Telegram.

        Args:
            user_type: Тип пользователя ('individual', 'business', 'investor')
            application_data: Данные заявки

        Returns:
            bool: True если отправка успешна, False в противном случае
        """
        if not self.enabled:
            logger.warning("Telegram отключен, пропускаем отправку")
            return False

        try:
            # Импортируем здесь, чтобы избежать циклических импортов
            from backend.core.application_formatter import ApplicationFormatter

            # Форматируем сообщение
            message = ApplicationFormatter.format_application(user_type, application_data)

            # Отправляем в Telegram
            response = self._send_message(message)

            if response and response.get('ok'):
                logger.info(f"Заявка успешно отправлена в Telegram. Chat ID: {self.chat_id}")
                return True
            else:
                error_msg = response.get('description', 'Неизвестная ошибка') if response else 'Нет ответа от Telegram API'
                logger.error(f"Ошибка отправки в Telegram: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"Ошибка при отправке в Telegram: {str(e)}", exc_info=True)
            return False

    def send_test_message(self, text: str = "Тестовое сообщение от ИИ-консультанта BBKinvest") -> bool:
        """Отправляет тестовое сообщение для проверки подключения."""
        if not self.enabled:
            logger.warning("Telegram отключен")
            return False

        try:
            response = self._send_message(text)
            if response and response.get('ok'):
                logger.info("Тестовое сообщение отправлено успешно")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка отправки тестового сообщения: {str(e)}")
            return False

    def _send_message(self, text: str) -> Optional[Dict[str, Any]]:
        """Отправляет сообщение через Telegram Bot API."""
        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Telegram API: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"Ошибка парсинга ответа от Telegram: {str(e)}")
            return None

    def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """Получает информацию о боте."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/getMe"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка получения информации о боте: {str(e)}")
            return None