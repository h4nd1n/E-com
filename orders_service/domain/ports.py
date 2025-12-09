from typing import Protocol


class EventPublisher(Protocol):
    async def publish_event(self, event_type: str, order_id: str, payload: dict) -> None:
        ...
