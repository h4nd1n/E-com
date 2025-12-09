from dataclasses import dataclass

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from orders_service.config import settings
from orders_service.domain.uow import UoWFactory
from orders_service.infrastructure.db import create_engine_and_sessionmaker, run_migrations
from orders_service.infrastructure.kafka import (
    KafkaEventPublisher,
    consume_commands,
    create_consumer,
    create_producer,
)
from orders_service.infrastructure.uow import create_uow_factory


@dataclass
class OrderServiceDeps:
    engine: AsyncEngine
    session_maker: async_sessionmaker[AsyncSession]
    uow_factory: UoWFactory
    producer: AIOKafkaProducer
    publisher: KafkaEventPublisher
    consumer: AIOKafkaConsumer


async def build_dependencies() -> OrderServiceDeps:
    engine, session_maker = create_engine_and_sessionmaker()
    await run_migrations(engine)

    uow_factory = create_uow_factory(session_maker)

    producer = await create_producer()
    publisher = KafkaEventPublisher(producer, topic=settings.events_topic)
    consumer = await create_consumer()

    return OrderServiceDeps(
        engine=engine,
        session_maker=session_maker,
        uow_factory=uow_factory,
        producer=producer,
        publisher=publisher,
        consumer=consumer,
    )


__all__ = [
    "build_dependencies",
    "consume_commands",
    "OrderServiceDeps",
]
