import logging
import os
import time

import requests
import telegram
from telegram import TelegramError
from dotenv import load_dotenv
from simplejson.errors import JSONDecodeError
from exceptions import CustomStatusesError
from http import HTTPStatus

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
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except TelegramError:
        logging.error(
            f'Невозможно отправить сообщение в чат id {TELEGRAM_CHAT_ID}'
        )


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except requests.exceptions.Timeout:
        logging.error('Превышено время ожидания. Сайт не отвечает.')
    except requests.exceptions.TooManyRedirects:
        logging.error('Некорректный url адрес. Попробуйте другой.')
    except requests.exceptions.RequestException as e:
        logging.error('Критическая ошибка. Работа прекращена.')
        raise SystemExit(e)
    if homework_statuses.status_code != HTTPStatus.OK:
        logging.error(f'Ошибка {homework_statuses.status_code}')
        raise CustomStatusesError
    try:
        return homework_statuses.json()
    except JSONDecodeError:
        logging.error('Ответ не преобразуется в json')


def check_response(response):
    """Проверяет ответ API на корректность."""
    homework = response['homeworks']
    if not homework:
        raise Exception('Нет ключа homeworks')
    if type(homework) is not list:
        raise Exception('Домашки приходят не в виде списка в ответ от API')
    if response is None:
        raise Exception('Пустой ответный запрос')
    if not isinstance(response, dict):
        logging.error('Некорректный тип данных на входе')
    return homework


def parse_status(homework):
    """Извлечение статуса работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logging.error('Переменная PRACTICUM_TOKEN не задана.')
        return False
    if TELEGRAM_TOKEN is None:
        logging.error('Переменная TELEGRAM_TOKEN не задана.')
        return False
    if TELEGRAM_CHAT_ID is None:
        logging.error('Переменная TELEGRAM_CHAT_ID не задана.')
        return False
    else:
        logging.info('Проверка переменных прошла успешна.')
        return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(0)
    # int(time.time())
    while check_tokens() is True:
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
            logging.error(f'Проблема с работой. Ошибка {error}')
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
