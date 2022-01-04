class CustomStatusesError(Exception):
    """Ошибка HTTP статуса запроса. Отличимый от 200."""

    def __init__(self, homework_statuses):
        """Обработка homework_statuses."""
        self.homework_statuses = homework_statuses
        super().__init__(homework_statuses)
        return (
            f'Статус код не 200!.'
            f'Статус код {homework_statuses.status_code}.'
        )
