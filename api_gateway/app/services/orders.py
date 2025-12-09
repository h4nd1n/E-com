from ..config import settings
from ..kafka_client import KafkaPublisher
from ..repositories.orders import OrderRepository
from ..repositories.payments import PaymentRepository
from ..schemas import OrderCreate, PaymentRequest


class OrderService:
    def __init__(self, orders_repo: OrderRepository, publisher: KafkaPublisher):
        self.orders_repo = orders_repo
        self.publisher = publisher

    async def create_order(self, payload: OrderCreate):
        order = await self.orders_repo.create(
            item=payload.item, amount=payload.amount, currency=payload.currency
        )
        correlation_id = await self.publisher.publish_event(
            topic=settings.kafka_topic_orders,
            event_type="OrderCreated",
            payload={
                "order_id": order.id,
                "item": order.item,
                "amount": order.amount,
                "currency": order.currency,
                "service": settings.order_service_name,
            },
            key=str(order.id),
            source=settings.order_service_name,
        )
        await self.publisher.log_event(
            "OrderCreatedLog",
            {"order_id": order.id, "correlation_id": correlation_id},
        )
        return order


class PaymentService:
    def __init__(self, payments_repo: PaymentRepository, publisher: KafkaPublisher):
        self.payments_repo = payments_repo
        self.publisher = publisher

    async def request_payment(self, order_id: int, payload: PaymentRequest):
        payment = await self.payments_repo.request_payment(
            order_id=order_id, amount=payload.amount, method=payload.method
        )

        correlation_id = await self.publisher.publish_event(
            topic=settings.kafka_topic_payments,
            event_type="PaymentRequested",
            payload={
                "payment_id": payment.id,
                "order_id": order_id,
                "amount": payment.amount,
                "method": payment.method,
                "service": settings.payment_service_name,
            },
            key=str(order_id),
            source=settings.payment_service_name,
        )
        await self.publisher.log_event(
            "PaymentRequestedLog",
            {
                "payment_id": payment.id,
                "order_id": order_id,
                "correlation_id": correlation_id,
            },
        )
        return payment
