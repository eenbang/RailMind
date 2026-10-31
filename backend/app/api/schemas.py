from __future__ import annotations

from datetime import time

from pydantic import BaseModel, Field, field_validator

from app.domain.models import (
    DimensionScores,
    PreferenceWeights,
    SeatClass,
    TimeWindow,
    TrainJourney,
    TravelRequest,
)


class TimeWindowSchema(BaseModel):
    start: time
    end: time

    def to_domain(self) -> TimeWindow:
        return TimeWindow(start=self.start, end=self.end)


class WeightsSchema(BaseModel):
    price: float = Field(default=0.30, ge=0, le=1)
    duration: float = Field(default=0.35, ge=0, le=1)
    comfort: float = Field(default=0.20, ge=0, le=1)
    schedule: float = Field(default=0.15, ge=0, le=1)

    @field_validator("schedule")
    @classmethod
    def weights_total_must_be_one(cls, value: float, info):
        data = info.data
        total = sum(data.values()) + value
        if abs(total - 1.0) > 0.001:
            raise ValueError("weight values must sum to 1")
        return value

    def to_domain(self) -> PreferenceWeights:
        return PreferenceWeights(
            price=self.price,
            duration=self.duration,
            comfort=self.comfort,
            schedule=self.schedule,
        )


class TravelRequestSchema(BaseModel):
    origin: str
    destination: str
    departure_window: TimeWindowSchema | None = None
    arrival_deadline: time | None = None
    max_price: float | None = Field(default=None, ge=0)
    max_duration_minutes: int | None = Field(default=None, ge=1)
    seat_classes: list[SeatClass] = Field(default_factory=lambda: [SeatClass.SECOND])
    weights: WeightsSchema = Field(default_factory=WeightsSchema)

    def to_domain(self) -> TravelRequest:
        return TravelRequest(
            origin=self.origin,
            destination=self.destination,
            departure_window=(
                self.departure_window.to_domain()
                if self.departure_window
                else None
            ),
            arrival_deadline=self.arrival_deadline,
            max_price=self.max_price,
            max_duration_minutes=self.max_duration_minutes,
            seat_classes=tuple(self.seat_classes),
            weights=self.weights.to_domain(),
        )


class RecommendationRequestSchema(BaseModel):
    request: TravelRequestSchema
    limit: int = Field(default=3, ge=1, le=20)
    include_candidates: bool = False


class JourneySearchRequestSchema(BaseModel):
    request: TravelRequestSchema
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class JourneyResponse(BaseModel):
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

    @classmethod
    def from_domain(cls, journey: TrainJourney) -> "JourneyResponse":
        return cls(
            id=journey.id,
            train_no=journey.train_no,
            departure_station=journey.departure_station,
            arrival_station=journey.arrival_station,
            departure_time=journey.departure_time,
            arrival_time=journey.arrival_time,
            duration_minutes=journey.duration_minutes,
            fares=journey.fares,
            mileage_km=journey.mileage_km,
            route_origin=journey.route_origin,
            route_terminal=journey.route_terminal,
            train_type=journey.train_type,
        )


class JourneySearchResponse(BaseModel):
    journeys: list[JourneyResponse]
    total: int
    page: int
    page_size: int


class DimensionScoresResponse(BaseModel):
    price: float
    duration: float
    comfort: float
    schedule: float

    @classmethod
    def from_domain(cls, scores: DimensionScores) -> "DimensionScoresResponse":
        return cls(
            price=scores.price,
            duration=scores.duration,
            comfort=scores.comfort,
            schedule=scores.schedule,
        )


class RecommendationResponse(BaseModel):
    journey: JourneyResponse
    selected_fare: float
    score: float
    dimension_scores: DimensionScoresResponse
    reasons: list[str]
    tradeoffs: list[str]
    confidence: float


class RelaxationSuggestionResponse(BaseModel):
    field: str
    suggested_value: str | int | float
    reason: str


class RecommendationResultResponse(BaseModel):
    recommendations: list[RecommendationResponse]
    candidate_count: int
    filtered_count: int
    relaxation_suggestions: list[RelaxationSuggestionResponse]
    algorithm_version: str
    data_version: str


class AssistantParseRequest(BaseModel):
    text: str = Field(min_length=2, max_length=500)


class AssistantParseResponse(BaseModel):
    request_draft: dict
    missing_fields: list[str]
    clarifications: list[str]
    parser: str
