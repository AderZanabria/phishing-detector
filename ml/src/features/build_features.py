"""Extracción de features estructurales y léxicas desde una URL nueva.

Estas 16 features replican el esquema de LegitPhish para poder puntuar
URLs que no vienen en el CSV. El entrenamiento usa las columnas ya
calculadas del dataset; esta función es la ruta de inferencia.
"""

from __future__ import annotations

import ipaddress
import math
import re
from collections import Counter
from urllib.parse import urlparse

from ml.src.config import FEATURE_COLUMNS

# TLDs frecuentes. 1 = popular, 0 = poco común / sospechoso en este esquema.
POPULAR_TLDS = {
    "com",
    "org",
    "net",
    "edu",
    "gov",
    "mil",
    "int",
    "io",
    "co",
    "uk",
    "de",
    "fr",
    "es",
    "it",
    "nl",
    "ca",
    "au",
    "br",
    "in",
    "jp",
    "info",
    "biz",
    "me",
    "app",
    "dev",
    "ai",
    "us",
    "eu",
}

# TLD compuestos frecuentes para no contar "co" como el TLD de "example.co.uk".
MULTI_PART_TLDS = {
    "co.uk",
    "org.uk",
    "ac.uk",
    "gov.uk",
    "com.au",
    "net.au",
    "org.au",
    "co.jp",
    "com.br",
    "com.mx",
    "com.ar",
    "co.za",
    "com.es",
}

SUSPICIOUS_EXTENSIONS = {
    "exe",
    "scr",
    "bat",
    "cmd",
    "msi",
    "dll",
    "js",
    "vbs",
    "jar",
    "apk",
    "zip",
    "rar",
    "7z",
    "php",
    "phtml",
    "hta",
    "iso",
}

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
_IPV4_RE = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")


def _shannon_entropy(value: str) -> float:
    """Entropía de Shannon en bits sobre los caracteres de la URL."""
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def _hostname_is_ip(hostname: str) -> bool:
    """True si el host es una IPv4 o IPv6 (con o sin corchetes)."""
    host = hostname.strip("[]")
    if not host:
        return False
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return bool(_IPV4_RE.fullmatch(host))


def _split_domain(hostname: str) -> tuple[str, str, int]:
    """Separa subdominios, nombre registrable y TLD.

    Returns:
        (registrable_name, tld, subdomain_count)
    """
    host = hostname.strip(".").lower()
    if not host or _hostname_is_ip(host):
        return "", "", 0

    parts = [part for part in host.split(".") if part]
    if len(parts) == 1:
        return parts[0], "", 0

    last_two = ".".join(parts[-2:])
    if last_two in MULTI_PART_TLDS and len(parts) >= 3:
        tld = last_two
        registrable = parts[-3]
        subdomain_count = max(0, len(parts) - 3)
    else:
        tld = parts[-1]
        registrable = parts[-2]
        subdomain_count = max(0, len(parts) - 2)
    return registrable, tld, subdomain_count


def extract_features_from_url(url: str) -> dict[str, float | int]:
    """Extrae el vector de 16 features de una URL.

    Args:
        url: URL en texto. Si no trae esquema se asume http:// solo para parsear.

    Returns:
        Diccionario con las claves de FEATURE_COLUMNS. Los flags son 0/1.

    Raises:
        ValueError: si la URL está vacía.
    """
    if url is None or not str(url).strip():
        raise ValueError("La URL no puede estar vacía.")

    raw = str(url).strip()
    parse_target = raw if "://" in raw else f"http://{raw}"
    parsed = urlparse(parse_target)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""

    registrable, tld, subdomain_count = _split_domain(hostname)
    digits = sum(character.isdigit() for character in raw)
    tokens = _TOKEN_RE.findall(raw)
    query_param_count = 0 if not query else len([part for part in query.split("&") if part])

    extension = ""
    if "." in path.rsplit("/", 1)[-1]:
        extension = path.rsplit(".", 1)[-1].lower()
        extension = extension.split("?")[0].split("#")[0]

    features: dict[str, float | int] = {
        "url_length": len(raw),
        "has_ip_address": int(_hostname_is_ip(hostname)),
        "dot_count": raw.count("."),
        "https_flag": int(parsed.scheme.lower() == "https" or raw.lower().startswith("https://")),
        "url_entropy": round(_shannon_entropy(raw), 6),
        "token_count": len(tokens),
        "subdomain_count": subdomain_count,
        "query_param_count": query_param_count,
        "tld_length": len(tld),
        "path_length": len(path),
        "has_hyphen_in_domain": int("-" in hostname),
        "number_of_digits": digits,
        "tld_popularity": int(tld.split(".")[-1] in POPULAR_TLDS or tld in POPULAR_TLDS),
        "suspicious_file_extension": int(extension in SUSPICIOUS_EXTENSIONS),
        "domain_name_length": len(registrable),
        "percentage_numeric_chars": round((digits / len(raw)) * 100.0, 6) if raw else 0.0,
    }
    # Garantiza el orden y el conjunto exacto que espera el modelo.
    return {name: features[name] for name in FEATURE_COLUMNS}
