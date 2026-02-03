import requests

TOKEN = 'ВСТАВЬТЕ_ВАШ_ТОКЕН_ЗДЕСЬ'


def get_chat_id():
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    response = requests.get(url).json()

    if response['ok']:
        for update in response['result']:
            if 'channel_post' in update:
                chat_id = update['channel_post']['chat']['id']
                print(f'Chat ID канала: {chat_id}')
                return chat_id
        print('Не найдено обновлений. Отправьте сообщение в канал.')
    else:
        print('Ошибка:', response)


if __name__ == '__main__':
    get_chat_id()