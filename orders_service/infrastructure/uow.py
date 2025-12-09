from contextlib import asynccontextmanager
from typing import AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from orders_service.domain.uow import UoWFactory, OrderUnitOfWork
from orders_service.infrastructure.repositories import (
    SqlAlchemyOrderEventRepository,
    SqlAlchemyOrderStateRepository,
)


class SqlAlchemyOrderUnitOfWork(OrderUnitOfWork):
    """UoW, инкапсулирующий сессию БД и репозитории."""

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self._session_maker = session_maker
        self._session: AsyncSession | None = None
        self.events = None
        self.state = None

    async def __aenter__(self) -> "SqlAlchemyOrderUnitOfWork":
        self._session = self._session_maker()
        self.events = SqlAlchemyOrderEventRepository(self._session)
        self.state = SqlAlchemyOrderStateRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session is None:
            return
        if exc:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()


def create_uow_factory(session_maker: async_sessionmaker[AsyncSession]) -> UoWFactory:
    @asynccontextmanager
    async def _factory() -> AsyncContextManager[SqlAlchemyOrderUnitOfWork]:
        async with SqlAlchemyOrderUnitOfWork(session_maker) as uow:
            yield uow

    return _factory
