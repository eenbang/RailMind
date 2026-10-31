from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.journey_repository import default_repository
from app.api.routes.assistant import router as assistant_router
from app.api.routes.journeys import router as journeys_router
from app.api.routes.recommendations import router as recommendations_router
from app.domain.recommendation import RecommendationEngine

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    app = FastAPI(
        title="RailMind API",
        version="0.1.0",
        description="Railway journey recommendation framework",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(assistant_router, prefix=API_PREFIX)
    app.include_router(journeys_router, prefix=API_PREFIX)
    app.include_router(recommendations_router, prefix=API_PREFIX)

    @app.get("/health")
    def health() -> dict[str, str]:
        repository = default_repository()
        return {
            "status": "ok",
            "data_version": repository.data_version,
            "algorithm_version": RecommendationEngine().algorithm_version,
        }

    return app


app = create_app()
