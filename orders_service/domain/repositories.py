from typing import Iterable, Protocol

from .models import OrderEventRecord, OrderStateRecord


class OrderEventRepository(Protocol):
    async def append_event(self, order_id: str, event_type: str, payload: dict) -> OrderEventRecord:
        ...

    async def load_events(self, order_id: str) -> Iterable[OrderEventRecord]:
        ...


class OrderStateRepository(Protocol):
    async def get_state(self, order_id: str) -> OrderStateRecord | None:
        ...

    async def upsert_state(self, order_id: str, status: str) -> OrderStateRecord:
        ...
