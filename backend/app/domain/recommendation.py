from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.models import (
    DimensionScores,
    Recommendation,
    RecommendationResult,
    RelaxationSuggestion,
    SeatClass,
    TrainJourney,
    TravelRequest,
)


@dataclass(frozen=True, slots=True)
class RecommendationEngine:
    """Deterministic baseline that can later be replaced or extended."""

    algorithm_version: str = "weighted-v1"

    def recommend(
        self,
        journeys: tuple[TrainJourney, ...],
        request: TravelRequest,
        limit: int = 3,
    ) -> RecommendationResult:
        route_matches = tuple(
            journey
            for journey in journeys
            if _station_matches(request.origin, journey.departure_station)
            and _station_matches(request.destination, journey.arrival_station)
        )
        eligible = self.filter_candidates(route_matches, request)
        if not eligible:
            return RecommendationResult(
                recommendations=(),
                candidate_count=len(route_matches),
                filtered_count=0,
                relaxation_suggestions=_relaxation_suggestions(
                    route_matches, request
                ),
                algorithm_version=self.algorithm_version,
            )

        scored = [
            self._score(journey, eligible, request)
            for journey in eligible
        ]
        scored.sort(key=lambda item: (-item.score, item.journey.departure_time))

        return RecommendationResult(
            recommendations=tuple(scored[:limit]),
            candidate_count=len(route_matches),
            filtered_count=len(eligible),
            algorithm_version=self.algorithm_version,
        )

    def filter_candidates(
        self,
        journeys: tuple[TrainJourney, ...],
        request: TravelRequest,
    ) -> tuple[TrainJourney, ...]:
        """Apply route and hard constraints without ranking."""
        return tuple(
            journey
            for journey in journeys
            if _station_matches(request.origin, journey.departure_station)
            and _station_matches(request.destination, journey.arrival_station)
            and self._passes_hard_constraints(journey, request)
        )

    def _passes_hard_constraints(
        self, journey: TrainJourney, request: TravelRequest
    ) -> bool:
        fare = journey.fare_for(request.seat_classes)
        if fare is None:
            return False
        if request.max_price is not None and fare > request.max_price:
            return False
        if (
            request.max_duration_minutes is not None
            and journey.duration_minutes > request.max_duration_minutes
        ):
            return False
        if (
            request.departure_window is not None
            and not request.departure_window.contains(journey.departure_time)
        ):
            return False
        if (
            request.arrival_deadline is not None
            and journey.arrival_time > request.arrival_deadline
        ):
            return False
        return True

    def _score(
        self,
        journey: TrainJourney,
        candidates: tuple[TrainJourney, ...],
        request: TravelRequest,
    ) -> Recommendation:
        fare = journey.fare_for(request.seat_classes)
        assert fare is not None
        fares = [
            candidate.fare_for(request.seat_classes)
            for candidate in candidates
        ]
        durations = [candidate.duration_minutes for candidate in candidates]

        price_score = _inverse_normalize(
            fare, min(value for value in fares if value is not None),
            max(value for value in fares if value is not None)
        )
        duration_score = _inverse_normalize(
            journey.duration_minutes, min(durations), max(durations)
        )
        comfort_score = _comfort_score(journey, request.seat_classes)
        schedule_score = _schedule_score(journey, request)

        dimensions = DimensionScores(
            price=round(price_score, 1),
            duration=round(duration_score, 1),
            comfort=round(comfort_score, 1),
            schedule=round(schedule_score, 1),
        )
        score = sum(
            getattr(dimensions, dimension) * weight
            for dimension, weight in request.weights.items()
        )

        avg_price = sum(value for value in fares if value is not None) / len(fares)
        avg_duration = sum(durations) / len(durations)
        reasons: list[str] = []
        tradeoffs: list[str] = []

        if fare < avg_price:
            reasons.append(f"票价 {fare:g} 元，低于候选车次均价")
        if journey.duration_minutes <= avg_duration:
            reasons.append(f"{journey.duration_minutes} 分钟直达，耗时较短")
        if request.departure_window and schedule_score >= 90:
            reasons.append("出发时间贴合你的偏好")
        if comfort_score >= 75:
            reasons.append("车型和座席舒适度较好")

        if fare > avg_price:
            tradeoffs.append("价格高于当前候选车次的平均水平")
        if journey.duration_minutes > avg_duration:
            tradeoffs.append("用时高于当前候选车次的平均水平")

        return Recommendation(
            journey=journey,
            selected_fare=round(fare, 1),
            score=round(score, 1),
            dimension_scores=dimensions,
            reasons=tuple(reasons[:3] or ["在当前条件下综合表现均衡"]),
            tradeoffs=tuple(tradeoffs[:2]),
            confidence=0.9,
        )


