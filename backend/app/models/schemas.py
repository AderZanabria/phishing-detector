"""Contratos de entrada y salida de la API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """URL a clasificar."""

    url: str = Field(
        ...,
        min_length=1,
        description="URL completa o dominio. Si no trae esquema se asume http://.",
        examples=["https://login-paypal.example.com/account"],
    )


class BatchPredictRequest(BaseModel):
    """Lote de URLs."""

    urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Entre 1 y 100 URLs.",
        examples=[["https://example.com", "http://192.168.0.1/login.php"]],
    )


class PredictResponse(BaseModel):
    """Resultado de una predicción. label positiva = phishing."""

    url: str = Field(..., description="URL normalizada que se puntuó.")
    is_phishing: bool = Field(..., description="True si la probabilidad supera el umbral.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Probabilidad de la clase predicha.")
    probability_phishing: float = Field(..., ge=0.0, le=1.0, description="P(phishing). Clase 1 del modelo.")
    probability_legit: float = Field(..., ge=0.0, le=1.0, description="P(legítima). Clase 0 del modelo.")
    risk_level: Literal["low", "medium", "high"] = Field(..., description="low < 0.3, medium 0.3-0.7, high > 0.7.")
    features: dict[str, float] = Field(..., description="Features en el orden del modelo.")
    explanation: list[str] = Field(..., description="Señales heurísticas legibles.")


class HealthResponse(BaseModel):
    """Estado del proceso y del modelo."""

    status: Literal["ok", "degraded"] = Field(..., examples=["ok"])
    model_loaded: bool = Field(..., examples=[True])
    version: str = Field(..., examples=["1.0.0"])


class BatchItemError(BaseModel):
    """URL del lote que no se pudo puntuar."""

    url: str
    detail: str


class BatchPredictResponse(BaseModel):
    """Predicciones válidas y errores por URL. Un fallo no aborta el lote."""

    results: list[PredictResponse] = Field(default_factory=list)
    errors: list[BatchItemError] = Field(default_factory=list)
