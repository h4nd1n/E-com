import asyncio
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from orders_service.application.service import OrderCommandService
from orders_service.domain.uow import UoWFactory
from orders_service.infrastructure.models import Base
from orders_service.infrastructure.uow import create_uow_factory
from orders_service.tests.fakes import FakePublisher, FakeUoW


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    # Позволяем использовать anyio с asyncio в pytest-asyncio.
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Своя петля событий для session-фикстур."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def async_engine(tmp_path) -> AsyncIterator[AsyncEngine]:
    db_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def session_maker(async_engine: AsyncEngine) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    Session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    yield Session


@pytest.fixture()
def uow_factory(session_maker: async_sessionmaker[AsyncSession]) -> UoWFactory:
    return create_uow_factory(session_maker)


@pytest.fixture()
def fake_uow() -> FakeUoW:
    return FakeUoW()


@pytest.fixture()
def fake_uow_factory(fake_uow: FakeUoW):
    @asynccontextmanager
    async def _factory():
        async with fake_uow:
            yield fake_uow

    return _factory


@pytest.fixture()
def fake_publisher() -> FakePublisher:
    return FakePublisher()


@pytest.fixture()
def order_service(fake_uow_factory, fake_publisher) -> OrderCommandService:
    return OrderCommandService(fake_uow_factory, fake_publisher)
