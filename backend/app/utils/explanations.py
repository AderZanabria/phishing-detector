"""Explicaciones heurísticas a partir de las features de la URL."""

from __future__ import annotations


def generate_explanation(features: dict, prediction: float) -> list[str]:
    """Devuelve señales legibles. Si no hay ninguna, un mensaje neutro."""
    reasons: list[str] = []

    if float(features.get("url_length", 0)) > 75:
        reasons.append("La URL es inusualmente larga")
    if int(features.get("has_ip_address", 0)) == 1:
        reasons.append("Usa una dirección IP en lugar de un dominio")
    if int(features.get("https_flag", 0)) == 0:
        reasons.append("No usa HTTPS")
    if int(features.get("subdomain_count", 0)) > 3:
        reasons.append("Tiene demasiados subdominios")
    if int(features.get("dot_count", 0)) > 4:
        reasons.append("Tiene demasiados puntos en el dominio")
    if int(features.get("has_hyphen_in_domain", 0)) == 1:
        reasons.append("El dominio contiene guiones (común en imitaciones)")
    if int(features.get("suspicious_file_extension", 0)) == 1:
        reasons.append("El enlace apunta a un archivo potencialmente peligroso")
    if float(features.get("url_entropy", 0)) > 4.0:
        reasons.append("La URL tiene alta entropía (posible ofuscación)")

    if prediction >= 0.7 and not reasons:
        reasons.append("El modelo marca la URL como phishing sin una señal heurística dominante")
    if not reasons:
        reasons.append("No se detectaron señales evidentes de phishing")
    return reasons
