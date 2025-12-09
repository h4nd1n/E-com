from dataclasses import dataclass
import json

import pytest

from orders_service.application.service import OrderCommandService
from orders_service.domain import commands, events
from orders_service.infrastructure.kafka import consume_commands
from orders_service.tests.fakes import FakeMessage, FakeConsumer


@pytest.mark.asyncio
async def test_consume_commands_end_to_end(fake_uow_factory, fake_publisher):
    service = OrderCommandService(fake_uow_factory, fake_publisher)

    command = {"type": commands.CREATE_ORDER, "order_id": "555", "item": "phone", "amount": 1}
    fake_messages = [FakeMessage(value=json.dumps(command).encode("utf-8"))]
    consumer = FakeConsumer(fake_messages)

    await consume_commands(consumer, service.handle_command)

    assert consumer.committed == 1
    assert consumer.stopped is True
    assert fake_publisher.events[0]["type"] == events.ORDER_CREATED
