from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import get_recommendation_service
from app.api.schemas import (
    DimensionScoresResponse,
    JourneyResponse,
    RecommendationRequestSchema,
    RecommendationResponse,
    RecommendationResultResponse,
    RelaxationSuggestionResponse,
)

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResultResponse)
def recommend(
    payload: RecommendationRequestSchema,
) -> RecommendationResultResponse:
    service = get_recommendation_service()
    result = service.run(payload.request.to_domain(), limit=payload.limit)
    return RecommendationResultResponse(
        recommendations=[
            RecommendationResponse(
                journey=JourneyResponse.from_domain(item.journey),
                selected_fare=item.selected_fare,
                score=item.score,
                dimension_scores=DimensionScoresResponse.from_domain(
                    item.dimension_scores
                ),
                reasons=list(item.reasons),
                tradeoffs=list(item.tradeoffs),
                confidence=item.confidence,
            )
            for item in result.recommendations
        ],
        candidate_count=result.candidate_count,
        filtered_count=result.filtered_count,
        relaxation_suggestions=[
            RelaxationSuggestionResponse(
                field=item.field,
                suggested_value=item.suggested_value,
                reason=item.reason,
            )
            for item in result.relaxation_suggestions
        ],
        algorithm_version=result.algorithm_version,
        data_version=result.data_version,
    )
