"""
Простой скрипт для проверки Telegram интеграции.
"""
import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.utils.telegram_helper import create_telegram_sender, create_notification_service


def main():
    """Проверяет подключение к Telegram."""
    print("Проверка подключения к Telegram...")

    # Создаем экземпляры
    telegram_sender = create_telegram_sender()
    notification_service = create_notification_service()

    # Проверяем настройки
    if not telegram_sender.enabled:
        print("❌ Telegram отключен в настройках")
        return

    if not telegram_sender.bot_token:
        print("❌ Не указан TELEGRAM_BOT_TOKEN")
        return

    if not telegram_sender.chat_id:
        print("❌ Не указан TELEGRAM_CHAT_ID")
        return

    print(f"✅ Настройки найдены")
    print(f"   Bot token: {telegram_sender.bot_token[:10]}...")
    print(f"   Chat ID: {telegram_sender.chat_id}")

    # Проверяем подключение
    print("\nПроверка подключения к Telegram API...")
    bot_info = telegram_sender.get_bot_info()

    if bot_info and bot_info.get('ok'):
        bot = bot_info['result']
        print(f"✅ Бот подключен успешно!")
        print(f"   Имя: {bot.get('first_name')}")
        print(f"   Username: @{bot.get('username')}")
        print(f"   ID: {bot.get('id')}")
    else:
        print("❌ Не удалось подключиться к Telegram API")
        return

    # Отправляем тестовое сообщение
    print("\nОтправка тестового сообщения...")
    success = telegram_sender.send_test_message("✅ Тестовое сообщение от ИИ-консультанта BBKinvest")

    if success:
        print("✅ Тестовое сообщение отправлено успешно!")
    else:
        print("❌ Не удалось отправить тестовое сообщение")

    # Проверяем общий сервис уведомлений
    print("\nПроверка Notification Service...")
    connections = notification_service.test_connections()

    print(f"\nИтоги:")
    print(f"  Telegram: {'✅' if connections['telegram'] else '❌'}")
    print(f"  Email: {'✅' if connections['email'] else '❌'}")


if __name__ == "__main__":
    main()