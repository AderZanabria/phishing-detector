# API

Base local: `http://localhost:8000`. Esquema interactivo en `/docs`.

## GET /health

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok", "model_loaded": true, "version": "1.0.0"}
```

`degraded` si el `.pkl` no cargó. Sigue respondiendo 200.

## POST /api/v1/predict

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.google.com"}'
```

Campos: `url`, `is_phishing`, `confidence`, `probability_phishing`, `probability_legit`, `risk_level` (`low` < 0.3, `medium` 0.3–0.7, `high` > 0.7), `features`, `explanation`.

Errores: 422 URL vacía o cuerpo inválido, 400 URL sin host, 503 modelo no cargado, 500 fallo de inferencia.

## GET /metrics

Texto Prometheus. No incluye URLs.

```bash
curl http://localhost:8000/metrics
```

Series: `phishing_predictions_total{is_phishing,risk_level}`, `prediction_latency_seconds`, `model_loaded`, `api_requests_total{method,endpoint,status}`.

## POST /api/v1/predict/batch

```bash
curl -X POST http://localhost:8000/api/v1/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com","http://192.168.0.1/login.php"]}'
```

```json
{"results": [], "errors": []}
```

Lista vacía: 422 (`min_length=1`). Si ninguna URL se puntúa: 400. Máximo 100.

No hay rate limiting. La API key `X-API-Key` está comentada en `backend/app/core/security.py`.

### Python

```python
import httpx
r = httpx.post("http://localhost:8000/api/v1/predict", json={"url": "https://example.com"})
print(r.json())
```

### JavaScript

```javascript
const res = await fetch("http://localhost:8000/api/v1/predict", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({url: "https://example.com"}),
});
console.log(await res.json());
```
