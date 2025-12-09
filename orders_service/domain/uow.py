from typing import AsyncContextManager, Callable, Protocol

from .repositories import OrderEventRepository, OrderStateRepository


class OrderUnitOfWork(Protocol):
    events: OrderEventRepository
    state: OrderStateRepository

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...


UoWFactory = Callable[[], AsyncContextManager[OrderUnitOfWork]]
