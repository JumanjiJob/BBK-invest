"""
Тестирование интеграции с Telegram API.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.integrations.telegram_sender import TelegramSender
from backend.integrations.email_sender import EmailSender
from backend.integrations.notification_service import NotificationService
from backend.core.models import UserType


def test_telegram_sender_initialization():
    """Тест инициализации TelegramSender."""
    sender = TelegramSender()
    assert hasattr(sender, 'bot_token')
    assert hasattr(sender, 'chat_id')
    assert hasattr(sender, 'enabled')


@patch('requests.post')
def test_send_message_success(mock_post):
    """Тест успешной отправки сообщения."""
    # Настраиваем мок
    mock_response = Mock()
    mock_response.json.return_value = {'ok': True, 'result': {'message_id': 123}}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    sender = TelegramSender()
    sender.bot_token = 'test_token'
    sender.chat_id = 'test_chat'
    sender.enabled = True

    result = sender.send_test_message("Тестовое сообщение")
    assert result is True


@patch('requests.post')
def test_send_message_failure(mock_post):
    """Тест неудачной отправки сообщения."""
    mock_post.side_effect = Exception("Ошибка сети")

    sender = TelegramSender()
    sender.bot_token = 'test_token'
    sender.chat_id = 'test_chat'
    sender.enabled = True

    result = sender.send_test_message("Тестовое сообщение")
    assert result is False


def test_application_formatter():
    """Тест форматирования заявок."""
    from backend.core.application_formatter import ApplicationFormatter

    # Тест для физического лица
    individual_data = {
        'name': 'Иван Иванов',
        'collateral': 'Toyota Camry 2020',
        'amount': 1000000,
        'purpose': 'развитие бизнеса',
        'phone': '89123456789'
    }

    formatted = ApplicationFormatter.format_individual_application(individual_data)
    assert 'Иван Иванов' in formatted
    assert 'Toyota Camry' in formatted
    assert '1,000,000 руб' in formatted

    # Тест для бизнеса
    business_data = {
        'company_name': 'ООО Тест',
        'amount': 5000000,
        'collateral': 'Офисное помещение',
        'purpose': 'развитие производства',
        'phone': '89223456789'
    }

    formatted = ApplicationFormatter.format_business_application(business_data)
    assert 'ООО Тест' in formatted
    assert '5,000,000 руб' in formatted
    assert 'Заемщик (бизнес)' in formatted

    # Тест для инвестора
    investor_data = {
        'name': 'Екатерина',
        'investment_amount': 3000000,
        'term_months': 12,
        'investment_goal': 'пассивный доход',
        'phone': '89323456789'
    }

    formatted = ApplicationFormatter.format_investor_application(investor_data)
    assert 'Екатерина' in formatted
    assert '3,000,000 руб' in formatted
    assert '12 месяцев' in formatted


def test_notification_service():
    """Тест сервиса уведомлений."""
    service = NotificationService()

    # Проверяем наличие необходимых методов
    assert hasattr(service, 'send_application_notification')
    assert hasattr(service, 'test_connections')
    assert hasattr(service, 'get_notification_stats')

    # Проверяем историю уведомлений
    stats = service.get_notification_stats()
    assert 'total' in stats
    assert 'success' in stats
    assert 'failed' in stats


@patch('backend.integrations.telegram_sender.TelegramSender.send_application')
@patch('backend.integrations.email_sender.EmailSender.send_application')
def test_notification_fallback(mock_email_send, mock_telegram_send):
    """Тест отката с Telegram на Email."""
    # Telegram падает
    mock_telegram_send.return_value = False
    # Email работает
    mock_email_send.return_value = True

    service = NotificationService()
    service.email_sender.enabled = True

    test_data = {
        'name': 'Тест',
        'phone': '89123456789',
        'session_id': 'test_session'
    }

    # Отправляем уведомление
    result = service.send_application_notification(
        UserType.INDIVIDUAL, test_data
    )

    # Должен сработать fallback на Email
    assert result is True
    mock_telegram_send.assert_called_once()
    mock_email_send.assert_called_once()


def test_generate_test_applications():
    """Генерация тестовых заявок для проверки."""
    test_applications = {
        'individual': [],
        'business': [],
        'investor': []
    }

    # Генерируем 10 тестовых заявок каждого типа
    for i in range(10):
        # Физические лица
        test_applications['individual'].append({
            'name': f'Тестовый пользователь {i + 1}',
            'collateral': f'Автомобиль Марка Модель {2015 + i}',
            'amount': 500000 + i * 100000,
            'purpose': f'Цель займа #{i + 1}',
            'phone': f'8912{i:07d}',
            'session_id': f'indiv_session_{i}'
        })

        # Бизнес
        test_applications['business'].append({
            'company_name': f'ООО "Тестовая компания {i + 1}"',
            'amount': 1000000 + i * 500000,
            'collateral': f'Обеспечение #{i + 1}: недвижимость, оборудование',
            'purpose': f'Развитие бизнеса #{i + 1}',
            'phone': f'8922{i:07d}',
            'session_id': f'bus_session_{i}'
        })

        # Инвесторы
        test_applications['investor'].append({
            'name': f'Инвестор {i + 1}',
            'investment_amount': 2000000 + i * 300000,
            'term_months': 6 + i * 3,
            'investment_goal': f'Цель инвестирования #{i + 1}',
            'phone': f'8932{i:07d}',
            'session_id': f'inv_session_{i}'
        })

    return test_applications


if __name__ == "__main__":
    print("Генерация тестовых данных...")
    test_data = generate_test_applications()

    print(f"Сгенерировано:")
    print(f"- Физические лица: {len(test_data['individual'])} заявок")
    print(f"- Бизнес: {len(test_data['business'])} заявок")
    print(f"- Инвесторы: {len(test_data['investor'])} заявок")

    # Выводим примеры
    print("\nПример заявки (физ. лицо):")
    print(test_data['individual'][0])