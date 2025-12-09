from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from ..errors import OrderNotFound, PaymentNotFound
from ..models import Order, Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, payment_id: int) -> Payment:
        payment = await self.session.get(Payment, payment_id)
        if not payment:
            raise PaymentNotFound(f"Платеж {payment_id} не найден")
        self.session.expunge(payment)
        return payment

    async def request_payment(self, *, order_id: int, amount: float, method: str) -> Payment:
        """Создаем платеж и отмечаем заказ как payment_requested в одной транзакции."""
        async with self.session.begin():
            order = await self.session.get(Order, order_id)
            if not order:
                raise OrderNotFound(f"Заказ {order_id} не найден")

            payment = Payment(
                order_id=order_id,
                amount=amount,
                method=method,
                status="requested",
            )
            self.session.add(payment)
            await self.session.flush()

            await self.session.execute(
                update(Order).where(Order.id == order_id).values(status="payment_requested")
            )

        self.session.expunge(payment)
        return payment
