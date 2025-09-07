# Food Receipt Analyzer - Development Makefile
.PHONY: install test test-unit test-integration test-error-handling demo clean lint format help

isort:
	isort .

black:
	black .

# Installation and setup
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-mock black flake8 mypy

# Testing
test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/test_models.py tests/test_database.py tests/test_computer_vision.py tests/test_ai_query.py -v

test-integration:
	python -m pytest tests/test_integration.py tests/test_complete_flow.py -v

test-error-handling:
	python scripts/run_error_tests.py

# Demos
demo-cv:
	python demos/demo_computer_vision.py

demo-ai:
	python demos/demo_ai_query.py

demo-db:
	python demos/demo_database.py

demo-vector:
	python demos/demo_vector_db.py

demo-complete:
	python demos/demo_complete_system.py

# Debug tools
debug-ai:
	python debug/debug_ai_query.py

debug-db:
	python debug/debug_database.py

debug-parsing:
	python debug/debug_parsing.py

# Development tools
check-install:
	python scripts/check_installation.py

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black . --line-length=100

type-check:
	mypy . --ignore-missing-imports

# Application
run:
	streamlit run app.py

run-app:
	python run_app.py

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf uploads/*.jpg uploads/*.png uploads/*.pdf

clean-data:
	rm -f data/receipts.db

# Help
help:
	@echo "Food Receipt Analyzer - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  check-install    Check installation and dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-error-handling Run error handling tests"
	@echo ""
	@echo "Demos:"
	@echo "  demo-cv          Run computer vision demo"
	@echo "  demo-ai          Run AI query demo"
	@echo "  demo-db          Run database demo"
	@echo "  demo-vector      Run vector search demo"
	@echo "  demo-complete    Run complete system demo"
	@echo ""
	@echo "Debug:"
	@echo "  debug-ai         Debug AI query processing"
	@echo "  debug-db         Debug database operations"
	@echo "  debug-parsing    Debug receipt parsing"
	@echo ""
	@echo "Development:"
	@echo "  lint             Run code linting"
	@echo "  format           Format code with black"
	@echo "  type-check       Run type checking with mypy"
	@echo ""
	@echo "Application:"
	@echo "  run              Start Streamlit application"
	@echo "  run-app          Start application with run_app.py"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean            Clean temporary files and caches"
	@echo "  clean-data       Clean database (WARNING: deletes all data)"
	@echo ""
	@echo "Help:"
	@echo "  help             Show this help message"