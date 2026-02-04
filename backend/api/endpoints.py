"""
API endpoints для чат-виджета.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Используем относительные импорты
from ..core.dialog_manager import dialog_manager

router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    """Модель запроса от чат-виджета."""
    session_id: Optional[str] = None
    message: Optional[str] = None
    action: Optional[str] = None  # Для действий типа "restart"


class ChatResponse(BaseModel):
    """Модель ответа чат-виджета."""
    message: str
    options: List[str] = []
    session_id: str
    step: str
    completed: bool = False


@router.post("/chat", response_model=ChatResponse)
async def process_chat_message(request: ChatRequest):
    """
    Обрабатывает сообщение пользователя и возвращает ответ ИИ.
    """
    try:
        # Обработка действия перезапуска
        if request.action == "restart" and request.session_id:
            new_session_id = dialog_manager.reset_dialog(request.session_id)
            request.session_id = new_session_id
            request.message = ""

        # Обработка сообщения
        result = dialog_manager.process_user_message(
            request.session_id or "",
            request.message or ""
        )

        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки сообщения: {str(e)}")


@router.get("/chat/state/{session_id}")
async def get_chat_state(session_id: str):
    """
    Получает текущее состояние диалога (для отладки).
    """
    state = dialog_manager.get_dialog_state(session_id)

    if not state:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    return {
        "session_id": state.session_id,
        "step": state.current_step,
        "user_type": state.user_type,
        "collected_data": state.collected_data,
        "completed": state.completed
    }


@router.post("/chat/quick-start")
async def quick_start_dialog(option: str):
    """
    Быстрый старт диалога с выбранной опцией.
    Используется для кнопок на сайте.
    """
    # Создаём новую сессию
    result = dialog_manager.process_user_message("", "")

    # Эмулируем выбор пользователя
    if option == "individual":
        result = dialog_manager.process_user_message(result["session_id"], "Займ")
        result = dialog_manager.process_user_message(result["session_id"], "Физическое лицо")
    elif option == "business":
        result = dialog_manager.process_user_message(result["session_id"], "Займ")
        result = dialog_manager.process_user_message(result["session_id"], "Бизнес")
    elif option == "investor":
        result = dialog_manager.process_user_message(result["session_id"], "Инвестировать")

    return ChatResponse(**result)