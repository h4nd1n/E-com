from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..errors import OrderNotFound
from ..models import Order


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, item: str, amount: float, currency: str) -> Order:
        order = Order(item=item, amount=amount, currency=currency, status="created")
        self.session.add(order)
        await self.session.flush()
        await self.session.commit()
        self.session.expunge(order)
        return order

    async def get(self, order_id: int) -> Order:
        order = await self.session.get(Order, order_id)
        if not order:
            raise OrderNotFound(f"Заказ {order_id} не найден")
        self.session.expunge(order)
        return order

    async def mark_payment_requested(self, order_id: int) -> None:
        stmt = (
            update(Order)
            .where(Order.id == order_id)
            .values(status="payment_requested")
        )
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise OrderNotFound(f"Заказ {order_id} не найден")
        await self.session.commit()

    async def ensure_exists(self, order_id: int) -> Order:
        return await self.get(order_id)
