from environs import Env
from pydantic import BaseModel


env = Env()
env.read_env()


class Settings(BaseModel):
    app_name: str = env.str("APP_NAME", "api-gateway")
    kafka_bootstrap_servers: str = env.str("KAFKA_BOOTSTRAP", "localhost:9092")
    kafka_topic_orders: str = env.str("KAFKA_TOPIC_ORDERS", "orders")
    kafka_topic_payments: str = env.str("KAFKA_TOPIC_PAYMENTS", "payments")
    kafka_topic_logs: str = env.str("KAFKA_TOPIC_LOGS", "logs")
    kafka_topic_analytics: str = env.str("KAFKA_TOPIC_ANALYTICS", "analytics-requests")
    order_service_name: str = env.str("ORDER_SERVICE_NAME", "order-service")
    payment_service_name: str = env.str("PAYMENT_SERVICE_NAME", "payment-service")
    analytics_service_name: str = env.str("ANALYTICS_SERVICE_NAME", "analytics-service")
    analytics_service_url: str = env.str("ANALYTICS_SERVICE_URL", "http://analytics-service:8000")
    database_url: str = env.str("DATABASE_URL", "sqlite+aiosqlite:///./data/gateway.db")


settings = Settings()
