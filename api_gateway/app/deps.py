from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .kafka_client import KafkaPublisher
from .repositories.orders import OrderRepository
from .repositories.payments import PaymentRepository
from .services.analytics import AnalyticsService
from .services.orders import OrderService, PaymentService


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Отдаем отдельную сессию из sessionmaker, сохраненного в app.state."""
    session_maker: async_sessionmaker[AsyncSession] = request.app.state.session_maker
    async with session_maker() as session:
        yield session


def get_kafka_publisher(request: Request) -> KafkaPublisher:
    """Достаем KafkaPublisher из состояния приложения."""
    return request.app.state.kafka_publisher


# Типовые алиасы для Annotated-deps
SessionDep = Annotated[AsyncSession, Depends(get_session)]
KafkaPublisherDep = Annotated[KafkaPublisher, Depends(get_kafka_publisher)]


def get_order_service(
    session: SessionDep,
    publisher: KafkaPublisherDep,
) -> OrderService:
    return OrderService(orders_repo=OrderRepository(session), publisher=publisher)


def get_payment_service(
    session: SessionDep,
    publisher: KafkaPublisherDep,
) -> PaymentService:
    return PaymentService(payments_repo=PaymentRepository(session), publisher=publisher)


def get_analytics_service(publisher: KafkaPublisherDep) -> AnalyticsService:
    return AnalyticsService(publisher=publisher)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]
