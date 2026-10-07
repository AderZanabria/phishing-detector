const FEATURE_LABELS = {
  url_length: "Longitud de la URL",
  has_ip_address: "Usa dirección IP",
  dot_count: "Cantidad de puntos",
  https_flag: "Usa HTTPS",
  url_entropy: "Entropía",
  token_count: "Tokens",
  subdomain_count: "Subdominios",
  query_param_count: "Parámetros de query",
  tld_length: "Longitud del TLD",
  path_length: "Longitud del path",
  has_hyphen_in_domain: "Guion en el dominio",
  number_of_digits: "Dígitos",
  tld_popularity: "TLD popular",
  suspicious_file_extension: "Extensión sospechosa",
  domain_name_length: "Longitud del dominio",
  percentage_numeric_chars: "% de caracteres numéricos",
};

export function featureLabel(name) {
  return FEATURE_LABELS[name] || name.replaceAll("_", " ");
}

export function formatDate(isoString) {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "Fecha desconocida";
  const diffMs = Date.now() - date.getTime();
  const minutes = Math.round(diffMs / 60000);
  if (minutes < 1) return "Hace un momento";
  if (minutes < 60) return `Hace ${minutes} min`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `Hace ${hours} h`;
  return date.toLocaleString("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatConfidence(value) {
  const number = Number(value);
  if (Number.isNaN(number)) return "—";
  return `${Math.round(number * 100)}%`;
}

export function getRiskColor(riskLevel) {
  if (riskLevel === "high") return "bg-red-100 text-red-800 border-red-200";
  if (riskLevel === "medium") return "bg-amber-100 text-amber-800 border-amber-200";
  return "bg-emerald-100 text-emerald-800 border-emerald-200";
}

export function isSuspiciousFeature(name, value) {
  const numeric = Number(value);
  if (name === "has_ip_address" || name === "has_hyphen_in_domain" || name === "suspicious_file_extension") {
    return numeric === 1;
  }
  if (name === "https_flag" || name === "tld_popularity") return numeric === 0;
  if (name === "url_length") return numeric > 75;
  if (name === "subdomain_count") return numeric > 3;
  if (name === "dot_count") return numeric > 4;
  if (name === "url_entropy") return numeric > 4;
  return false;
}

export function truncateUrl(url, max = 72) {
  if (!url || url.length <= max) return url;
  return `${url.slice(0, max - 1)}…`;
}
