from __future__ import annotations

from dataclasses import dataclass

from app.adapters.journey_repository import JourneyRepository
from app.domain.models import RecommendationResult, TravelRequest
from app.domain.recommendation import RecommendationEngine


@dataclass(slots=True)
class RecommendationService:
    repository: JourneyRepository
    engine: RecommendationEngine

    def run(
        self, request: TravelRequest, limit: int = 3
    ) -> RecommendationResult:
        journeys = self.repository.all()
        result = self.engine.recommend(journeys, request, limit=limit)
        return RecommendationResult(
            recommendations=result.recommendations,
            candidate_count=result.candidate_count,
            filtered_count=result.filtered_count,
            relaxation_suggestions=result.relaxation_suggestions,
            algorithm_version=result.algorithm_version,
            data_version=self.repository.data_version,
        )
