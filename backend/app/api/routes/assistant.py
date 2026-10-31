from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from app.adapters.intent_parser import RuleBasedIntentParser
from app.api.schemas import AssistantParseRequest, AssistantParseResponse

router = APIRouter(tags=["assistant"])


@router.post("/assistant/parse", response_model=AssistantParseResponse)
def parse_intent(payload: AssistantParseRequest) -> AssistantParseResponse:
    parser = RuleBasedIntentParser()
    draft, clarifications = parser.parse(payload.text)
    return AssistantParseResponse(
        request_draft=asdict(draft),
        missing_fields=list(draft.missing_fields),
        clarifications=list(clarifications),
        parser=parser.name,
    )
