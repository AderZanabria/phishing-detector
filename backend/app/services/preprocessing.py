"""Normalización y validación mínima de URLs."""

from __future__ import annotations

from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """Quita espacios y añade http:// si no hay esquema."""
    cleaned = str(url).strip()
    if cleaned and "://" not in cleaned:
        return f"http://{cleaned}"
    return cleaned


def validate_url(url: str) -> bool:
    """True si hay esquema http/https y un host, o al menos un dominio."""
    if not url or not str(url).strip():
        return False
    candidate = normalize_url(url)
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname or ""
    return bool(host) and " " not in host
