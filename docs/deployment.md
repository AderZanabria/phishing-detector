# Despliegue en producción

Precios comprobados en fuentes públicas de 2026. Las plataformas los cambian: confirma en el dashboard antes de dejar un servicio encendido.

## 1. Requisitos

- Repo en GitHub con `ml/models/phishing_model.pkl` disponible en el build (el free tier no tiene disco persistente).
- Cuenta en Render, Railway o Fly.io.
- Docker solo si construyes la imagen en local.
- `CORS_ORIGINS` = origen exacto del frontend, con `https://`.

## 2. Render

Recomendado para empezar. El blueprint es `render.yaml`.

1. New → Blueprint → conecta el repo.
2. En el servicio API, `CORS_ORIGINS=https://<frontend>.onrender.com`.
3. En el static site, `VITE_API_URL=https://<api>.onrender.com` y vuelve a lanzar el build. Vite incrusta esa URL.
4. Health check: `/health`.
5. Rewrite `/*` → `/index.html` para React Router. Ya está en el blueprint.

Free tier 2026: web service de 512 MB, 750 horas por workspace, se duerme a los 15 minutos y tarda cerca de un minuto en despertar. Static sites no se duermen. No lo uses como producción real. El plan de pago de 512 MB sin sleep está alrededor de 7 USD/mes.

## 3. Railway

`railway.json` construye `backend/Dockerfile` (contexto = raíz) y arranca uvicorn en `$PORT`.

```bash
railway login
railway init
railway up
railway variables set CORS_ORIGINS=https://tu-front.up.railway.app
```

El trial es 5 USD durante 30 días. Después hay un free de 1 USD/mes y 0.5 GB, insuficiente para este proceso. Hobby son 5 USD/mes de mínimo, con ese crédito de uso incluido.

Para servir también el frontend en el mismo servicio, construye `frontend/dist` en la imagen y monta StaticFiles. Postgres, si más adelante guardas historial: `railway add --database postgres` y lee `DATABASE_URL`. Hoy el historial vive en el navegador.

## 4. Fly.io

```bash
fly launch --no-deploy
fly secrets set CORS_ORIGINS=https://phishing-detector.fly.dev
fly deploy
```

`fly.toml` para en vacío (`min_machines_running = 0`) y despierta con la siguiente petición. Fly ya no da un free tier permanente a cuentas nuevas: el trial es corto y pide tarjeta. Una shared-cpu-1x con 256 MB ronda 2 USD/mes si está siempre encendida; 256 MB puede quedarse corto con XGBoost. Si el proceso muere por memoria, sube a 512 MB.

## 5. Variables

| Variable | Dónde | Ejemplo |
| --- | --- | --- |
| MODEL_PATH | API | `/app/ml/models/phishing_model.pkl` |
| FEATURES_PATH | API | `/app/ml/models/feature_names.json` |
| CORS_ORIGINS | API | `https://app.tudominio.com` |
| DECISION_THRESHOLD | API | `0.5` |
| VITE_API_URL | build del frontend | `https://api.tudominio.com` |

No pongas secretos en el repo. En Render y Railway van en el dashboard. En Fly, `fly secrets set`.

## 6. Dominio y HTTPS

Las tres terminan TLS. Añade el dominio en el panel, crea el CNAME que indiquen y espera el certificado. `VITE_API_URL` y `CORS_ORIGINS` tienen que usar ese `https://`, no `localhost`.

## 7. Monitoreo

`GET /metrics` expone Prometheus: `phishing_predictions_total`, `prediction_latency_seconds`, `model_loaded`, `api_requests_total`. No incluye URLs.

UptimeRobot: monitor HTTP a `https://api.../health` cada 5 minutos. Alerta si el cuerpo no contiene `"model_loaded": true` o si el wakeup del free tier supera el timeout.

## 8. Reentrenamiento

Cada 3-6 meses, o si baja el recall de phishing. `scripts/retrain_model.sh` descarga un CSV opcional, entrena y solo conserva el `.pkl` si el F1 sube. Luego hay que reconstruir la imagen: el modelo se carga al arrancar.

```bash
./scripts/retrain_model.sh
```

GitHub Actions programado puede lanzar ese script y abrir un PR con el `.pkl`. No hay endpoint de reentrenamiento.

Drift: compara en `/metrics` la mezcla `is_phishing` y la latencia. Un salto de `high` sin cambio de tráfico es señal para revisar el dataset, no una prueba de deriva.

## 9. Problemas

- `/health` degraded: el build no copió el `.pkl`.
- CORS: el origen del navegador no está en `CORS_ORIGINS`.
- El frontend llama a localhost: `VITE_API_URL` no estaba definida en el build.
- 503 en `/predict`: modelo ausente. 422: body inválido.
- Cold start: el primer curl del free tier puede pasar de 2 segundos. El script de verificación lo marca.

## 10. Coste orientativo

| Plataforma | Free | Always-on pequeño | Cold start | Escala |
| --- | --- | --- | --- | --- |
| Render | 750 h, duerme a los 15 min | ~7 USD/mes sin sleep | ~1 min | instancias fijas |
| Railway | 5 USD de trial, luego 1 USD | ~5-15 USD | no duerme en Hobby | por uso |
| Fly.io | trial corto, tarjeta | ~2-5 USD | scale-to-zero | regiones |

## Seguridad

HTTPS es automático. CORS solo con el dominio del frontend. `require_api_key` en `backend/app/core/security.py` queda desconectado; actívalo con `API_KEY` si `/metrics` no debe ser público. No montes el repo ni expongas `/docs` si no lo necesitas. Rate limit: añade `slowapi` delante de `/predict` si el servicio es público; no está activo.
