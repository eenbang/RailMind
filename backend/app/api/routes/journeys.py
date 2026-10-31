from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import get_journey_repository
from app.api.schemas import (
    JourneyResponse,
    JourneySearchRequestSchema,
    JourneySearchResponse,
)
from app.domain.recommendation import RecommendationEngine

router = APIRouter(tags=["journeys"])


@router.post("/journeys/search", response_model=JourneySearchResponse)
def search_journeys(
    payload: JourneySearchRequestSchema,
) -> JourneySearchResponse:
    request = payload.request.to_domain()
    candidates = RecommendationEngine().filter_candidates(
        get_journey_repository().all(), request
    )
    candidates = tuple(
        sorted(candidates, key=lambda journey: journey.departure_time)
    )
    start = (payload.page - 1) * payload.page_size
    end = start + payload.page_size
    return JourneySearchResponse(
        journeys=[
            JourneyResponse.from_domain(journey)
            for journey in candidates[start:end]
        ],
        total=len(candidates),
        page=payload.page,
        page_size=payload.page_size,
    )
