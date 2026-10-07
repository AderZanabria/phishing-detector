# Arquitectura

```text
Usuario
  -> Frontend React (5173)
  -> POST /api/v1/predict
  -> FastAPI
  -> validate/normalize URL
  -> extract_features_from_url (ml/src/features)
  -> XGBoost (ml/models/phishing_model.pkl)
  -> explicación heurística
  -> JSON (veredicto, probabilidades, features)
```

## Componentes

- `ml/`: carga LegitPhish, invierte la etiqueta, entrena y serializa el modelo.
- `backend/`: singleton que carga el `.pkl` al arrancar. Si falta, `/health` queda `degraded` y predict responde 503.
- `frontend/`: formulario, tarjeta de resultado e historial local. No guarda URLs en servidor.

## Decisiones

- Se reutiliza `extract_features_from_url` para no tener dos extractores.
- La clase positiva es phishing. `predict_proba[:, 1]` es la probabilidad de phishing.
- El lote no aborta por una URL mala: responde `{results, errors}`.
- El Docker del backend usa la raíz como contexto porque importa el paquete `ml`.

## Despliegue

```text
docker compose
  backend  uvicorn :8000  volumen ml/models
  frontend vite :5173     o nginx :80 en prod
```

## Escalado

El modelo es CPU y stateless. Se puede subir `--workers` o replicar el backend detrás de un balanceador. El `.pkl` debe estar en cada réplica o en un volumen compartido de solo lectura.
