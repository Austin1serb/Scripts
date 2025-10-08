.PHONY: help install install-dev test clean run

help:
	@echo "Photo Organizer - Makefile Commands"
	@echo "===================================="
	@echo "make install      - Install package and dependencies"
	@echo "make install-dev  - Install with dev dependencies"
	@echo "make test         - Run tests"
	@echo "make test-cov     - Run tests with coverage report"
	@echo "make clean        - Remove build artifacts and caches"
	@echo "make run          - Run with default settings (dry-run)"
	@echo "make lint         - Run linting checks"
	@echo "make format       - Format code with black"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov black pylint

test:
	pytest tests/ -v

test-cov:
	pytest --cov=photo_organizer --cov-report=html --cov-report=term tests/
	@echo "Coverage report generated in htmlcov/index.html"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

run:
	python -m photo_organizer.cli run \
		--input "$$HOME/Desktop/RC Photos" \
		--output "./organized" \
		--rotate-cities \
		--dry-run

lint:
	pylint photo_organizer/

format:
	black photo_organizer/ tests/
