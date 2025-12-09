from orders_service.domain import commands, events
from orders_service.domain.errors import OrderAlreadyExists, OrderNotFound
from orders_service.domain.ports import EventPublisher
from orders_service.domain.uow import UoWFactory


class OrderCommandService:
    """Бизнес-логика обработки команд заказов. Работает только через UoW и репозитории."""

    def __init__(self, uow_factory: UoWFactory, publisher: EventPublisher):
        self.uow_factory = uow_factory
        self.publisher = publisher

    async def handle_command(self, command: dict) -> None:
        cmd_type = command.get("type")
        if cmd_type == commands.CREATE_ORDER:
            await self._handle_create(command)
        elif cmd_type == commands.CANCEL_ORDER:
            await self._handle_cancel(command)
        elif cmd_type == commands.MARK_PAID:
            await self._handle_mark_paid(command)
        elif cmd_type == commands.SHIP_ORDER:
            await self._handle_ship(command)
        # Неизвестные команды игнорируем, но можно залогировать снаружи.

    async def _handle_create(self, cmd: dict) -> None:
        order_id = str(cmd["order_id"])
        payload = {
            "order_id": order_id,
            "item": cmd.get("item"),
            "amount": cmd.get("amount"),
            "currency": cmd.get("currency"),
        }
        async with self.uow_factory() as uow:
            existing = await uow.state.get_state(order_id)
            if existing:
                raise OrderAlreadyExists(f"Заказ {order_id} уже создан")
            await uow.events.append_event(order_id, events.ORDER_CREATED, payload)
            await uow.state.upsert_state(order_id, status="created")
            await uow.commit()

        await self.publisher.publish_event(events.ORDER_CREATED, order_id, payload)

    async def _handle_cancel(self, cmd: dict) -> None:
        order_id = str(cmd["order_id"])
        payload = {"order_id": order_id, "reason": cmd.get("reason")}
        async with self.uow_factory() as uow:
            state = await uow.state.get_state(order_id)
            if not state:
                raise OrderNotFound(f"Заказ {order_id} не найден")
            await uow.events.append_event(order_id, events.ORDER_CANCELLED, payload)
            await uow.state.upsert_state(order_id, status="cancelled")
            await uow.commit()

        await self.publisher.publish_event(events.ORDER_CANCELLED, order_id, payload)

    async def _handle_mark_paid(self, cmd: dict) -> None:
        order_id = str(cmd["order_id"])
        payload = {"order_id": order_id, "paid_at": cmd.get("paid_at")}
        async with self.uow_factory() as uow:
            state = await uow.state.get_state(order_id)
            if not state:
                raise OrderNotFound(f"Заказ {order_id} не найден")
            await uow.events.append_event(order_id, events.ORDER_PAID, payload)
            await uow.state.upsert_state(order_id, status="paid")
            await uow.commit()

        await self.publisher.publish_event(events.ORDER_PAID, order_id, payload)

    async def _handle_ship(self, cmd: dict) -> None:
        order_id = str(cmd["order_id"])
        payload = {"order_id": order_id, "shipped_at": cmd.get("shipped_at")}
        async with self.uow_factory() as uow:
            state = await uow.state.get_state(order_id)
            if not state:
                raise OrderNotFound(f"Заказ {order_id} не найден")
            await uow.events.append_event(order_id, events.ORDER_SHIPPED, payload)
            await uow.state.upsert_state(order_id, status="shipped")
            await uow.commit()

        await self.publisher.publish_event(events.ORDER_SHIPPED, order_id, payload)
