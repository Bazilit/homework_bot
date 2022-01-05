import logging
import os
import time

import requests
import telegram
from telegram import TelegramError
from dotenv import load_dotenv
from simplejson.errors import JSONDecodeError
from exceptions import CustomStatusesError, ResponseIsNone
from http import HTTPStatus

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 10
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
PAST_MESSAGE = ''

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='myapp.log'
)

logger = logging.getLogger(__name__)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except TelegramError:
        logger.error(
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
        logger.error('Превышено время ожидания. Сайт не отвечает.')
    except requests.exceptions.TooManyRedirects:
        logger.error('Некорректный url адрес. Попробуйте другой.')
    except requests.exceptions.RequestException as e:
        logger.error('Критическая ошибка. Работа прекращена.')
        raise SystemExit(e)
    if homework_statuses.status_code != HTTPStatus.OK:
        logger.error(f'Ошибка {homework_statuses.status_code}')
        raise CustomStatusesError
    try:
        response = homework_statuses.json()
        return response
    except JSONDecodeError:
        logger.error('Ответ не преобразуется в json')


def check_response(response):
    """Проверяет ответ API на корректность."""
    if response is None:
        logger.error('response пришел пустым.')
        raise ResponseIsNone
    if not isinstance(response, dict):
        logger.error('Некорректный тип данных response на входе')
        raise TypeError('Некорректный тип данных response на входе')
    if 'homeworks' not in response:
        logger.error('По ключу homeworks ничего нет')
        raise KeyError('Ошибка с ключем homeworks')
    if response['homeworks'] == []:
        return {}
    homework = response['homeworks']
    if not isinstance(homework, list):
        logger.error('По ключу homework данные не ввиде списка')
        raise TypeError('По ключу homework данные не ввиде списка')
    return homework


def parse_status(homework):
    """Извлечение статуса работы."""
    if 'homework_name' not in homework:
        logger.error('По ключу homework_name ничего нет')
        raise KeyError('Ошибка с ключем homework_name')
    homework_name = homework['homework_name']
    if 'status' not in homework:
        logger.error('По ключу status ничего нет')
        raise KeyError('Ошибка с ключем status')
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        logger.error(f'Неизвестный статус {homework_status}')
        raise KeyError('Ошибка с ключем homework_status')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logger.error('Переменная PRACTICUM_TOKEN не задана.')
        return False
    if TELEGRAM_TOKEN is None:
        logger.error('Переменная TELEGRAM_TOKEN не задана.')
        return False
    if TELEGRAM_CHAT_ID is None:
        logger.error('Переменная TELEGRAM_CHAT_ID не задана.')
        return False
    else:
        logger.info('Проверка переменных прошла успешна.')
        return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while check_tokens():
        try:
            response = get_api_answer(current_timestamp)
            logger.info('Ответ response получен')
            homework = check_response(response)
            logger.info('response проверен')
            if homework:
                message = parse_status(homework[0])
                logger.info('Статусы получены')
                if message != PAST_MESSAGE:
                    send_message(bot, message)
                    logger.info('Письмо отправлено')
            else:
                logger.info('Статус работы не изменился')
                time.sleep(RETRY_TIME)
            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(f'Проблема с работой. Ошибка {error}')
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
