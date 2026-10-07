FROM python:3.11-slim

WORKDIR /app

# Se copia ml/ completo, no solo ml/models: el extractor importa ml.src.features.
COPY ml /app/ml
COPY backend /app/backend

WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
ENV MODEL_PATH=/app/ml/models/phishing_model.pkl
ENV FEATURES_PATH=/app/ml/models/feature_names.json
ENV API_V1_PREFIX=/api/v1
ENV CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ENV LOG_LEVEL=info
ENV DECISION_THRESHOLD=0.5

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
