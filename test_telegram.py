import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_test_message():
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    data = {
        'chat_id': CHAT_ID,
        'text': '✅ Тестовое сообщение от BBKinvest AI Consultant\nБот работает корректно!',
        'parse_mode': 'HTML'
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        print('✅ Сообщение отправлено успешно!')
        return True
    else:
        print('❌ Ошибка отправки:', response.text)
        return False


if __name__ == '__main__':
    send_test_message()