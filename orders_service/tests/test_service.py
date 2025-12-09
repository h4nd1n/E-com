import pytest

from orders_service.domain import commands, events
from orders_service.domain.errors import OrderAlreadyExists, OrderNotFound
from orders_service.domain.models import OrderStateRecord


@pytest.mark.asyncio
async def test_create_order_success(order_service, fake_uow, fake_publisher):
    cmd = {"type": commands.CREATE_ORDER, "order_id": "1", "item": "book", "amount": 10, "currency": "USD"}
    await order_service.handle_command(cmd)

    assert fake_uow.state.items["1"].status == "created"
    assert fake_uow.committed is True
    assert fake_publisher.published[0]["type"] == events.ORDER_CREATED


@pytest.mark.asyncio
async def test_create_order_duplicate_raises(order_service, fake_uow, fake_publisher):
    fake_uow.state.items["1"] = OrderStateRecord(order_id="1", status="created")

    cmd = {"type": commands.CREATE_ORDER, "order_id": "1"}
    with pytest.raises(OrderAlreadyExists):
        await order_service.handle_command(cmd)


@pytest.mark.asyncio
async def test_cancel_order_not_found(order_service):
    cmd = {"type": commands.CANCEL_ORDER, "order_id": "missing"}
    with pytest.raises(OrderNotFound):
        await order_service.handle_command(cmd)


@pytest.mark.asyncio
async def test_mark_paid_and_ship_flow(order_service, fake_uow, fake_publisher):
    fake_uow.state.items["42"] = OrderStateRecord(order_id="42", status="created")

    await order_service.handle_command({"type": commands.MARK_PAID, "order_id": "42", "paid_at": "t"})
    await order_service.handle_command({"type": commands.SHIP_ORDER, "order_id": "42", "shipped_at": "t2"})

    assert fake_uow.state.items["42"].status == "shipped"
    assert fake_publisher.published[-1]["type"] == events.ORDER_SHIPPED
