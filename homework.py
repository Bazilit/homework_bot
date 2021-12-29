import requests
import time
import os
import telegram
from dotenv import load_dotenv
import logging
from urllib.error import HTTPError
from urllib3.exceptions import ConnectTimeoutError
from requests.exceptions import (
    ConnectionError, Timeout, RequestException,
    InvalidHeader, InvalidURL, ProxyError, InvalidProxyURL
    )

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 1
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

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
    result = homework_statuses.json()
    if homework_statuses.status_code != 200:
        raise Exception(f'Статус код не 200! Статус код {homework_statuses.status_code}')
    return result
    


def check_response(response):
    """проверяет ответ API на корректность.
    """
    homework = response.get('homeworks')
    if not homework:
        raise Exception('Нет ключа homeworks')
    if type(homework) is not list:
        raise Exception('домашки приходят не в виде списка в ответ от API')
    return homework



def parse_status(homework): #готово. работает. Проверить путь запроса homework
    """извлекает из информации о конкретной домашней работе статус этой работы.
    """
    homework_name = homework['homework_name']
    homework_status = homework['status']
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError as e:
        logging.error(f'Неверный ключ запроса verdict. Тип ошибки {e}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens(): #Проверка работает. Многоточие и None возвращает как некорректный тип данных
    """проверяет доступность переменных окружения
    """
    try:
        if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            logging.debug('Проверка переменных окружения завершилась успешно')
            return True
        elif len(TELEGRAM_CHAT_ID) == 0:
            print('В переменной TELEGRAM_CHAT_ID пустое значение')
            return False
        elif len(TELEGRAM_TOKEN) == 0:
            print('В переменной TELEGRAM_TOKEN пустое значение')
            return False
        elif len(PRACTICUM_TOKEN) == 0:
            print('В переменной PRACTICUM_TOKEN пустое значение')
            return False
        elif PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            logging.debug('Проверка переменных окружения завершилась успешно')
            return True
    except TypeError as e:
        logging.error('В переменной некорректное значение данных. Тип ошибки {e}')
        return False



def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1638138951
    # int(time.time())
    check_tokens() #идет проверка переменных, если все ок возвращает значение True и запускается цикл
    while True:
        try:
            response = get_api_answer(current_timestamp) # делаем запрос к API домашки
            check_response(response) # Проверяет ответ API на корректность
            homework = response.get('homeworks')
            message = parse_status(homework) #После проверки запроса происходит нарезка данных с запроса
            
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}' # Это перечень ошибок в котороых переменные доступны, но что-то пошло не так
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            message = 'Проблема с глобальными переменными и токен. Проверка на наличие не пройдена.'
            send_message(bot, message)
            raise SystemExit


if __name__ == '__main__':
    main()
