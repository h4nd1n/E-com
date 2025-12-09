import httpx

from ..config import settings
from ..kafka_client import KafkaPublisher
from ..schemas import AnalyticsRequest, AnalyticsResult


class AnalyticsService:
    def __init__(self, publisher: KafkaPublisher):
        self.publisher = publisher

    async def request_analytics(self, payload: AnalyticsRequest) -> AnalyticsResult:
        """Делаем HTTP-запрос в analytics-service и логируем событие в Kafka."""
        params = {
            "metric": payload.metric,
            "from_ts": payload.from_ts,
            "to_ts": payload.to_ts,
            "limit": payload.limit,
        }
        async with httpx.AsyncClient(base_url=settings.analytics_service_url, timeout=5.0) as client:
            response = await client.get("/analytics", params=params)
            response.raise_for_status()
            data = response.json()

        await self.publisher.log_event(
            "AnalyticsHttpRequested",
            {"metric": payload.metric, "status": "ok"},
        )

        return AnalyticsResult(data=data)
