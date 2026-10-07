.PHONY: all install dev dev-api dev-web test seed clean

PYTHON ?= apps/api/.venv/bin/python
PIP ?= apps/api/.venv/bin/pip
UVICORN ?= apps/api/.venv/bin/uvicorn
PYTEST ?= apps/api/.venv/bin/pytest

all: dev

install:
	@echo "==> Setting up Python virtual environment..."
	python3.12 -m venv apps/api/.venv || python3 -m venv apps/api/.venv
	$(PIP) install --upgrade pip
	$(PIP) install -r apps/api/requirements.txt
	@echo "==> Installing Node dependencies..."
	npm install --prefix apps/web

seed:
	@echo "==> Generating sample PDFs and ground truth..."
	$(PYTHON) sample_data/generate_samples.py
	@echo "==> Seeding database..."
	PYTHONPATH=apps/api $(PYTHON) -m app.services.seed

dev-api:
	@echo "==> Starting FastAPI backend on http://localhost:8000..."
	cd apps/api && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-web:
	@echo "==> Starting Next.js frontend on http://localhost:3000..."
	npm run dev --prefix apps/web

dev:
	@echo "==> Starting Recon-Bot in development mode..."
	@make -j 2 dev-api dev-web

test:
	@echo "==> Running backend test suite..."
	PYTHONPATH=apps/api $(PYTEST) apps/api/tests -v

build:
	@echo "==> Building Next.js production bundle..."
	npm run build --prefix apps/web

clean:
	rm -rf apps/api/__pycache__ apps/api/.pytest_cache apps/web/.next apps/web/out
