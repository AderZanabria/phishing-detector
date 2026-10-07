"""Métricas Prometheus del detector."""

from __future__ import annotations

import time

from fastapi import APIRouter, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from app.models.ml_model import ml_model

router = APIRouter(tags=["metrics"])

PREDICTIONS = Counter(
    "phishing_predictions_total",
    "Predicciones completadas.",
    ["is_phishing", "risk_level"],
)
LATENCY = Histogram(
    "prediction_latency_seconds",
    "Latencia de predict_url.",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
MODEL_LOADED = Gauge("model_loaded", "1 si el modelo está cargado.")
REQUESTS = Counter(
    "api_requests_total",
    "Peticiones HTTP observadas por la app.",
    ["method", "endpoint", "status"],
)


def record_prediction(is_phishing: bool, risk_level: str, elapsed: float) -> None:
    PREDICTIONS.labels(str(is_phishing).lower(), risk_level).inc()
    LATENCY.observe(elapsed)


def record_request(method: str, endpoint: str, status: int) -> None:
    REQUESTS.labels(method, endpoint, str(status)).inc()


class timed:
    """Context manager mínimo para la latencia de una predicción."""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start


@router.get("/metrics")
async def metrics() -> Response:
    MODEL_LOADED.set(1 if ml_model.loaded else 0)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Cuenta peticiones HTTP. No sustituye a los contadores de predicción."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        route = request.scope.get("route")
        endpoint = getattr(route, "path", request.url.path)
        record_request(request.method, endpoint, response.status_code)
        return response
