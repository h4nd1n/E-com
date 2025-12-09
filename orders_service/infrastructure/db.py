from pathlib import Path
from typing import Tuple

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from orders_service.config import settings
from orders_service.infrastructure.models import Base


def _ensure_sqlite_dir(database_url: str) -> None:
    url = make_url(database_url)
    if url.drivername.startswith("sqlite") and url.database:
        db_path = Path(url.database)
        if db_path.parent:
            db_path.parent.mkdir(parents=True, exist_ok=True)


def create_engine_and_sessionmaker() -> Tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Создаем движок и sessionmaker для сервиса заказов."""
    _ensure_sqlite_dir(settings.database_url)
    engine = create_async_engine(settings.database_url, future=True, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return engine, session_maker


async def run_migrations(engine: AsyncEngine) -> None:
    """Поднимаем таблицы event-sourcing модели."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
