# Phishing Detector

Detector de phishing que clasifica **solo URLs**. Un XGBoost puntúa 16 features estructurales y léxicas; FastAPI las expone y React las muestra.

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Contenido

- [Características](#características)
- [Stack](#stack)
- [Estructura](#estructura)
- [Instalación](#instalación)
- [Uso](#uso)
- [Tests](#tests)
- [Docker](#docker)
- [Métricas](#métricas)
- [Roadmap](#roadmap)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

## Características

- Extracción de features de URL en inferencia, sin descargar la página.
- API `GET /health`, `POST /api/v1/predict` y `POST /api/v1/predict/batch`.
- UI con veredicto, confianza, explicación e historial local.
- Convención del pipeline: **1 = phishing, 0 = legítima**. LegitPhish publica lo contrario y se invierte al cargar.

## Demo

Placeholder: captura de la pantalla de análisis en `docs/demo.png`.

## Stack

Python 3.11, pandas, scikit-learn, XGBoost, FastAPI, React 18, Vite, Tailwind, Docker.

## Estructura

```text
phishing-detector/
├── backend/          FastAPI
├── frontend/         React + Vite
├── ml/               datos, entrenamiento e inferencia
├── tests/            pytest
├── docs/             arquitectura, API, dataset, despliegue
├── docker-compose.yml
└── Makefile
```

## Instalación

Requisitos: Python 3.11, Node 20, Docker opcional.

```bash
git clone <repo> phishing-detector
cd phishing-detector
python3 -m venv .venv && source .venv/bin/activate
make install
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Dataset LegitPhish (el archivo oficial se llama `url_features_extracted1.csv`):

```bash
mkdir -p ml/data/raw
curl -L -o ml/data/raw/legitphish.csv \
  "https://data.mendeley.com/public-files/datasets/hx4m73v2sf/files/0ed51e4d-d160-4047-b650-3f0801eea4aa/file_downloaded"
make train
```

Backend y frontend:

```bash
uvicorn app.main:app --reload --app-dir backend --port 8000
cd frontend && npm run dev
```

La UI queda en http://localhost:5173 y la API en http://localhost:8000/docs.

## Uso

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"url":"http://192.168.0.1/login.php"}'
```

En la web, pega una URL y pulsa Analizar. El historial vive en `localStorage`.

## Tests

```bash
make test
```

Los tests que exigen `ml/models/phishing_model.pkl` se omiten si el modelo no está entrenado.

## Docker

El contexto del backend es la raíz del repo, porque la imagen copia `ml/` y `backend/`.

```bash
cp .env.example .env
docker compose up --build
docker compose -f docker-compose.prod.yml up --build -d
```

`VITE_API_URL` apunta a `http://localhost:8000` porque el navegador no resuelve el nombre `backend`.

## Métricas

Placeholder. Rellena tras `python ml/src/models/evaluate_model.py`.

| Métrica | Valor |
| --- | --- |
| Accuracy | — |
| Precision | — |
| Recall | — |
| F1 | — |
| ROC AUC | — |

## Roadmap

- Umbral configurable desde la UI.
- Explicaciones con importancia de features del modelo.
- Reentrenamiento programado.

## Contribuir

Abre un issue o un PR contra `main`. `make test` y `make lint` deben pasar.

## Licencia

MIT.

## Autor

Proyecto educativo de detección de phishing por URL. Dataset LegitPhish: Potpelwar, Kulkarni y Waghmare, Mendeley Data, DOI 10.17632/hx4m73v2sf.2, CC BY 4.0.
