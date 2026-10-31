from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from enum import StrEnum


class SeatClass(StrEnum):
    SECOND = "second"
    FIRST = "first"
    HARD_SEAT = "hard_seat"
    HARD_SLEEPER = "hard_sleeper"
    SOFT_SLEEPER = "soft_sleeper"


@dataclass(frozen=True, slots=True)
class TimeWindow:
    start: time
    end: time

    def contains(self, value: time) -> bool:
        return self.start <= value <= self.end


@dataclass(frozen=True, slots=True)
class PreferenceWeights:
    price: float = 0.30
    duration: float = 0.35
    comfort: float = 0.20
    schedule: float = 0.15

    def items(self) -> tuple[tuple[str, float], ...]:
        return (
            ("price", self.price),
            ("duration", self.duration),
            ("comfort", self.comfort),
            ("schedule", self.schedule),
        )

    def total(self) -> float:
        return sum(value for _, value in self.items())


@dataclass(frozen=True, slots=True)
class TrainJourney:
    id: str
    train_no: str
    departure_station: str
    arrival_station: str
    departure_time: time
    arrival_time: time
    duration_minutes: int
    fares: dict[SeatClass, float]
    mileage_km: int
    route_origin: str
    route_terminal: str
    train_type: str

    def fare_for(self, seat_classes: tuple[SeatClass, ...]) -> float | None:
        if not seat_classes:
            available = list(self.fares.values())
            return min(available) if available else None
        fares = [
            self.fares[seat]
            for seat in seat_classes
            if seat in self.fares
        ]
        return min(fares) if fares else None


@dataclass(frozen=True, slots=True)
class TravelRequest:
    origin: str
    destination: str
    departure_window: TimeWindow | None = None
    arrival_deadline: time | None = None
    max_price: float | None = None
    max_duration_minutes: int | None = None
    seat_classes: tuple[SeatClass, ...] = (SeatClass.SECOND,)
    weights: PreferenceWeights = field(default_factory=PreferenceWeights)


@dataclass(frozen=True, slots=True)
class TravelRequestDraft:
    """A partially parsed request before clarification is complete."""

    origin: str | None = None
    destination: str | None = None
    departure_window: TimeWindow | None = None
    arrival_deadline: time | None = None
    max_price: float | None = None
    max_duration_minutes: int | None = None
    seat_classes: tuple[SeatClass, ...] = (SeatClass.SECOND,)
    weights: PreferenceWeights = field(default_factory=PreferenceWeights)

    @property
    def missing_fields(self) -> tuple[str, ...]:
        fields: list[str] = []
        if not self.origin:
            fields.append("origin")
        if not self.destination:
            fields.append("destination")
        return tuple(fields)


@dataclass(frozen=True, slots=True)
class DimensionScores:
    price: float
    duration: float
    comfort: float
    schedule: float


@dataclass(frozen=True, slots=True)
class Recommendation:
    journey: TrainJourney
    selected_fare: float
    score: float
    dimension_scores: DimensionScores
    reasons: tuple[str, ...]
    tradeoffs: tuple[str, ...]
    confidence: float


@dataclass(frozen=True, slots=True)
class RelaxationSuggestion:
    field: str
    suggested_value: str | int | float
    reason: str


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    recommendations: tuple[Recommendation, ...]
    candidate_count: int
    filtered_count: int
    relaxation_suggestions: tuple[RelaxationSuggestion, ...] = ()
    algorithm_version: str = "weighted-v1"
    data_version: str = "sh_to_hz.sample"
