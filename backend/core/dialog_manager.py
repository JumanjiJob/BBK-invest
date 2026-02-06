"""
Главный менеджер диалоговых состояний.
"""
from typing import Dict, Tuple, Optional, Any
from .models import DialogState
from .session_store import session_store
from .scenario_manager import scenario_manager, DialogStep
import logging

logger = logging.getLogger(__name__)


class DialogStateManager:
    """Координатор всех компонентов диалоговой системы."""

    def __init__(self):
        self.scenario_manager = scenario_manager
        self._notification_service = None

    @property
    def notification_service(self):
        """Ленивая загрузка notification_service."""
        if self._notification_service is None:
            from backend.utils.telegram_helper import create_notification_service
            self._notification_service = create_notification_service()
        return self._notification_service

    def process_user_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Обрабатывает сообщение пользователя и возвращает ответ."""

        # Получаем или создаём сессию
        session = session_store.get_session(session_id)
        if not session:
            session_id = session_store.create_session()
            session = session_store.get_session(session_id)

        # Если диалог завершён, начинаем новый
        if session.completed:
            session_store.delete_session(session_id)
            session_id = session_store.create_session()
            session = session_store.get_session(session_id)

        # Определяем следующий шаг
        next_step, updates = self.scenario_manager.get_next_step(
            DialogStep(session.current_step),
            user_message,
            session.collected_data
        )

        # Обрабатываем ошибки валидации
        if "error" in updates:
            response = {
                "message": f"❌ {updates['error']}\n\n{self.scenario_manager.get_message(DialogStep(session.current_step))}",
                "options": self.scenario_manager.get_options(DialogStep(session.current_step)),
                "session_id": session_id,
                "step": session.current_step
            }
            return response

        # Если нужно сбросить данные
        if updates.get("reset"):
            session.collected_data = {}

        # Обновляем данные сессии
        if updates:
            session.collected_data.update({k: v for k, v in updates.items()
                                           if k not in ["error", "reset"]})

            # Если в обновлениях есть user_type, обновляем и поле сессии
            if "user_type" in updates:
                session.user_type = updates["user_type"]

        # Обновляем состояние сессии
        session.current_step = next_step.value

        # ОБРАБОТКА ЗАВЕРШЕНИЯ ДИАЛОГА
        if next_step == DialogStep.COMPLETED:
            session.completed = True

            # Отправляем уведомление о заявке
            self._send_application_notification(session.user_type, session.collected_data, session_id)

        # Формируем ответное сообщение
        message_text = self.scenario_manager.get_message(next_step, session.collected_data)
        options = self.scenario_manager.get_options(next_step)

        # Сохраняем обновлённую сессию
        session_store.update_session(session_id, {
            "user_type": session.user_type,  # Обновляем тип пользователя
            "current_step": session.current_step,
            "collected_data": session.collected_data,
            "completed": session.completed
        })

        return {
            "message": message_text,
            "options": options,
            "session_id": session_id,
            "step": session.current_step,
            "completed": session.completed
        }

    def _send_application_notification(self, user_type, collected_data: Dict[str, Any], session_id: str):
        """Отправляет уведомление о новой заявке."""
        try:
            # Подготавливаем данные для отправки
            application_data = collected_data.copy()
            application_data['session_id'] = session_id

            # Конвертируем UserType enum в строку
            user_type_str = user_type.value if hasattr(user_type, 'value') else str(user_type)

            # Отправляем через notification service
            success = self.notification_service.send_application_notification(
                user_type_str, application_data
            )

            if success:
                logger.info(f"Уведомление о заявке отправлено. Session: {session_id}")
            else:
                logger.error(f"Не удалось отправить уведомление о заявке. Session: {session_id}")

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления: {str(e)}", exc_info=True)

    def get_dialog_state(self, session_id: str) -> Optional[DialogState]:
        """Получает текущее состояние диалога."""
        return session_store.get_session(session_id)

    def reset_dialog(self, session_id: str) -> str:
        """Сбрасывает диалог и возвращает новый session_id."""
        session_store.delete_session(session_id)
        return session_store.create_session()


# Глобальный экземпляр менеджера
dialog_manager = DialogStateManager()