"""Carga y limpieza del CSV LegitPhish.

El dataset original anota:
    ClassLabel / Label = 0  -> phishing
    ClassLabel / Label = 1  -> legítima

Este módulo invierte esa convención para que el resto del pipeline use
la clase positiva estándar en detección:
    label = 1  -> phishing
    label = 0  -> legítima
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd

from ml.src.config import (
    DEFAULT_RAW_CSV,
    FEATURE_COLUMNS,
    LABEL_COLUMN,
    URL_COLUMN,
)

logger = logging.getLogger(__name__)

_LABEL_ALIASES = {"label", "classlabel", "class_label", "target", "y"}
_URL_ALIASES = {"url", "uri", "link"}


def _normalize_column_name(name: str) -> str:
    """Pasa un nombre de columna a snake_case minúsculo."""
    cleaned = str(name).strip().lower()
    cleaned = re.sub(r"[\s\-]+", "_", cleaned)
    cleaned = re.sub(r"[^a-z0-9_]", "", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned


def _rename_special_columns(columns: list[str]) -> dict[str, str]:
    """Detecta URL y etiqueta aunque vengan como URL, ClassLabel, Label, etc."""
    rename: dict[str, str] = {}
    for column in columns:
        if column in _URL_ALIASES and column != URL_COLUMN:
            rename[column] = URL_COLUMN
        elif column in _LABEL_ALIASES and column != LABEL_COLUMN:
            rename[column] = LABEL_COLUMN
    return rename


def _invert_legitphish_label(series: pd.Series) -> pd.Series:
    """Invierte 0/1 de LegitPhish.

    Original: 0 = phishing, 1 = legítima.
    Salida:   1 = phishing, 0 = legítima.
    """
    numeric = pd.to_numeric(series, errors="coerce")
    unique = set(numeric.dropna().unique().tolist())
    if not unique.issubset({0, 1, 0.0, 1.0}):
        raise ValueError(
            "La columna de etiqueta debe ser binaria 0/1. "
            f"Valores encontrados: {sorted(unique)[:10]}"
        )
    # 1 - original: phishing (0) pasa a 1 y legítima (1) pasa a 0.
    inverted = (1 - numeric).astype("int8")
    return inverted


def load_dataset(path: str | Path | None = None) -> pd.DataFrame:
    """Carga legitphish.csv y devuelve un DataFrame limpio.

    Args:
        path: Ruta al CSV. Por defecto ml/data/raw/legitphish.csv.

    Returns:
        DataFrame con columnas normalizadas, label invertida (1 = phishing)
        y sin filas con NaN en features o etiqueta.

    Raises:
        FileNotFoundError: si el CSV no existe.
        ValueError: si faltan la URL, la etiqueta o alguna feature esperada.
    """
    csv_path = Path(path) if path is not None else DEFAULT_RAW_CSV
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"No se encontró el dataset en '{csv_path}'. "
            "Coloca legitphish.csv en ml/data/raw/ o pasa la ruta explícita."
        )

    logger.info("Cargando dataset desde %s", csv_path)
    frame = pd.read_csv(csv_path)
    if frame.empty:
        raise ValueError(f"El CSV '{csv_path}' está vacío.")

    frame.columns = [_normalize_column_name(column) for column in frame.columns]
    frame = frame.rename(columns=_rename_special_columns(list(frame.columns)))

    missing = [column for column in (URL_COLUMN, LABEL_COLUMN) if column not in frame.columns]
    if missing:
        raise ValueError(
            f"Faltan columnas obligatorias {missing}. "
            f"Columnas disponibles: {list(frame.columns)}"
        )

    missing_features = [column for column in FEATURE_COLUMNS if column not in frame.columns]
    if missing_features:
        raise ValueError(
            "Faltan features esperadas de LegitPhish: "
            f"{missing_features}. Columnas disponibles: {list(frame.columns)}"
        )

    before = len(frame)
    frame = frame.dropna(subset=[URL_COLUMN, LABEL_COLUMN, *FEATURE_COLUMNS]).copy()
    dropped = before - len(frame)
    if dropped:
        logger.warning("Se descartaron %s filas con NaN en URL, label o features.", dropped)
    if frame.empty:
        raise ValueError("Tras eliminar NaN no quedan filas utilizables.")

    frame[URL_COLUMN] = frame[URL_COLUMN].astype(str).str.strip()
    frame = frame[frame[URL_COLUMN].ne("")].copy()
    frame[LABEL_COLUMN] = _invert_legitphish_label(frame[LABEL_COLUMN])
    for column in FEATURE_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    still_nan = int(frame[FEATURE_COLUMNS].isna().any(axis=1).sum())
    if still_nan:
        logger.warning("Se descartaron %s filas con features no numéricas.", still_nan)
        frame = frame.dropna(subset=FEATURE_COLUMNS).copy()
    if frame.empty:
        raise ValueError("Tras convertir features a numérico no quedan filas.")

    ordered = [URL_COLUMN, LABEL_COLUMN, *FEATURE_COLUMNS]
    extra = [column for column in frame.columns if column not in ordered]
    frame = frame[ordered + extra].reset_index(drop=True)

    counts = frame[LABEL_COLUMN].value_counts().to_dict()
    logger.info(
        "Dataset listo: %s filas. label=1 phishing: %s, label=0 legítima: %s",
        len(frame),
        counts.get(1, 0),
        counts.get(0, 0),
    )
    return frame
