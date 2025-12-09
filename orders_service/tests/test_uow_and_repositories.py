import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from orders_service.domain import events
from orders_service.infrastructure.models import OrderEvent, OrderState
from orders_service.infrastructure.repositories import (
    SqlAlchemyOrderEventRepository,
    SqlAlchemyOrderStateRepository,
)
@pytest.mark.asyncio
async def test_uow_commit_persists_changes(session_maker: async_sessionmaker[AsyncSession], uow_factory):
    async with uow_factory() as uow:
        await uow.events.append_event("10", events.ORDER_CREATED, {"order_id": "10"})
        await uow.state.upsert_state("10", "created")
        await uow.commit()

    async with session_maker() as session:
        res_event = await session.execute(select(OrderEvent).where(OrderEvent.order_id == "10"))
        res_state = await session.get(OrderState, "10")
        assert res_event.scalar_one().type == events.ORDER_CREATED
        assert res_state.status == "created"


@pytest.mark.asyncio
async def test_repositories_load_and_upsert(session_maker: async_sessionmaker[AsyncSession]):
    async with session_maker() as session:
        events_repo = SqlAlchemyOrderEventRepository(session)
        state_repo = SqlAlchemyOrderStateRepository(session)

        await events_repo.append_event("77", events.ORDER_CREATED, {"order_id": "77"})
        await state_repo.upsert_state("77", "created")
        await session.commit()

        loaded = await events_repo.load_events("77")
        state = await state_repo.get_state("77")

        assert len(loaded) == 1
        assert loaded[0].type == events.ORDER_CREATED
        assert state.status == "created"
