"""
Общий сервис для отправки уведомлений.
"""
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис управления уведомлениями (Telegram + резервный Email)."""

    def __init__(self, telegram_sender=None, email_sender=None):
        self.telegram_sender = telegram_sender
        self.email_sender = email_sender
        self.notification_history = []  # Для логов

    def send_application_notification(self, user_type: str,
                                    application_data: Dict[str, Any]) -> bool:
        """
        Отправляет уведомление о новой заявке.
        Сначала пробует Telegram, в случае ошибки - отправляет на Email.

        Args:
            user_type: Тип пользователя ('individual', 'business', 'investor')
            application_data: Данные заявки

        Returns:
            bool: True если хотя бы одна отправка успешна
        """
        # Добавляем timestamp и session_id если их нет
        if 'timestamp' not in application_data:
            application_data['timestamp'] = datetime.now().isoformat()
        if 'session_id' not in application_data:
            application_data['session_id'] = 'unknown'

        success = False
        errors = []

        # Пытаемся отправить в Telegram
        if self.telegram_sender and self.telegram_sender.enabled:
            try:
                telegram_success = self.telegram_sender.send_application(
                    user_type, application_data
                )

                if telegram_success:
                    logger.info(f"Заявка успешно отправлена в Telegram")
                    success = True
                    self._log_notification("telegram", user_type, application_data, True)
                else:
                    errors.append("Telegram отправка не удалась")
                    self._log_notification("telegram", user_type, application_data, False)
            except Exception as e:
                errors.append(f"Telegram ошибка: {str(e)}")
                logger.error(f"Ошибка отправки в Telegram: {str(e)}")
                self._log_notification("telegram", user_type, application_data, False)

        # Если Telegram не сработал, пробуем Email (если доступен)
        if not success and self.email_sender and self.email_sender.enabled:
            try:
                email_success = self.email_sender.send_application(
                    user_type, application_data
                )

                if email_success:
                    logger.info(f"Заявка успешно отправлена на Email")
                    success = True
                    self._log_notification("email", user_type, application_data, True)
                else:
                    errors.append("Email отправка не удалась")
                    self._log_notification("email", user_type, application_data, False)
            except Exception as e:
                errors.append(f"Email ошибка: {str(e)}")
                logger.error(f"Ошибка отправки на Email: {str(e)}")
                self._log_notification("email", user_type, application_data, False)

        # Логируем итог
        if success:
            logger.info(f"Уведомление о заявке отправлено. Тип: {user_type}")
        else:
            logger.error(f"Не удалось отправить уведомление. Ошибки: {'; '.join(errors)}")

        return success

    def test_connections(self) -> Dict[str, bool]:
        """Тестирует соединения с Telegram и Email."""
        results = {
            'telegram': False,
            'email': False
        }

        # Тест Telegram
        if self.telegram_sender and self.telegram_sender.enabled:
            try:
                telegram_info = self.telegram_sender.get_bot_info()
                if telegram_info and telegram_info.get('ok'):
                    results['telegram'] = True
                    logger.info(f"Telegram подключен")
                else:
                    logger.error("Telegram: Не удалось получить информацию о боте")
            except Exception as e:
                logger.error(f"Telegram тест не пройден: {str(e)}")

        # Тест Email (если доступен)
        if self.email_sender and self.email_sender.enabled:
            try:
                results['email'] = self.email_sender.send_test_email()
                if results['email']:
                    logger.info("Email подключен")
                else:
                    logger.error("Email: Не удалось отправить тестовое письмо")
            except Exception as e:
                logger.error(f"Email тест не пройден: {str(e)}")
        else:
            logger.info("Email отключен в настройках")

        return results

    def _log_notification(self, channel: str, user_type: str,
                         data: Dict[str, Any], success: bool):
        """Логирует отправку уведомления."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'channel': channel,
            'user_type': user_type,
            'session_id': data.get('session_id', 'unknown'),
            'success': success,
            'data_summary': {
                'name': data.get('name') or data.get('company_name', 'unknown'),
                'phone': data.get('phone', 'unknown')[-4:] if data.get('phone') else 'unknown'
            }
        }

        self.notification_history.append(log_entry)

        # Ограничиваем историю последними 100 записями
        if len(self.notification_history) > 100:
            self.notification_history = self.notification_history[-100:]

    def get_notification_stats(self) -> Dict[str, Any]:
        """Возвращает статистику отправленных уведомлений."""
        if not self.notification_history:
            return {'total': 0, 'success': 0, 'failed': 0}

        total = len(self.notification_history)
        success = sum(1 for entry in self.notification_history if entry['success'])

        return {
            'total': total,
            'success': success,
            'failed': total - success,
            'last_10': self.notification_history[-10:] if total > 10 else self.notification_history
        }