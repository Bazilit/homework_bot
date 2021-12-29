import requests
import time
from pprint import pprint

PRACTICUM_TOKEN = 'AQAAAABX-LiaAAYckSvWDNT6vEKrvzxwgJjWivY'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def get_api_answer():
    """делает запрос к единственному эндпоинту API-сервиса.
    """
    url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    payload = {'from_date': 1638116040}
    homework_statuses = requests.get(url, headers=headers, params=payload).json()
    pprint(homework_statuses)

get_api_answer()