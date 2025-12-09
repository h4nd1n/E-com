import asyncio
import logging

from orders_service import config
from orders_service.application.service import OrderCommandService
from orders_service.deps import build_dependencies, consume_commands

log = logging.getLogger("order_service")


async def bootstrap() -> None:
    deps = await build_dependencies()
    service = OrderCommandService(uow_factory=deps.uow_factory, publisher=deps.publisher)

    log.info("Order service started, listening commands topic %s", config.settings.commands_topic)
    await consume_commands(deps.consumer, service.handle_command)


def main() -> None:
    asyncio.run(bootstrap())


if __name__ == "__main__":
    main()
