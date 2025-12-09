class OrderServiceError(Exception):
    """Базовая ошибка сервиса заказов."""


class OrderAlreadyExists(OrderServiceError):
    """Заказ уже существует."""


class OrderNotFound(OrderServiceError):
    """Заказ не найден."""


class InvalidStateTransition(OrderServiceError):
    """Невалидное изменение статуса."""
