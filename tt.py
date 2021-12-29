import requests

def check_response(response):
    """проверяет ответ API на корректность.
    """
    try:
        homeworks = response.get('homeworks')
    except None as e:
        return f'Список работ пуст. Тип ошибки {e}.'
