"""Endpoints de predicción individual y por lote."""

from __future__ import annotations

import asyncio
import logging
import time

from fastapi import APIRouter, HTTPException, status

from app.models.ml_model import ModelNotLoadedError
from app.models.schemas import (
    BatchPredictRequest,
    BatchPredictResponse,
    PredictRequest,
    PredictResponse,
)
from app.api.routes.metrics import record_prediction
from app.services.predictor import InvalidURLError, PredictionError, predict_url

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["predict"])


def _http_error(exc: Exception) -> HTTPException:
    """Traduce errores de dominio a códigos HTTP."""
    if isinstance(exc, InvalidURLError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, PredictionError) and isinstance(exc.__cause__, ModelNotLoadedError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    if isinstance(exc, PredictionError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    logger.exception("Error no controlado en predicción")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error interno al puntuar la URL.",
    )


@router.post("", response_model=PredictResponse)
async def predict(payload: PredictRequest) -> PredictResponse:
    """Clasifica una URL. 1 = phishing en el modelo subyacente."""
    started = time.perf_counter()
    try:
        result = await asyncio.to_thread(predict_url, payload.url)
        record_prediction(result["is_phishing"], result["risk_level"], time.perf_counter() - started)
        return PredictResponse(**result)
    except (InvalidURLError, PredictionError) as exc:
        raise _http_error(exc) from exc


@router.post("/batch", response_model=BatchPredictResponse)
async def predict_batch(payload: BatchPredictRequest) -> BatchPredictResponse:
    """Puntúa hasta 100 URLs. Una URL inválida no aborta el lote."""
    results: list[PredictResponse] = []
    errors: list[dict[str, str]] = []
    for url in payload.urls:
        started = time.perf_counter()
        try:
            item = await asyncio.to_thread(predict_url, url)
            record_prediction(item["is_phishing"], item["risk_level"], time.perf_counter() - started)
            results.append(PredictResponse(**item))
        except (InvalidURLError, PredictionError) as exc:
            logger.info("URL omitida en el lote: %s (%s)", url, exc)
            errors.append({"url": url, "detail": str(exc)})
        except Exception as exc:  # noqa: BLE001
            logger.exception("Fallo inesperado en el lote para %s", url)
            errors.append({"url": url, "detail": f"Error interno: {exc}"})
    if not results and errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Ninguna URL del lote pudo puntuarse.", "errors": errors},
        )
    return BatchPredictResponse(results=results, errors=errors)
