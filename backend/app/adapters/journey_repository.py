from __future__ import annotations

import re
from datetime import time
from pathlib import Path
from typing import Protocol

from app.domain.models import SeatClass, TrainJourney


class JourneyRepository(Protocol):
    data_version: str

    def all(self) -> tuple[TrainJourney, ...]:
        """Return all journeys in the active data snapshot."""


class TextJourneyRepository:
    """Development adapter for the checked-in Shanghai–Hangzhou sample."""

    data_version = "sh_to_hz.sample"

    def __init__(self, path: Path) -> None:
        self._path = path
        self._cache: tuple[TrainJourney, ...] | None = None

    def all(self) -> tuple[TrainJourney, ...]:
        if self._cache is None:
            self._cache = tuple(parse_journeys(self._path.read_text(encoding="utf-8")))
        return self._cache


def default_repository() -> TextJourneyRepository:
    root = Path(__file__).resolve().parents[3]
    return TextJourneyRepository(root / "data" / "sh_to_hz.txt")


def parse_journeys(text: str) -> list[TrainJourney]:
    blocks = re.split(r"(?m)^\d+:\s*$", text)[1:]
    journeys: list[TrainJourney] = []
    for index, block in enumerate(blocks, start=1):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        values: dict[str, str] = {}
        train_no = lines[0]
        for line in lines[1:]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            values[key] = value

        fares = _parse_fares(values)
        journeys.append(
            TrainJourney(
                id=f"sample-{index:03d}",
                train_no=train_no,
                departure_station=_required(values, "出发车站"),
                arrival_station=_required(values, "到达车站"),
                departure_time=time.fromisoformat(_required(values, "开点")),
                arrival_time=time.fromisoformat(_required(values, "到点")),
                duration_minutes=_duration_minutes(_required(values, "历时")),
                fares=fares,
                mileage_km=int(float(_required(values, "里程"))),
                route_origin=_required(values, "起始站"),
                route_terminal=_required(values, "终点站"),
                train_type=_required(values, "车次类型"),
            )
        )
    return journeys


def _required(values: dict[str, str], key: str) -> str:
    value = values.get(key)
    if value is None:
        raise ValueError(f"Travel record is missing {key!r}")
    return value


def _duration_minutes(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def _parse_fares(values: dict[str, str]) -> dict[SeatClass, float]:
    mappings = {
        "二等座": SeatClass.SECOND,
        "一等座": SeatClass.FIRST,
        "硬座": SeatClass.HARD_SEAT,
        "硬卧 上/中/下": SeatClass.HARD_SLEEPER,
        "软卧 上/下": SeatClass.SOFT_SLEEPER,
    }
    fares: dict[SeatClass, float] = {}
    for source_key, seat_class in mappings.items():
        raw = values.get(source_key)
        if raw is None:
            continue
        numbers = re.findall(r"\d+(?:\.\d+)?", raw)
        if numbers:
            fares[seat_class] = min(float(number) for number in numbers)
    return fares
