"""Inferencia sobre URLs nuevas con el modelo entrenado.

Uso desde la raíz del proyecto:
    python ml/src/models/predict_model.py --url "http://192.168.0.1/login.php"
    python ml/src/models/predict_model.py --url-file urls.txt
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import joblib
import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ml.src.config import FEATURE_NAMES_PATH, MODEL_PATH  # noqa: E402
from ml.src.features.build_features import extract_features_from_url  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def load_model(model_path: str | Path | None = None):
    """Carga el XGBoost serializado y el orden de features."""
    checkpoint = Path(model_path) if model_path is not None else MODEL_PATH
    if not checkpoint.is_file():
        raise FileNotFoundError(
            f"No se encontró el modelo en '{checkpoint}'. Entrena antes con train_model.py."
        )
    if not FEATURE_NAMES_PATH.is_file():
        raise FileNotFoundError(
            f"No se encontró '{FEATURE_NAMES_PATH}'. Vuelve a entrenar para regenerarlo."
        )
    model = joblib.load(checkpoint)
    feature_names = json.loads(FEATURE_NAMES_PATH.read_text(encoding="utf-8"))
    return model, feature_names


def predict_url(url: str, model=None, feature_names: list[str] | None = None) -> dict:
    """Devuelve la clase y la probabilidad de phishing de una URL.

    label 1 = phishing, label 0 = legítima.
    """
    if model is None or feature_names is None:
        model, feature_names = load_model()

    features = extract_features_from_url(url)
    frame = pd.DataFrame([{name: features[name] for name in feature_names}])
    prediction = int(model.predict(frame)[0])
    probability = float(model.predict_proba(frame)[0, 1]) if hasattr(model, "predict_proba") else float(prediction)
    return {
        "url": url,
        "label": prediction,
        "class_name": "phishing" if prediction == 1 else "legitima",
        "phishing_probability": round(probability, 6),
        "features": features,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Predice phishing/legítima para una o más URLs.")
    parser.add_argument("--url", action="append", default=[], help="URL a clasificar. Repetible.")
    parser.add_argument("--url-file", default=None, help="Archivo de texto con una URL por línea.")
    parser.add_argument("--model-path", default=None)
    args = parser.parse_args()

    urls = list(args.url)
    if args.url_file:
        file_path = Path(args.url_file)
        if not file_path.is_file():
            raise FileNotFoundError(f"No se encontró el archivo de URLs: {file_path}")
        urls.extend(line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip())
    if not urls:
        raise SystemExit("Pasa al menos una URL con --url o --url-file.")

    model, feature_names = load_model(args.model_path)
    for url in urls:
        result = predict_url(url, model, feature_names)
        print(
            f"{result['class_name']}\tlabel={result['label']}\t"
            f"p_phishing={result['phishing_probability']:.4f}\t{result['url']}"
        )


if __name__ == "__main__":
    main()
