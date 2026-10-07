#!/usr/bin/env bash
# Reentrena sin make. Mantiene el .pkl anterior si el F1 nuevo no mejora.
set -euo pipefail
cd "$(dirname "$0")/.."

CSV="ml/data/raw/legitphish.csv"
MODEL="ml/models/phishing_model.pkl"
REPORT="ml/models/classification_report.txt"
BACKUP="ml/models/phishing_model.prev.pkl"
URL="https://data.mendeley.com/public-files/datasets/hx4m73v2sf/files/0ed51e4d-d160-4047-b650-3f0801eea4aa/file_downloaded"

mkdir -p ml/data/raw ml/models
if [[ ! -f "$CSV" ]]; then
  echo "Descargando LegitPhish..."
  curl -L -o "$CSV" "$URL"
fi
if [[ -f "$MODEL" ]]; then
  cp "$MODEL" "$BACKUP"
fi
if [[ -f "$REPORT" ]]; then
  cp "$REPORT" "${REPORT}.prev"
fi

python ml/src/data/make_dataset.py
python ml/src/models/train_model.py
python ml/src/models/evaluate_model.py

python - <<'PY'
from pathlib import Path
import re, shutil
report = Path("ml/models/classification_report.txt").read_text(encoding="utf-8")
prev = Path("ml/models/classification_report.txt.prev")
def f1(text: str) -> float:
    match = re.search(r"weighted avg\s+\S+\s+\S+\s+(\d+\.\d+)", text)
    if not match:
        raise SystemExit("No se encontró F1 weighted en el reporte.")
    return float(match.group(1))
new = f1(report)
if not prev.is_file():
    print(f"Primer modelo aceptado. F1={new:.4f}")
    raise SystemExit(0)
old = f1(prev.read_text(encoding="utf-8"))
print(f"F1 anterior={old:.4f} nuevo={new:.4f}")
if new > old:
    print("Nuevo modelo mejor. Se conserva.")
else:
    shutil.copy("ml/models/phishing_model.prev.pkl", "ml/models/phishing_model.pkl")
    print("Nuevo modelo no mejora. Se restauró el anterior.")
    raise SystemExit(2)
PY
