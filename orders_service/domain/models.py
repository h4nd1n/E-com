from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class OrderEventRecord:
    order_id: str
    type: str
    payload: dict[str, Any]
    id: int | None = None
    created_at: datetime | None = None


@dataclass
class OrderStateRecord:
    order_id: str
    status: str
    updated_at: datetime | None = None
