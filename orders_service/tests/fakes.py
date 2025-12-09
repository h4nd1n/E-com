from dataclasses import dataclass, field
from typing import Any

from orders_service.domain.models import OrderStateRecord
from orders_service.domain.uow import OrderUnitOfWork


@dataclass
class FakeMessage:
    value: bytes


class FakeConsumer:
    def __init__(self, messages):
        self._messages = messages
        self.committed = 0
        self.stopped = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._messages:
            raise StopAsyncIteration
        return self._messages.pop(0)

    async def commit(self):
        self.committed += 1

    async def stop(self):
        self.stopped = True


@dataclass
class FakePublisher:
    published: list[dict[str, Any]] = field(default_factory=list)

    async def publish_event(self, event_type: str, order_id: str, payload: dict) -> None:
        self.published.append({"type": event_type, "order_id": order_id, "payload": payload})

    @property
    def events(self) -> list[dict[str, Any]]:
        # Совместимость с тестами, ожидающими .events
        return self.published


class FakeOrderEventsRepo:
    def __init__(self):
        self.items = []

    async def append_event(self, order_id: str, event_type: str, payload: dict) -> None:
        self.items.append({"order_id": order_id, "type": event_type, "payload": payload})

    async def load_events(self, order_id: str):
        return [e for e in self.items if e["order_id"] == order_id]


class FakeOrderStateRepo:
    def __init__(self):
        self.items: dict[str, OrderStateRecord] = {}

    async def get_state(self, order_id: str):
        return self.items.get(order_id)

    async def upsert_state(self, order_id: str, status: str):
        rec = OrderStateRecord(order_id=order_id, status=status)
        self.items[order_id] = rec
        return rec


class FakeUoW(OrderUnitOfWork):
    def __init__(self):
        self.events = FakeOrderEventsRepo()
        self.state = FakeOrderStateRepo()
        self.committed = False

    async def __aenter__(self) -> "FakeUoW":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.committed = False
