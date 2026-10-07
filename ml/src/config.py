"""Constantes compartidas del pipeline de detección de phishing por URL.

Convención de etiqueta (después de load_dataset):
    1 = phishing
    0 = legítima

LegitPhish publica la etiqueta al revés (ClassLabel 0 = phishing, 1 = legítima).
La inversión se aplica en ml/src/data/load_data.py y queda registrada aquí.
"""

from pathlib import Path

# ml/src/config.py -> parents[2] == raíz del proyecto (phishing-detector/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "ml" / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "ml" / "data" / "processed"
EXTERNAL_DIR = PROJECT_ROOT / "ml" / "data" / "external"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"

DEFAULT_RAW_CSV = RAW_DIR / "legitphish.csv"
MODEL_PATH = MODELS_DIR / "phishing_model.pkl"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.json"
LABEL_MAPPING_PATH = MODELS_DIR / "label_mapping.json"
CONFUSION_MATRIX_PATH = MODELS_DIR / "confusion_matrix.png"
CLASSIFICATION_REPORT_PATH = MODELS_DIR / "classification_report.txt"

# Features estructurales/léxicas del paper LegitPhish (16 columnas, sin URL ni label).
FEATURE_COLUMNS = [
    "url_length",
    "has_ip_address",
    "dot_count",
    "https_flag",
    "url_entropy",
    "token_count",
    "subdomain_count",
    "query_param_count",
    "tld_length",
    "path_length",
    "has_hyphen_in_domain",
    "number_of_digits",
    "tld_popularity",
    "suspicious_file_extension",
    "domain_name_length",
    "percentage_numeric_chars",
]

URL_COLUMN = "url"
LABEL_COLUMN = "label"

# Después de la inversión aplicada en load_data.py.
POSITIVE_CLASS = 1  # phishing
NEGATIVE_CLASS = 0  # legítima
CLASS_NAMES = {0: "legitima", 1: "phishing"}

RANDOM_STATE = 42
TEST_SIZE = 0.20

XGB_PARAMS = {
    "n_estimators": 200,
    "max_depth": 6,
    "learning_rate": 0.1,
    "random_state": RANDOM_STATE,
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "n_jobs": -1,
}
