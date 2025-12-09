class DomainError(Exception):
    """Базовая доменная ошибка."""


class OrderNotFound(DomainError):
    """Заказ не найден."""


class PaymentNotFound(DomainError):
    """Платеж не найден."""
