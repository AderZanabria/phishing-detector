"""Tests del extractor de features de URL."""

from __future__ import annotations

import pytest

from ml.src.config import FEATURE_COLUMNS
from ml.src.features.build_features import extract_features_from_url


def test_legit_url_has_expected_keys(sample_legit_url):
    features = extract_features_from_url(sample_legit_url)
    assert list(features) == FEATURE_COLUMNS
    assert features["https_flag"] == 1
    assert features["has_ip_address"] == 0
    assert features["url_length"] == len(sample_legit_url)


def test_ip_address_flag():
    features = extract_features_from_url("http://192.168.0.1/login.php")
    assert features["has_ip_address"] == 1
    assert features["https_flag"] == 0
    assert features["suspicious_file_extension"] == 1


def test_https_flag_absent_without_scheme():
    # Sin esquema se asume http:// solo para parsear; el flag HTTPS sigue en 0.
    features = extract_features_from_url("example.com/login")
    assert features["https_flag"] == 0


def test_subdomain_count_multipart():
    features = extract_features_from_url("https://a.b.c.example.co.uk/path")
    assert features["subdomain_count"] == 3
    assert features["tld_length"] == len("co.uk")


def test_empty_url_raises():
    with pytest.raises(ValueError):
        extract_features_from_url("   ")


def test_special_characters_do_not_break():
    features = extract_features_from_url("https://example.com/a%20b?q=1&x=2#frag")
    assert features["query_param_count"] == 2
    assert features["url_length"] > 0


def test_hyphen_and_digits():
    features = extract_features_from_url("http://pay-pal-secure123.xyz/verify")
    assert features["has_hyphen_in_domain"] == 1
    assert features["number_of_digits"] == 3
    assert features["percentage_numeric_chars"] > 0


def test_suspicious_extension_and_entropy_type():
    features = extract_features_from_url("http://files.example.net/invoice.exe")
    assert features["suspicious_file_extension"] == 1
    assert isinstance(features["url_entropy"], float)
    assert features["url_entropy"] >= 0
