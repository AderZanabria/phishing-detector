"""Flujo de predicción repetida. Sin estado entre requests."""

from __future__ import annotations

from tests.conftest import requires_model


@requires_model
def test_predict_response_contract(client, sample_phishing_url):
    response = client.post("/api/v1/predict", json={"url": sample_phishing_url})
    assert response.status_code == 200
    body = response.json()
    assert body["url"].startswith("http")
    assert isinstance(body["explanation"], list)
    assert isinstance(body["features"], dict)
    assert abs(body["probability_phishing"] + body["probability_legit"] - 1) < 1e-4


@requires_model
def test_consecutive_predictions_do_not_leak_state(client, sample_legit_url):
    first = client.post("/api/v1/predict", json={"url": sample_legit_url}).json()
    second = client.post("/api/v1/predict", json={"url": "http://192.168.0.1/login.php"}).json()
    third = client.post("/api/v1/predict", json={"url": sample_legit_url}).json()
    assert first["url"] != second["url"]
    assert first["probability_phishing"] == third["probability_phishing"]
    assert first["features"]["has_ip_address"] != second["features"]["has_ip_address"]


@requires_model
def test_same_url_is_stable(client, sample_legit_url):
    left = client.post("/api/v1/predict", json={"url": sample_legit_url}).json()
    right = client.post("/api/v1/predict", json={"url": sample_legit_url}).json()
    assert left["is_phishing"] == right["is_phishing"]
    assert left["probability_phishing"] == right["probability_phishing"]
    assert left["features"] == right["features"]
