"""Gráficos de evaluación del detector de phishing."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def save_confusion_matrix(matrix: np.ndarray, output_path: str | Path) -> Path:
    """Guarda la matriz de confusión 2x2 con etiquetas legítima / phishing.

    Args:
        matrix: Matriz de sklearn con labels=[0, 1].
        output_path: PNG de salida.

    Returns:
        Ruta escrita.
    """
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(6, 5))
    image = axis.imshow(matrix, cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set_xticks([0, 1], labels=["legítima (0)", "phishing (1)"])
    axis.set_yticks([0, 1], labels=["legítima (0)", "phishing (1)"])
    axis.set_xlabel("Predicción")
    axis.set_ylabel("Real")
    axis.set_title("Matriz de confusión — phishing = 1")

    threshold = matrix.max() / 2.0 if matrix.size else 0
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            color = "white" if matrix[row, col] > threshold else "black"
            axis.text(col, row, f"{int(matrix[row, col])}", ha="center", va="center", color=color)

    figure.tight_layout()
    figure.savefig(destination, dpi=150)
    plt.close(figure)
    return destination
