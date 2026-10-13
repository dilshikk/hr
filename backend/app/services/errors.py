class ServiceError(Exception):
    """Ожидаемая ошибка бизнес-логики; превращается в JSON-ответ с кодом status."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
