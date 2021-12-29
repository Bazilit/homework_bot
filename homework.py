import logging
import os
import time

import requests
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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    response = homework_statuses.json()
    if homework_statuses.status_code != 200:
        raise Exception(
            f'Статус код не 200!'
            f'Статус код {homework_statuses.status_code}'
        )
    return response


def check_response(response):
    """Проверяет ответ API на корректность."""
    homework = response['homeworks']
    if not homework:
        raise Exception('Нет ключа homeworks')
    if type(homework) is not list:
        raise Exception('домашки приходят не в виде списка в ответ от API')
    if response is None:
        raise Exception('Нет ')
    if not isinstance(response, dict):
        logging.error('Ошибка работает')
    return homework


def parse_status(homework):
    """Извлечение статуса работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
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
    except TypeError as error:
        logging.error(
            f'В переменной некорректное значение данных.'
            f'Тип ошибки {error}')
        return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    check_tokens()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            check_response(response)
            homework = response['homeworks'][0]
            if homework:
                logging.info(f'{homework} найден. Данные отправлены')
                message = parse_status(homework)
                send_message(bot, message)
            else:
                logging.info(f'{homework} не найден. Словарь отсутствует')
                logging.debug(f'Следующая попытка через {RETRY_TIME} сек')
            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(f'Проблема с работой. Ошибка{error}')
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
