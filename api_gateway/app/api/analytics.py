from fastapi import APIRouter, Query

from ..deps import AnalyticsServiceDep
from ..schemas import AnalyticsRequest, AnalyticsResult

router = APIRouter(tags=["analytics"])


@router.get(
    "/analytics/{metric}",
    response_model=AnalyticsResult,
    summary="Запросить аналитические данные (HTTP к analytics-service)",
)
async def analytics_request(
    metric: str,
    service: AnalyticsServiceDep,
    from_ts: str | None = Query(None, description="Начало периода (ISO)"),
    to_ts: str | None = Query(None, description="Конец периода (ISO)"),
    limit: int = Query(100, ge=1, le=1000, description="Лимит строк"),
) -> AnalyticsResult:
    payload = AnalyticsRequest(metric=metric, from_ts=from_ts, to_ts=to_ts, limit=limit)
    return await service.request_analytics(payload)
