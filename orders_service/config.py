from environs import Env
from pydantic import BaseModel

env = Env()
env.read_env()


class Settings(BaseModel):
    service_name: str = env.str("ORDER_SERVICE_NAME", "order-service")
    kafka_bootstrap_servers: str = env.str("KAFKA_BOOTSTRAP", "localhost:9092")
    commands_topic: str = env.str("ORDERS_COMMANDS_TOPIC", "orders_commands")
    events_topic: str = env.str("ORDERS_EVENTS_TOPIC", "orders_events")
    database_url: str = env.str("ORDERS_DATABASE_URL", "sqlite+aiosqlite:///./data/orders.db")


settings = Settings()
