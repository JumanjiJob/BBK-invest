"""
Главный менеджер диалоговых состояний.
"""
from typing import Dict, Tuple, Optional, Any
from .models import DialogState
from .session_store import session_store
from .scenario_manager import scenario_manager, DialogStep


class DialogStateManager:
    """Координатор всех компонентов диалоговой системы."""

    def __init__(self):
        self.scenario_manager = scenario_manager

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

        # Обновляем состояние сессии
        session.current_step = next_step.value

        if next_step == DialogStep.COMPLETED:
            session.completed = True
            # Здесь позже добавим отправку в Telegram

        # Формируем ответное сообщение
        message_text = self.scenario_manager.get_message(next_step, session.collected_data)
        options = self.scenario_manager.get_options(next_step)

        # Сохраняем обновлённую сессию
        session_store.update_session(session_id, {
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

    def get_dialog_state(self, session_id: str) -> Optional[DialogState]:
        """Получает текущее состояние диалога."""
        return session_store.get_session(session_id)

    def reset_dialog(self, session_id: str) -> str:
        """Сбрасывает диалог и возвращает новый session_id."""
        session_store.delete_session(session_id)
        return session_store.create_session()


# Глобальный экземпляр менеджера
dialog_manager = DialogStateManager()