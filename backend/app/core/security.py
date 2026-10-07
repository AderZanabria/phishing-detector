"""CORS y dependencia opcional de API key.

La API key no está activa. Para activarla, descomenta `require_api_key`
y úsala como dependencia en los routers de predicción.
"""

from __future__ import annotations

import os

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings


def configure_cors(app: FastAPI) -> None:
    """Añade CORS con los orígenes de CORS_ORIGINS."""
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Dependencia opcional. No está cableada en los routers.

    Actívala cuando definas API_KEY en el entorno:
        # router = APIRouter(dependencies=[Depends(require_api_key)])
    """
    expected = os.getenv("API_KEY")
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida o ausente.",
        )
