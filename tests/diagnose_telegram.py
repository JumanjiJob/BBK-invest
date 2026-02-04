import os
import requests
from dotenv import load_dotenv

print("=== ДИАГНОСТИКА TELEGRAM BOT ===")
print()

# 1. Проверка файлов
print("1. Проверка файлов...")
if os.path.exists('../.env'):
    print("✅ Файл .env существует")
else:
    print("❌ Файл .env НЕ найден")
    exit(1)

# 2. Загрузка переменных
print("\n2. Загрузка переменных окружения...")
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if TOKEN:
    print(f"✅ TELEGRAM_BOT_TOKEN: {TOKEN[:10]}... (длина: {len(TOKEN)})")
else:
    print("❌ TELEGRAM_BOT_TOKEN не найден в .env")

if CHAT_ID:
    print(f"✅ TELEGRAM_CHAT_ID: {CHAT_ID}")
else:
    print("❌ TELEGRAM_CHAT_ID не найден в .env")

# 3. Проверка формата токена
print("\n3. Проверка формата токена...")
if TOKEN:
    parts = TOKEN.split(':')
    if len(parts) == 2 and parts[0].isdigit() and len(parts[1]) > 10:
        print("✅ Формат токена верный (число:строка)")
        print(f"   ID бота: {parts[0]}")
        print(f"   Хэш: {parts[1][:10]}...")
    else:
        print("❌ Формат токена неверный!")
        print(f"   Ожидается: '123456789:ABCdefGHIjkl...'")
        print(f"   Получено: {TOKEN}")

# 4. Проверка бота через API getMe
print("\n4. Проверка бота через API getMe...")
if TOKEN:
    url = f'https://api.telegram.org/bot{TOKEN}/getMe'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"✅ Бот найден и работает!")
                print(f"   Username: @{bot_info.get('username')}")
                print(f"   ID: {bot_info.get('id')}")
                print(f"   Имя: {bot_info.get('first_name')}")
            else:
                print(f"❌ Ошибка в ответе API: {data.get('description')}")
        elif response.status_code == 404:
            print("❌ Ошибка 404: Бот не найден (неверный токен)")
            print("   Возможные причины:")
            print("   1. Токен скопирован не полностью")
            print("   2. Токен содержит лишние пробелы")
            print("   3. Бот был удален или токен изменен")
        elif response.status_code == 401:
            print("❌ Ошибка 401: Неавторизованный доступ (токен неверный)")
        else:
            print(f"❌ Неожиданная ошибка: {response.status_code}")
            print(f"   Ответ: {response.text[:100]}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")

# 5. Проверка канала через getUpdates
print("\n5. Проверка обновлений (getUpdates)...")
if TOKEN:
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                updates = data.get('result', [])
                if updates:
                    print(f"✅ Получено обновлений: {len(updates)}")
                    for i, update in enumerate(updates[-3:]):  # Последние 3
                        if 'channel_post' in update:
                            chat = update['channel_post']['chat']
                            print(f"   Обновление {i + 1}: Канал '{chat.get('title')}', ID: {chat.get('id')}")
                        elif 'message' in update:
                            chat = update['message']['chat']
                            print(
                                f"   Обновление {i + 1}: Чат '{chat.get('title', chat.get('first_name'))}', ID: {chat.get('id')}")
                else:
                    print("ℹ️ Нет обновлений. Если бот в канале, отправьте сообщение в канал.")
            else:
                print(f"❌ Ошибка в ответе: {data.get('description')}")
        else:
            print(f"❌ Ошибка запроса: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")

# 6. Попытка отправки с отладкой
print("\n6. Попытка отправки сообщения...")
if TOKEN and CHAT_ID:
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    # Пробуем разные форматы chat_id
    chat_ids_to_try = [CHAT_ID]

    # Если chat_id отрицательный, но не начинается с -100
    try:
        chat_int = int(CHAT_ID)
        if chat_int < 0 and not str(chat_int).startswith('-100'):
            chat_ids_to_try.append(f"-100{abs(chat_int)}")
    except ValueError:
        pass

    for test_chat_id in chat_ids_to_try:
        print(f"\n   Пробуем chat_id: {test_chat_id}")
        data = {
            'chat_id': test_chat_id,
            'text': 'Тестовое сообщение от BBKinvest AI Consultant',
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Сообщение отправлено успешно!")
                break
            else:
                print(f"   ❌ Ошибка: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Ошибка сети: {e}")

print("\n" + "=" * 50)
print("ДИАГНОСТИКА ЗАВЕРШЕНА")