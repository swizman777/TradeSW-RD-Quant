.PHONY: install backtest test lint format report verdict clean coverage

install:
	python -m venv .venv
	.venv/Scripts/pip install -e ".[dev]"

backtest:
	.venv/Scripts/python scripts/run_backtest.py

refresh-data:
	.venv/Scripts/python scripts/refresh_data.py

test:
	.venv/Scripts/pytest tests/ -v

coverage:
	.venv/Scripts/pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

lint:
	.venv/Scripts/ruff check src/ tests/ scripts/
	.venv/Scripts/mypy src/

format:
	.venv/Scripts/ruff format src/ tests/ scripts/

report:
	.venv/Scripts/python -c "from src.reporting import generate_verdict; generate_verdict()"

clean:
	rm -rf .venv data/*.parquet reports/*.png reports/*.html .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
