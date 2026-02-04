"""
Тесты диалоговой системы.
"""
import pytest
from backend.core.dialog_manager import dialog_manager


def test_individual_scenario():
    """Тест полного сценария для физического лица."""

    # Шаг 1: Начало диалога
    response1 = dialog_manager.process_user_message("", "")
    assert "Здравствуйте" in response1["message"]
    assert response1["step"] == "ask_loan_or_invest"

    session_id = response1["session_id"]

    # Шаг 2: Выбор "Займ"
    response2 = dialog_manager.process_user_message(session_id, "Займ")
    assert "физическое лицо" in response2["message"].lower()

    # Шаг 3: Выбор "Физическое лицо"
    response3 = dialog_manager.process_user_message(session_id, "Физическое лицо")
    assert "введите ваше имя" in response3["message"].lower()

    # Шаг 4: Ввод имени
    response4 = dialog_manager.process_user_message(session_id, "Иван Иванов")
    assert "залог" in response4["message"].lower()

    # Шаг 5: Ввод залога
    response5 = dialog_manager.process_user_message(session_id, "Toyota Camry, 2020 год")
    assert "сумма" in response5["message"].lower()

    # Шаг 6: Ввод суммы
    response6 = dialog_manager.process_user_message(session_id, "1000000")
    assert "цель" in response6["message"].lower()

    # Шаг 7: Ввод цели
    response7 = dialog_manager.process_user_message(session_id, "развитие бизнеса")
    assert "телефон" in response7["message"].lower()

    # Шаг 8: Ввод телефона
    response8 = dialog_manager.process_user_message(session_id, "89123456789")
    assert "проверьте данные" in response8["message"].lower()

    # Шаг 9: Подтверждение
    response9 = dialog_manager.process_user_message(session_id, "Да, отправить заявку")
    assert "отправлена" in response9["message"].lower()
    assert response9["completed"] is True


def test_business_scenario():
    """Тест сценария для бизнеса."""
    response1 = dialog_manager.process_user_message("", "")
    session_id = response1["session_id"]

    dialog_manager.process_user_message(session_id, "Займ")
    dialog_manager.process_user_message(session_id, "Бизнес")

    response = dialog_manager.process_user_message(session_id, "ООО 'Тестовая компания'")
    assert "сумма" in response["message"].lower()


def test_investor_scenario():
    """Тест сценария для инвестора."""
    response1 = dialog_manager.process_user_message("", "")
    session_id = response1["session_id"]

    response2 = dialog_manager.process_user_message(session_id, "Инвестировать")
    assert "введите ваше имя" in response2["message"].lower()


def test_validation():
    """Тест валидации данных."""
    response1 = dialog_manager.process_user_message("", "")
    session_id = response1["session_id"]

    # Неправильный выбор
    response = dialog_manager.process_user_message(session_id, "Неизвестный вариант")
    assert "выберите" in response["message"].lower()

    # Тестирование валидации телефона
    dialog_manager.process_user_message(session_id, "Займ")
    dialog_manager.process_user_message(session_id, "Физическое лицо")
    dialog_manager.process_user_message(session_id, "Иван")
    dialog_manager.process_user_message(session_id, "Авто")
    dialog_manager.process_user_message(session_id, "1000000")
    dialog_manager.process_user_message(session_id, "Цель")

    # Неправильный телефон
    response = dialog_manager.process_user_message(session_id, "123")
    assert "ошибка" in response["message"].lower() or "номер" in response["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])