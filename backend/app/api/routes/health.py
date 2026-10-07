"""Estado del servicio."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.models.ml_model import ml_model
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """ok si el modelo cargó; degraded si el .pkl no está disponible."""
    loaded = ml_model.loaded
    return HealthResponse(
        status="ok" if loaded else "degraded",
        model_loaded=loaded,
        version=get_settings().app_version,
    )
