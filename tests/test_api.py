"""Tests HTTP del backend."""

from __future__ import annotations

import pytest

from tests.conftest import requires_model

EXPECTED_FIELDS = {
    "url",
    "is_phishing",
    "confidence",
    "probability_phishing",
    "probability_legit",
    "risk_level",
    "features",
    "explanation",
}


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert "model_loaded" in body
    assert body["version"] == "1.0.0"


@requires_model
def test_health_model_loaded(client):
    body = client.get("/health").json()
    assert body["model_loaded"] is True
    assert body["status"] == "ok"


@requires_model
def test_predict_legit_shape(client, sample_legit_url):
    response = client.post("/api/v1/predict", json={"url": sample_legit_url})
    assert response.status_code == 200
    body = response.json()
    assert EXPECTED_FIELDS <= body.keys()
    assert 0.0 <= body["probability_phishing"] <= 1.0
    assert body["risk_level"] in {"low", "medium", "high"}


@requires_model
def test_predict_suspicious_ip(client):
    response = client.post("/api/v1/predict", json={"url": "http://192.168.0.1/login.php"})
    assert response.status_code == 200
    body = response.json()
    assert body["features"]["has_ip_address"] == 1.0
    assert body["is_phishing"] in {True, False}


def test_empty_url_is_422(client):
    response = client.post("/api/v1/predict", json={"url": ""})
    assert response.status_code == 422


def test_missing_url_is_422(client):
    response = client.post("/api/v1/predict", json={})
    assert response.status_code == 422


def test_malformed_url_is_400(client):
    response = client.post("/api/v1/predict", json={"url": "http://"})
    assert response.status_code in {400, 503}


@requires_model
def test_batch_three_urls(client, sample_legit_url, sample_phishing_url):
    payload = {"urls": [sample_legit_url, sample_phishing_url, "http://192.168.0.1/login.php"]}
    response = client.post("/api/v1/predict/batch", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 3
    assert body["errors"] == []


def test_batch_empty_list_is_422(client):
    response = client.post("/api/v1/predict/batch", json={"urls": []})
    assert response.status_code == 422
