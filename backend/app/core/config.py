"""Configuración cargada desde variables de entorno.

Las rutas de modelo y features son relativas al directorio de trabajo
del proceso (la raíz del repo en local, /app en Docker).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[3] == raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Variables de entorno de la API."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / "backend" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model_path: str = Field(
        default="../ml/models/phishing_model.pkl",
        alias="MODEL_PATH",
        description="Ruta al modelo XGBoost serializado con joblib.",
    )
    features_path: str = Field(
        default="../ml/models/feature_names.json",
        alias="FEATURES_PATH",
        description="Ruta al JSON con el orden de features.",
    )
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS",
        description="Orígenes CORS separados por coma.",
    )
    log_level: str = Field(default="info", alias="LOG_LEVEL")
    decision_threshold: float = Field(default=0.5, alias="DECISION_THRESHOLD")
    app_version: str = "1.0.0"

    @field_validator("decision_threshold")
    @classmethod
    def _threshold_in_range(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("DECISION_THRESHOLD debe estar entre 0 y 1.")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def resolve_path(self, raw: str) -> Path:
        """Resuelve una ruta relativa respecto al cwd y, si no existe, respecto a la raíz del repo."""
        path = Path(raw)
        if path.is_absolute():
            return path
        from_cwd = (Path.cwd() / path).resolve()
        if from_cwd.exists():
            return from_cwd
        from_root = (PROJECT_ROOT / path).resolve()
        if from_root.exists():
            return from_root
        # Rutas tipo ../ml/models/... escritas desde backend/.
        from_backend = (PROJECT_ROOT / "backend" / path).resolve()
        return from_backend if from_backend.exists() else from_cwd


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración cacheada."""
    return Settings()