_CITY_STATIONS = {
    "上海": (
        "上海",
        "上海虹桥",
        "上海南",
        "上海松江",
        "上海西",
        "金山北",
        "练塘",
    ),
    "杭州": ("杭州", "杭州东", "杭州西", "杭州南"),
}


def _station_matches(query: str, station: str) -> bool:
    normalized_query = query.replace("市", "").strip()
    normalized_station = station.replace("市", "").strip()
    aliases = _CITY_STATIONS.get(normalized_query)
    if aliases is not None:
        return any(alias in normalized_station for alias in aliases)
    return normalized_query in normalized_station


def _inverse_normalize(value: float, minimum: float, maximum: float) -> float:
    if maximum == minimum:
        return 100.0
    return (maximum - value) / (maximum - minimum) * 100


def _comfort_score(
    journey: TrainJourney, seat_classes: tuple[SeatClass, ...]
) -> float:
    train_score = {
        "高速动车": 88,
        "城际高速": 86,
        "高速": 84,
        "动车组": 78,
        "动车": 74,
        "新空调直达": 62,
        "新空调直快": 58,
        "新空调快速": 55,
        "普速": 48,
    }
    seat_score = {
        SeatClass.FIRST: 96,
        SeatClass.SECOND: 82,
        SeatClass.SOFT_SLEEPER: 88,
        SeatClass.HARD_SLEEPER: 70,
        SeatClass.HARD_SEAT: 52,
    }
    base = next(
        (
            value
            for label, value in train_score.items()
            if label in journey.train_type
        ),
        60,
    )
    seats = [
        seat_score[seat]
        for seat in seat_classes
        if seat in journey.fares
    ]
    selected_seat = max(seats) if seats else min(seat_score.values())
    return round(base * 0.7 + selected_seat * 0.3, 1)


def _schedule_score(journey: TrainJourney, request: TravelRequest) -> float:
    if request.departure_window is None:
        return 75.0
    if request.departure_window.contains(journey.departure_time):
        return 100.0
    start = request.departure_window.start.hour * 60 + request.departure_window.start.minute
    end = request.departure_window.end.hour * 60 + request.departure_window.end.minute
    current = journey.departure_time.hour * 60 + journey.departure_time.minute
    midpoint = (start + end) / 2
    distance = min(abs(current - midpoint), 720)
    return max(0.0, 100 - distance / 3)


def _relaxation_suggestions(
    candidates: tuple[TrainJourney, ...], request: TravelRequest
) -> tuple[RelaxationSuggestion, ...]:
    suggestions: list[RelaxationSuggestion] = []
    fares = [
        fare
        for journey in candidates
        if (fare := journey.fare_for(request.seat_classes)) is not None
    ]
    if request.max_price is not None and fares:
        cheapest_over_budget = min(
            (fare for fare in fares if fare > request.max_price),
            default=None,
        )
        if cheapest_over_budget is not None:
            suggestions.append(
                RelaxationSuggestion(
                    field="max_price",
                    suggested_value=cheapest_over_budget,
                    reason=f"预算至少提高到 {cheapest_over_budget:g} 元才会出现可选座席",
                )
            )

    if request.max_duration_minutes is not None and candidates:
        shortest = min(journey.duration_minutes for journey in candidates)
        if shortest > request.max_duration_minutes:
            suggestions.append(
                RelaxationSuggestion(
                    field="max_duration_minutes",
                    suggested_value=shortest,
                    reason=f"当前线路最快通达时间为 {shortest} 分钟",
                )
            )
    return tuple(suggestions)
