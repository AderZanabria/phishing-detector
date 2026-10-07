"""Dependencias de FastAPI."""

from __future__ import annotations

from app.models.ml_model import MLModelLoader, ml_model


def get_ml_model() -> MLModelLoader:
    """Devuelve el singleton cargado en el arranque."""
    return ml_model
