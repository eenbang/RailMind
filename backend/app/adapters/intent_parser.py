from __future__ import annotations

import re
from datetime import time
from typing import Protocol

from app.domain.models import SeatClass, TimeWindow, TravelRequestDraft


class IntentParser(Protocol):
    name: str

    def parse(self, text: str) -> tuple[TravelRequestDraft, tuple[str, ...]]:
        """Return a request draft and optional clarification messages."""


class RuleBasedIntentParser:
    """Predictable fallback used before an LLM adapter is connected."""

    name = "rule-based"

    def parse(self, text: str) -> tuple[TravelRequestDraft, tuple[str, ...]]:
        normalized = text.strip()
        origin, destination = _extract_route(normalized)
        price = _extract_price(normalized)
        departure_window = _extract_departure_window(normalized)
        seat_classes = _extract_seats(normalized)
        clarifications: list[str] = []
        if "点前到" in normalized or "之前到" in normalized:
            clarifications.append(
                "已识别到达时间要求；当前框架先保留该条件，等待接入更完整的意图模型。"
            )

        draft = TravelRequestDraft(
            origin=origin,
            destination=destination,
            departure_window=departure_window,
            max_price=price,
            seat_classes=seat_classes,
        )
        return draft, tuple(clarifications)


def _extract_route(text: str) -> tuple[str | None, str | None]:
    patterns = (
        r"(?:从\s*)?([\u4e00-\u9fff]{2,8}?)\s*(?:到|去|至)\s*([\u4e00-\u9fff]{2,8})",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            destination = re.split(
                r"(?:，|,|。|上午|下午|晚上|早上|中午|\d)",
                match.group(2),
                maxsplit=1,
            )[0]
            return match.group(1), destination
    return None, None


def _extract_price(text: str) -> float | None:
    match = re.search(r"(?:预算|不超过|最多)\s*(\d+(?:\.\d+)?)\s*元?", text)
    return float(match.group(1)) if match else None


def _extract_departure_window(text: str) -> TimeWindow | None:
    period = (
        ("早上", 6, 9),
        ("上午", 8, 12),
        ("中午", 11, 14),
        ("下午", 14, 18),
        ("晚上", 18, 23),
    )
    for keyword, start_hour, end_hour in period:
        if keyword in text:
            return TimeWindow(time(start_hour), time(end_hour, 59))
    explicit = re.search(
        r"(\d{1,2})(?::(\d{2}))?\s*(?:点)?(?:到|至|-|—)\s*"
        r"(\d{1,2})(?::(\d{2}))?\s*(?:点)?",
        text,
    )
    if explicit:
        return TimeWindow(
            time(int(explicit.group(1)), int(explicit.group(2) or 0)),
            time(int(explicit.group(3)), int(explicit.group(4) or 59)),
        )
    return None


def _extract_seats(text: str) -> tuple[SeatClass, ...]:
    if any(keyword in text for keyword in ("一等座", "商务座")):
        return (SeatClass.FIRST,)
    if "卧铺" in text:
        return (SeatClass.SOFT_SLEEPER, SeatClass.HARD_SLEEPER)
    if "硬座" in text:
        return (SeatClass.HARD_SEAT,)
    return (SeatClass.SECOND,)
