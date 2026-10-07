"""Tests de carga e inferencia. Se omiten si no hay .pkl."""

from __future__ import annotations

import json

import pytest

from ml.src.config import FEATURE_COLUMNS
from ml.src.features.build_features import extract_features_from_url
from tests.conftest import FEATURES_PATH, MODEL_PATH, requires_model


def test_feature_names_match_extractor():
    names = json.loads(FEATURES_PATH.read_text(encoding="utf-8"))
    assert names == FEATURE_COLUMNS


@requires_model
def test_model_file_loads():
    import joblib

    model = joblib.load(MODEL_PATH)
    assert hasattr(model, "predict")


@requires_model
def test_predict_probability_in_unit_interval(sample_legit_url):
    from app.models.ml_model import MLModelLoader

    loader = MLModelLoader()
    loader.load()
    assert loader.loaded
    probability = loader.predict(extract_features_from_url(sample_legit_url))
    assert 0.0 <= probability <= 1.0


@requires_model
def test_feature_count_matches_json():
    from app.models.ml_model import MLModelLoader

    loader = MLModelLoader()
    loader.load()
    names = json.loads(FEATURES_PATH.read_text(encoding="utf-8"))
    assert loader.feature_names == names
    assert len(loader.feature_names) == 16


@requires_model
def test_known_urls_separate_risk(sample_legit_url, sample_phishing_url):
    """La URL con IP y extensión sospechosa no debe puntuar por debajo de google.

    El umbral absoluto depende del modelo entrenado; aquí se comprueba orden y rango.
    """
    from app.models.ml_model import MLModelLoader

    loader = MLModelLoader()
    loader.load()
    legit = loader.predict(extract_features_from_url(sample_legit_url))
    suspicious = loader.predict(extract_features_from_url("http://192.168.0.1/login.php"))
    phishing = loader.predict(extract_features_from_url(sample_phishing_url))
    assert 0.0 <= legit <= 1.0
    assert 0.0 <= phishing <= 1.0
    assert suspicious >= legit
