import json
from typing import Optional
from uuid import uuid4

from aiokafka import AIOKafkaProducer

from .config import settings


def _json_payload(event_type: str, payload: dict, source: str) -> bytes:
    return json.dumps(
        {
            "event_type": event_type,
            "source": source,
            "payload": payload,
        },
        ensure_ascii=True,
    ).encode("utf-8")


class KafkaPublisher:
    """Обертка вокруг AIOKafkaProducer без глобальных синглтонов."""

    def __init__(self, producer: AIOKafkaProducer):
        self._producer = producer

    async def publish_event(
        self,
        topic: str,
        event_type: str,
        payload: dict,
        key: Optional[str] = None,
        source: Optional[str] = None,
    ) -> str:
        correlation_id = str(uuid4())
        message_payload = {**payload, "correlation_id": correlation_id}
        await self._producer.send_and_wait(
            topic,
            _json_payload(event_type, message_payload, source or settings.app_name),
            key=key.encode("utf-8") if key else None,
        )
        return correlation_id

    async def log_event(self, event_type: str, payload: dict) -> str:
        return await self.publish_event(
            settings.kafka_topic_logs,
            event_type=event_type,
            payload=payload,
            source=settings.app_name,
        )

    async def close(self) -> None:
        await self._producer.stop()


async def create_kafka_publisher() -> KafkaPublisher:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=settings.app_name,
    )
    await producer.start()
    return KafkaPublisher(producer)
