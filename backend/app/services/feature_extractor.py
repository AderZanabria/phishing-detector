"""Adaptador sobre el extractor de la fase de ML.

No se duplica la lógica. Se importa extract_features_from_url de
ml.src.features.build_features, que ya devuelve las 16 features en el
orden de FEATURE_COLUMNS. La raíz del repo se añade a sys.path para que
el paquete `ml` sea importable tanto en local como en Docker (PYTHONPATH=/app).
"""

from __future__ import annotations

import sys
from pathlib import Path

from app.core.config import PROJECT_ROOT
from app.models.ml_model import ml_model
from app.services.preprocessing import normalize_url

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.src.features.build_features import extract_features_from_url  # noqa: E402


class FeatureExtractionError(ValueError):
    """La URL no se pudo convertir al vector del modelo."""


def extract_features(url: str) -> dict[str, float]:
    """Devuelve el vector ordenado que espera feature_names.json.

    Raises:
        FeatureExtractionError: URL vacía, malformada o con features incompletas.
    """
    if url is None or not str(url).strip():
        raise FeatureExtractionError("La URL está vacía.")

    normalized = normalize_url(url)
    try:
        raw = extract_features_from_url(normalized)
    except ValueError as exc:
        raise FeatureExtractionError(str(exc)) from exc
    except Exception as exc:
        raise FeatureExtractionError(f"No se pudieron extraer features: {exc}") from exc

    names = ml_model.feature_names or list(raw.keys())
    missing = [name for name in names if name not in raw]
    if missing:
        raise FeatureExtractionError(f"El extractor no produjo las features del modelo: {missing}")
    return {name: float(raw[name]) for name in names}
