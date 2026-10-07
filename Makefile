.PHONY: help install train test lint dev docker-dev docker-prod clean

help:
	@echo "install       dependencias de ml, backend, tests y frontend"
	@echo "train         prepara el CSV y entrena XGBoost"
	@echo "test          pytest con cobertura"
	@echo "lint          ruff"
	@echo "dev           backend y frontend en local"
	@echo "docker-dev    compose de desarrollo"
	@echo "docker-prod   compose de producción"
	@echo "clean         cachés y node_modules"

install:
	python3 -m pip install -r ml/requirements.txt -r backend/requirements.txt -r requirements-dev.txt
	cd frontend && npm install

train:
	python ml/src/data/make_dataset.py
	python ml/src/models/train_model.py
	python ml/src/models/evaluate_model.py

test:
	python -m pytest

lint:
	python -m ruff check backend ml tests

dev:
	uvicorn app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8000 & \
	cd frontend && npm run dev

docker-dev:
	docker compose up --build

docker-prod:
	docker compose -f docker-compose.prod.yml up --build -d

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov frontend/node_modules frontend/dist
