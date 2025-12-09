from pydantic import BaseModel, Field
from typing import Optional


class OrderCreate(BaseModel):
    item: str = Field(..., description="Название товара")
    amount: float = Field(..., gt=0, description="Сумма заказа")
    currency: str = Field(..., min_length=3, max_length=3, description="Код валюты ISO")


class OrderOut(BaseModel):
    id: int
    status: str = "created"


class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма оплаты")
    method: str = Field(..., description="Способ оплаты")


class PaymentOut(BaseModel):
    id: int
    status: str


class AnalyticsRequest(BaseModel):
    metric: str
    from_ts: Optional[str] = Field(None, description="ISO метка начала периода")
    to_ts: Optional[str] = Field(None, description="ISO метка конца периода")
    limit: int = Field(100, ge=1, le=1000, description="Лимит строк")


class AnalyticsAck(BaseModel):
    status: str
    correlation_id: str


class AnalyticsResult(BaseModel):
    data: dict
