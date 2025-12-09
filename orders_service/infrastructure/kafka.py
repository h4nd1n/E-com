import json
import logging
from typing import Callable, Awaitable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from orders_service.config import settings

log = logging.getLogger("order_service.kafka")


class KafkaEventPublisher:
    """Изолированная обертка для публикации событий заказов."""

    def __init__(self, producer: AIOKafkaProducer, topic: str):
        self.producer = producer
        self.topic = topic

    async def publish_event(self, event_type: str, order_id: str, payload: dict) -> None:
        envelope = {
            "type": event_type,
            "order_id": order_id,
            "payload": payload,
        }
        await self.producer.send_and_wait(
            self.topic,
            json.dumps(envelope).encode("utf-8"),
            key=str(order_id).encode("utf-8"),
        )


async def create_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=settings.service_name,
    )
    await producer.start()
    return producer


async def create_consumer() -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        settings.commands_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=settings.service_name,
        group_id=f"{settings.service_name}-group",
        enable_auto_commit=False,
    )
    await consumer.start()
    return consumer


async def consume_commands(consumer: AIOKafkaConsumer, handler: Callable[[dict], Awaitable[None]]) -> None:
    """Запускает бесконечное чтение команд с последовательной обработкой."""
    try:
        async for msg in consumer:
            try:
                command = json.loads(msg.value.decode("utf-8"))
                await handler(command)
                await consumer.commit()
            except Exception as exc:
                log.exception("Ошибка обработки команды: %s", exc)
                await consumer.commit()
    finally:
        await consumer.stop()
