.PHONY: install backtest test lint format report verdict clean coverage

ifeq ($(OS),Windows_NT)
	VENV_BIN := .venv/Scripts
else
	VENV_BIN := .venv/bin
endif
PYTHON := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip
PYTEST := $(VENV_BIN)/pytest
RUFF := $(VENV_BIN)/ruff
MYPY := $(VENV_BIN)/mypy

install:
	python -m venv .venv
	$(PIP) install -e ".[dev]"

backtest:
	$(PYTHON) scripts/run_backtest.py

refresh-data:
	$(PYTHON) scripts/refresh_data.py

test:
	$(PYTEST) tests/ -v

coverage:
	$(PYTEST) tests/ --cov=src --cov-report=term-missing --cov-report=html

lint:
	$(RUFF) check src/ tests/ scripts/
	$(MYPY) src/

format:
	$(RUFF) format src/ tests/ scripts/

report:
	$(PYTHON) -c "from src.reporting import generate_verdict; generate_verdict()"

clean:
	rm -rf .venv data/*.parquet reports/*.png reports/*.html .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
