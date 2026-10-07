"""Orquesta validación, features, modelo y explicación."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.models.ml_model import ModelNotLoadedError, ml_model
from app.services.feature_extractor import FeatureExtractionError, extract_features
from app.services.preprocessing import normalize_url, validate_url
from app.utils.explanations import generate_explanation

logger = logging.getLogger(__name__)


class InvalidURLError(ValueError):
    """La URL no pasa la validación mínima."""


class PredictionError(RuntimeError):
    """Fallo interno al puntuar una URL válida."""


def _risk_level(probability: float) -> str:
    if probability < 0.3:
        return "low"
    if probability <= 0.7:
        return "medium"
    return "high"


def predict_url(url: str) -> dict:
    """Clasifica una URL. 1 = phishing en el modelo.

    Raises:
        InvalidURLError: URL vacía o malformada.
        PredictionError: modelo ausente o fallo de inferencia.
    """
    if not validate_url(url):
        raise InvalidURLError("La URL está vacía o no tiene un dominio válido.")

    normalized = normalize_url(url)
    try:
        features = extract_features(normalized)
        probability = ml_model.predict(features)
    except (FeatureExtractionError, ModelNotLoadedError) as exc:
        raise PredictionError(str(exc)) from exc
    except Exception as exc:
        logger.exception("Fallo al predecir %s", normalized)
        raise PredictionError(f"El modelo no pudo puntuar la URL: {exc}") from exc

    threshold = get_settings().decision_threshold
    is_phishing = probability >= threshold
    confidence = probability if is_phishing else 1.0 - probability
    return {
        "url": normalized,
        "is_phishing": is_phishing,
        "confidence": round(confidence, 6),
        "probability_phishing": round(probability, 6),
        "probability_legit": round(1.0 - probability, 6),
        "risk_level": _risk_level(probability),
        "features": features,
        "explanation": generate_explanation(features, probability),
    }
