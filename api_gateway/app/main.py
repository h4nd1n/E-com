from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .api import analytics, orders
from .config import settings
from .db import create_engine_and_sessionmaker, run_migrations
from .kafka_client import create_kafka_publisher


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Создаем ресурсы на старте и закрываем их на останове."""
    engine, session_maker = create_engine_and_sessionmaker()
    app.state.engine = engine
    app.state.session_maker = session_maker
    await run_migrations(engine)

    kafka_publisher = await create_kafka_publisher()
    app.state.kafka_publisher = kafka_publisher
    await kafka_publisher.log_event("GatewayStarted", {"service": settings.app_name})

    try:
        yield
    finally:
        await kafka_publisher.log_event("GatewayStopping", {"service": settings.app_name})
        await kafka_publisher.close()
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(orders.router)
    app.include_router(analytics.router)
    return app


app = create_app()
