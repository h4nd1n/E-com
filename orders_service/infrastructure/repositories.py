from datetime import datetime, UTC
from typing import Iterable

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from orders_service.domain.models import OrderEventRecord, OrderStateRecord
from orders_service.domain.repositories import OrderEventRepository, OrderStateRepository
from orders_service.infrastructure.models import OrderEvent, OrderState


class SqlAlchemyOrderEventRepository(OrderEventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def append_event(self, order_id: str, event_type: str, payload: dict) -> OrderEventRecord:
        event = OrderEvent(order_id=order_id, type=event_type, payload=payload)
        self.session.add(event)
        await self.session.flush()
        return OrderEventRecord(
            id=event.id,
            order_id=event.order_id,
            type=event.type,
            payload=event.payload,
            created_at=event.created_at,
        )

    async def load_events(self, order_id: str) -> Iterable[OrderEventRecord]:
        stmt = select(OrderEvent).where(OrderEvent.order_id == order_id).order_by(OrderEvent.id)
        result = await self.session.execute(stmt)
        events = result.scalars().all()
        return [
            OrderEventRecord(
                id=item.id,
                order_id=item.order_id,
                type=item.type,
                payload=item.payload,
                created_at=item.created_at,
            )
            for item in events
        ]


class SqlAlchemyOrderStateRepository(OrderStateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_state(self, order_id: str) -> OrderStateRecord | None:
        state = await self.session.get(OrderState, order_id)
        if not state:
            return None
        return OrderStateRecord(order_id=state.order_id, status=state.status, updated_at=state.updated_at)

    async def upsert_state(self, order_id: str, status: str) -> OrderStateRecord:
        now = datetime.now(UTC)
        existing = await self.session.get(OrderState, order_id)
        if existing:
            await self.session.execute(
                update(OrderState)
                .where(OrderState.order_id == order_id)
                .values(status=status, updated_at=now)
            )
            return OrderStateRecord(order_id=order_id, status=status, updated_at=now)

        state = OrderState(order_id=order_id, status=status, updated_at=now)
        self.session.add(state)
        await self.session.flush()
        return OrderStateRecord(order_id=state.order_id, status=state.status, updated_at=state.updated_at)
