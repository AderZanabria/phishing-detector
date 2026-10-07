"""Separa features y etiqueta, hace el split estratificado y persiste los cortes.

Uso desde la raíz del proyecto:
    python -m ml.src.data.make_dataset
    python ml/src/data/make_dataset.py --input ml/data/raw/legitphish.csv
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ml.src.config import (  # noqa: E402
    FEATURE_COLUMNS,
    LABEL_COLUMN,
    PROCESSED_DIR,
    RANDOM_STATE,
    TEST_SIZE,
    URL_COLUMN,
)
from ml.src.data.load_data import load_dataset  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def make_dataset(input_path: str | Path | None = None, output_dir: str | Path | None = None) -> dict[str, Path]:
    """Carga el CSV, separa X/y y guarda train/test 80/20 estratificado.

    Returns:
        Rutas de los artefactos escritos en ml/data/processed/.
    """
    frame = load_dataset(input_path)
    destination = Path(output_dir) if output_dir is not None else PROCESSED_DIR
    destination.mkdir(parents=True, exist_ok=True)

    missing = [column for column in FEATURE_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"No se puede construir X; faltan columnas: {missing}")

    features = frame[FEATURE_COLUMNS].astype(float)
    target = frame[LABEL_COLUMN].astype(int)
    urls = frame[URL_COLUMN]

    if target.nunique() < 2:
        raise ValueError("La etiqueta tiene una sola clase; no se puede estratificar el split.")

    x_train, x_test, y_train, y_test, url_train, url_test = train_test_split(
        features,
        target,
        urls,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=target,
    )

    artifacts = {
        "X_train": destination / "X_train.pkl",
        "X_test": destination / "X_test.pkl",
        "y_train": destination / "y_train.pkl",
        "y_test": destination / "y_test.pkl",
        "url_train": destination / "url_train.pkl",
        "url_test": destination / "url_test.pkl",
    }
    joblib.dump(x_train.reset_index(drop=True), artifacts["X_train"])
    joblib.dump(x_test.reset_index(drop=True), artifacts["X_test"])
    joblib.dump(y_train.reset_index(drop=True), artifacts["y_train"])
    joblib.dump(y_test.reset_index(drop=True), artifacts["y_test"])
    joblib.dump(url_train.reset_index(drop=True), artifacts["url_train"])
    joblib.dump(url_test.reset_index(drop=True), artifacts["url_test"])

    # CSV de apoyo para inspección manual; el entrenamiento lee los .pkl.
    x_train.to_csv(destination / "X_train.csv", index=False)
    x_test.to_csv(destination / "X_test.csv", index=False)
    y_train.to_csv(destination / "y_train.csv", index=False, header=[LABEL_COLUMN])
    y_test.to_csv(destination / "y_test.csv", index=False, header=[LABEL_COLUMN])

    metadata = {
        "rows_total": int(len(frame)),
        "rows_train": int(len(x_train)),
        "rows_test": int(len(x_test)),
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "stratified": True,
        "positive_class": "1 = phishing",
        "negative_class": "0 = legitima",
        "label_note": (
            "LegitPhish original: 0=phishing, 1=legitima. "
            "Invertido en load_dataset para que 1=phishing."
        ),
        "feature_columns": FEATURE_COLUMNS,
        "class_counts_train": {str(k): int(v) for k, v in y_train.value_counts().sort_index().items()},
        "class_counts_test": {str(k): int(v) for k, v in y_test.value_counts().sort_index().items()},
    }
    metadata_path = destination / "split_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    artifacts["metadata"] = metadata_path

    logger.info(
        "Split guardado en %s (train=%s, test=%s).",
        destination,
        metadata["rows_train"],
        metadata["rows_test"],
    )
    return artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara el split train/test de LegitPhish.")
    parser.add_argument("--input", default=None, help="Ruta al CSV crudo. Por defecto ml/data/raw/legitphish.csv.")
    parser.add_argument("--output", default=None, help="Directorio de salida. Por defecto ml/data/processed/.")
    args = parser.parse_args()
    make_dataset(args.input, args.output)


if __name__ == "__main__":
    main()
