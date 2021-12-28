import requests
import time
import os
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message): #Команда отправки сообщения в Телегу
    """отправляет сообщение в Telegram чат
    """
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """делает запрос к единственному эндпоинту API-сервиса.
    """
    timestamp = current_timestamp or int(time.time()) #time.time это текущее время utc. int для округления
    params = {'from_date': timestamp}
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)

    ...


def check_response(response):
    """проверяет ответ API на корректность.
    """

    ...


def parse_status(homework): #готово. работает. Проверить путь запроса homework
    """извлекает из информации о конкретной домашней работе статус этой работы.
    """
    homework_name = homework.json().get('homeworks')[0]['homework_name']
    homework_status = homework.json().get('homeworks')[0]['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens(): #Проверка работает. Многоточие и None возвращает как некорректный тип данных
    """проверяет доступность переменных окружения
    """
    try:
        if len(TELEGRAM_CHAT_ID) == 0:
            print('В переменной TELEGRAM_CHAT_ID пустое значение')
            return False
        elif len(TELEGRAM_TOKEN) == 0:
            print('В переменной TELEGRAM_TOKEN пустое значение')
            return False
        elif len(PRACTICUM_TOKEN) == 0:
            print('В переменной PRACTICUM_TOKEN пустое значение')
            return False
        else:
            return True
    except TypeError:
        print('В переменной некорректное значение данных')
        return False



def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...
    check_tokens() #идет проверка переменных, если все ок возвращает значение True и запускается цикл
    while True:
        try:
            response = get_api_answer(current_timestamp) # делаем запрос к API домашки
            check_response(response) # Проверяет ответ API на корректность

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}' # Это перечень ошибок в котороых переменные доступны, но что-то пошло не так
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
