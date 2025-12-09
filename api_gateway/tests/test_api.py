import asyncio
from types import SimpleNamespace

import httpx
import pytest
import pytest_asyncio

from app.services import analytics as analytics_service
import app.main as main

from app import config


class FakeKafkaPublisher:
    def __init__(self):
        self.events = []
        self.logs = []

    async def publish_event(self, topic: str, event_type: str, payload: dict, key: str | None = None, source: str | None = None) -> str:
        self.events.append({"topic": topic, "event_type": event_type, "payload": payload, "key": key, "source": source})
        return "corr-id"

    async def log_event(self, event_type: str, payload: dict) -> str:
        self.logs.append({"event_type": event_type, "payload": payload})
        return "log-id"

    async def close(self) -> None:
        return None


class FakeResponse:
    def __init__(self, data: dict, status_code: int = 200):
        self._data = data
        self.status_code = status_code

    def json(self) -> dict:
        return self._data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=self)


class FakeAsyncClient:
    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url
        self.timeout = timeout
        self.requests = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, path: str, params: dict | None = None):
        self.requests.append({"path": path, "params": params})
        return FakeResponse({"metric": params.get("metric"), "rows": []})


@pytest_asyncio.fixture
async def test_app(monkeypatch, tmp_path):
    # Подменяем конфиг на изолированную SQLite и тестовый HTTP сервис аналитики.
    config.settings.database_url = f"sqlite+aiosqlite:///{tmp_path/'test.db'}"
    config.settings.analytics_service_url = "http://analytics.test"

    fake_publisher = FakeKafkaPublisher()

    async def fake_create_kafka_publisher():
        return fake_publisher

    # Подменяем фабрику Kafka и httpx-клиент в сервисе аналитики.
    monkeypatch.setattr(main, "create_kafka_publisher", fake_create_kafka_publisher)
    monkeypatch.setattr(analytics_service, "httpx", SimpleNamespace(AsyncClient=FakeAsyncClient))

    app = main.create_app()
    lifespan = app.router.lifespan_context(app)
    await lifespan.__aenter__()
    transport = httpx.ASGITransport(app=app)
    client = httpx.AsyncClient(transport=transport, base_url="http://testserver")

    try:
        yield {"client": client, "publisher": fake_publisher}
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_create_order(test_app):
    client = test_app["client"]
    publisher = test_app["publisher"]

    resp = await client.post(
        "/orders",
        json={"item": "cat food", "amount": 10.5, "currency": "USD"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 1
    assert body["status"] == "created"
    assert any(e["event_type"] == "OrderCreated" for e in publisher.events)


@pytest.mark.asyncio
async def test_pay_order_flow(test_app):
    client = test_app["client"]
    publisher = test_app["publisher"]

    await client.post("/orders", json={"item": "toy", "amount": 5, "currency": "USD"})
    resp = await client.post("/orders/1/pay", json={"amount": 5, "method": "card"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 1
    assert body["status"] == "requested"
    assert any(e["event_type"] == "PaymentRequested" for e in publisher.events)


@pytest.mark.asyncio
async def test_pay_order_not_found(test_app):
    client = test_app["client"]

    resp = await client.post("/orders/999/pay", json={"amount": 5, "method": "card"})
    assert resp.status_code == 404
    assert "не найден" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_analytics_http_passthrough(test_app):
    client = test_app["client"]
    publisher = test_app["publisher"]

    resp = await client.get("/analytics/sales", params={"limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["metric"] == "sales"
    assert any(log["event_type"] == "AnalyticsHttpRequested" for log in publisher.logs)
