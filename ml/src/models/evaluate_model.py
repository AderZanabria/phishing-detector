"""Evaluación del modelo guardado sobre el split de test.

Uso desde la raíz del proyecto:
    python ml/src/models/evaluate_model.py
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ml.src.config import (  # noqa: E402
    CLASSIFICATION_REPORT_PATH,
    CONFUSION_MATRIX_PATH,
    FEATURE_COLUMNS,
    MODEL_PATH,
    MODELS_DIR,
    PROCESSED_DIR,
)
from ml.src.visualization.plot_metrics import save_confusion_matrix  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def load_test_data(processed_dir: str | Path | None = None):
    """Carga X_test.pkl y y_test.pkl."""
    directory = Path(processed_dir) if processed_dir is not None else PROCESSED_DIR
    x_path = directory / "X_test.pkl"
    y_path = directory / "y_test.pkl"
    if not x_path.is_file() or not y_path.is_file():
        raise FileNotFoundError(
            f"No están los datos de test en '{directory}'. "
            "Ejecuta antes: python ml/src/data/make_dataset.py"
        )
    x_test = joblib.load(x_path)
    y_test = joblib.load(y_path)
    missing = [column for column in FEATURE_COLUMNS if column not in x_test.columns]
    if missing:
        raise ValueError(f"X_test no contiene las features esperadas: {missing}")
    if y_test.isna().any() or x_test.isna().any().any():
        raise ValueError("El split de test contiene NaN.")
    return x_test[FEATURE_COLUMNS], y_test


def evaluate_model(
    model_path: str | Path | None = None,
    processed_dir: str | Path | None = None,
) -> dict[str, float]:
    """Calcula métricas, guarda el reporte y la matriz de confusión."""
    checkpoint = Path(model_path) if model_path is not None else MODEL_PATH
    if not checkpoint.is_file():
        raise FileNotFoundError(
            f"No se encontró el modelo en '{checkpoint}'. "
            "Ejecuta antes: python ml/src/models/train_model.py"
        )

    model = joblib.load(checkpoint)
    x_test, y_test = load_test_data(processed_dir)
    predictions = model.predict(x_test)
    if hasattr(model, "predict_proba"):
        scores = model.predict_proba(x_test)[:, 1]
    else:
        scores = predictions

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, pos_label=1, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, pos_label=1, zero_division=0)),
        "f1_score": float(f1_score(y_test, predictions, pos_label=1, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, scores)),
    }

    report = classification_report(
        y_test,
        predictions,
        target_names=["legitima (0)", "phishing (1)"],
        digits=4,
        zero_division=0,
    )
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    CLASSIFICATION_REPORT_PATH.write_text(
        "Convención: 1 = phishing, 0 = legítima "
        "(LegitPhish original invertida en load_dataset).\n\n"
        + report
        + "\n"
        + "\n".join(f"{name}: {value:.6f}" for name, value in metrics.items())
        + "\n",
        encoding="utf-8",
    )
    save_confusion_matrix(matrix, CONFUSION_MATRIX_PATH)

    logger.info("accuracy=%.4f precision=%.4f recall=%.4f f1=%.4f roc_auc=%.4f", *metrics.values())
    logger.info("Reporte: %s", CLASSIFICATION_REPORT_PATH)
    logger.info("Matriz: %s", CONFUSION_MATRIX_PATH)
    print(report)
    for name, value in metrics.items():
        print(f"{name}: {value:.6f}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evalúa phishing_model.pkl sobre el test set.")
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--processed-dir", default=None)
    args = parser.parse_args()
    evaluate_model(args.model_path, args.processed_dir)


if __name__ == "__main__":
    main()
