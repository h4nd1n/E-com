from fastapi import APIRouter, HTTPException

from ..deps import OrderServiceDep, PaymentServiceDep
from ..errors import OrderNotFound
from ..schemas import OrderCreate, OrderOut, PaymentOut, PaymentRequest

router = APIRouter(tags=["orders"])


@router.post("/orders", response_model=OrderOut, summary="Создать заказ")
async def create_order(
    payload: OrderCreate,
    service: OrderServiceDep,
) -> OrderOut:
    order = await service.create_order(payload)
    return OrderOut(id=order.id, status=order.status)


@router.post(
    "/orders/{order_id}/pay",
    response_model=PaymentOut,
    summary="Инициировать оплату",
)
async def pay_order(
    order_id: int,
    payload: PaymentRequest,
    service: PaymentServiceDep,
) -> PaymentOut:
    try:
        payment = await service.request_payment(order_id, payload)
    except OrderNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return PaymentOut(id=payment.id, status=payment.status)
