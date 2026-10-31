from __future__ import annotations

from functools import lru_cache

from app.adapters.journey_repository import (
    JourneyRepository,
    default_repository,
)
from app.domain.recommendation import RecommendationEngine
from app.services.recommendation_service import RecommendationService


@lru_cache(maxsize=1)
def get_journey_repository() -> JourneyRepository:
    return default_repository()


@lru_cache(maxsize=1)
def get_recommendation_service() -> RecommendationService:
    return RecommendationService(
        repository=get_journey_repository(),
        engine=RecommendationEngine(),
    )
