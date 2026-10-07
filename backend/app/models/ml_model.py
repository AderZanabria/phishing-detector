"""Carga única del modelo XGBoost y de la lista de features."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Mismo orden que ml/src/config.py. Se usa solo si falta feature_names.json.
FALLBACK_FEATURES = [
    "url_length",
    "has_ip_address",
    "dot_count",
    "https_flag",
    "url_entropy",
    "token_count",
    "subdomain_count",
    "query_param_count",
    "tld_length",
    "path_length",
    "has_hyphen_in_domain",
    "number_of_digits",
    "tld_popularity",
    "suspicious_file_extension",
    "domain_name_length",
    "percentage_numeric_chars",
]


class ModelNotLoadedError(RuntimeError):
    """El modelo no está disponible para inferencia."""


class MLModelLoader:
    """Singleton que carga el .pkl y el JSON de features una sola vez."""

    def __init__(self) -> None:
        self.model = None
        self.feature_names: list[str] = []
        self.loaded = False
        self.load_error: str | None = None

    def load(self) -> None:
        """Lee phishing_model.pkl y feature_names.json. No relanza si faltan."""
        settings = get_settings()
        model_path = settings.resolve_path(settings.model_path)
        features_path = settings.resolve_path(settings.features_path)
        self.loaded = False
        self.model = None
        self.load_error = None

        if features_path.is_file():
            try:
                self.feature_names = json.loads(features_path.read_text(encoding="utf-8"))
                if not isinstance(self.feature_names, list) or not self.feature_names:
                    raise ValueError("feature_names.json no contiene una lista de columnas.")
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                logger.exception("No se pudo leer %s", features_path)
                self.feature_names = list(FALLBACK_FEATURES)
                self.load_error = f"features ilegibles: {exc}"
        else:
            logger.warning("No existe %s. Se usa el orden de features por defecto.", features_path)
            self.feature_names = list(FALLBACK_FEATURES)

        if not model_path.is_file():
            self.load_error = f"No se encontró el modelo en {model_path}"
            logger.error(self.load_error)
            return

        try:
            self.model = joblib.load(model_path)
            self.loaded = True
            logger.info("Modelo cargado desde %s (%s features).", model_path, len(self.feature_names))
        except Exception as exc:  # joblib/xgboost pueden fallar de varias formas
            self.load_error = f"No se pudo cargar el modelo: {exc}"
            logger.exception(self.load_error)

    def predict(self, features_dict: dict) -> float:
        """Devuelve la probabilidad de phishing (clase 1).

        Raises:
            ModelNotLoadedError: si el .pkl no está cargado.
            ValueError: si faltan features.
        """
        if not self.loaded or self.model is None:
            raise ModelNotLoadedError(self.load_error or "Modelo no cargado.")

        missing = [name for name in self.feature_names if name not in features_dict]
        if missing:
            raise ValueError(f"Faltan features para el modelo: {missing}")

        import pandas as pd

        frame = pd.DataFrame([{name: float(features_dict[name]) for name in self.feature_names}])
        if hasattr(self.model, "predict_proba"):
            return float(self.model.predict_proba(frame)[0, 1])
        return float(self.model.predict(frame)[0])


ml_model = MLModelLoader()
