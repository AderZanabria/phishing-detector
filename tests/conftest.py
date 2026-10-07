"""Fixtures compartidas. Añade la raíz y backend/ al path."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
for path in (str(ROOT), str(BACKEND)):
    if path not in sys.path:
        sys.path.insert(0, path)

MODEL_PATH = ROOT / "ml" / "models" / "phishing_model.pkl"
FEATURES_PATH = ROOT / "ml" / "models" / "feature_names.json"


def model_available() -> bool:
    return MODEL_PATH.is_file() and FEATURES_PATH.is_file()


@pytest.fixture(scope="session")
def project_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def client():
    """TestClient sobre la app FastAPI. No exige que el .pkl exista."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_legit_url() -> str:
    return "https://www.google.com"


@pytest.fixture
def sample_phishing_url() -> str:
    return "http://banco-falso-seguro.xyz/login/verify"


@pytest.fixture
def sample_features() -> dict:
    return {
        "url_length": 22,
        "has_ip_address": 0,
        "dot_count": 2,
        "https_flag": 1,
        "url_entropy": 3.2,
        "token_count": 3,
        "subdomain_count": 1,
        "query_param_count": 0,
        "tld_length": 3,
        "path_length": 0,
        "has_hyphen_in_domain": 0,
        "number_of_digits": 0,
        "tld_popularity": 1,
        "suspicious_file_extension": 0,
        "domain_name_length": 6,
        "percentage_numeric_chars": 0.0,
    }


requires_model = pytest.mark.skipif(
    not model_available(),
    reason="Falta ml/models/phishing_model.pkl. Entrena antes de estos tests.",
)
