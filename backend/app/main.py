"""Aplicación FastAPI del detector de phishing por URL."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api.routes import health, metrics, predict
from app.core.config import get_settings
from app.core.security import configure_cors
from app.models.ml_model import ml_model

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo una vez al arrancar. Un .pkl ausente no tumba el proceso."""
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        ml_model.load()
    except Exception:
        logger.exception("Fallo inesperado al cargar el modelo. /health quedará degraded.")
    if not ml_model.loaded:
        logger.error("Modelo no disponible: %s", ml_model.load_error)
    yield


def create_app() -> FastAPI:
    """Construye la app con CORS, health en raíz y predict bajo /api/v1."""
    settings = get_settings()
    app = FastAPI(
        title="Phishing Detector API",
        version=__version__,
        description=(
            "Clasifica URLs como phishing o legítimas con un XGBoost entrenado "
            "sobre features estructurales y léxicas. Clase positiva: 1 = phishing."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    configure_cors(app)
    app.add_middleware(metrics.MetricsMiddleware)
    app.include_router(health.router)
    app.include_router(metrics.router)
    app.include_router(predict.router, prefix=settings.api_v1_prefix)
    static_dir = os.getenv("STATIC_DIR")
    if static_dir and Path(static_dir).is_dir():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")

    @app.get("/", tags=["root"])
    async def root() -> dict[str, str]:
        return {
            "message": "Phishing Detector API",
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
            "predict": f"{settings.api_v1_prefix}/predict",
        }

    return app


app = create_app()
