"""Entrenamiento del clasificador XGBoost de phishing por URL.

Uso desde la raíz del proyecto:
    python ml/src/models/train_model.py
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import joblib
from xgboost import XGBClassifier

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ml.src.config import (  # noqa: E402
    FEATURE_COLUMNS,
    FEATURE_NAMES_PATH,
    LABEL_MAPPING_PATH,
    MODEL_PATH,
    MODELS_DIR,
    PROCESSED_DIR,
    XGB_PARAMS,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def load_processed(processed_dir: str | Path | None = None):
    """Carga X_train/y_train generados por make_dataset.py."""
    directory = Path(processed_dir) if processed_dir is not None else PROCESSED_DIR
    x_path = directory / "X_train.pkl"
    y_path = directory / "y_train.pkl"
    if not x_path.is_file() or not y_path.is_file():
        raise FileNotFoundError(
            f"No están los datos procesados en '{directory}'. "
            "Ejecuta antes: python ml/src/data/make_dataset.py"
        )
    x_train = joblib.load(x_path)
    y_train = joblib.load(y_path)
    missing = [column for column in FEATURE_COLUMNS if column not in x_train.columns]
    if missing:
        raise ValueError(f"X_train no contiene las features esperadas: {missing}")
    if y_train.isna().any():
        raise ValueError("y_train contiene NaN.")
    return x_train[FEATURE_COLUMNS], y_train


def train_model(processed_dir: str | Path | None = None, model_path: str | Path | None = None):
    """Entrena XGBoost y guarda modelo, nombres de features y mapeo de etiqueta."""
    x_train, y_train = load_processed(processed_dir)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # scale_pos_weight compensa que phishing sea la clase mayoritaria en LegitPhish
    # sin cambiar los hiperparámetros pedidos. Si las clases están balanceadas, queda en 1.
    positives = int((y_train == 1).sum())
    negatives = int((y_train == 0).sum())
    if positives == 0:
        raise ValueError("No hay ejemplos de phishing (label=1) en el entrenamiento.")
    scale_pos_weight = negatives / positives

    params = dict(XGB_PARAMS)
    params["scale_pos_weight"] = scale_pos_weight
    model = XGBClassifier(**params)
    logger.info("Entrenando XGBoost con %s filas. params=%s", len(x_train), params)
    model.fit(x_train, y_train)

    destination = Path(model_path) if model_path is not None else MODEL_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, destination)

    FEATURE_NAMES_PATH.write_text(json.dumps(FEATURE_COLUMNS, indent=2), encoding="utf-8")
    LABEL_MAPPING_PATH.write_text(
        json.dumps(
            {
                "1": "phishing",
                "0": "legitima",
                "source_convention": "LegitPhish ClassLabel 0=phishing, 1=legitima",
                "pipeline_convention": "label invertida: 1=phishing, 0=legitima",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("Modelo guardado en %s", destination)
    logger.info("Features guardadas en %s", FEATURE_NAMES_PATH)
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena el detector XGBoost de phishing.")
    parser.add_argument("--processed-dir", default=None, help="Directorio con X_train.pkl y y_train.pkl.")
    parser.add_argument("--model-path", default=None, help="Ruta de salida del .pkl.")
    args = parser.parse_args()
    train_model(args.processed_dir, args.model_path)


if __name__ == "__main__":
    main()
