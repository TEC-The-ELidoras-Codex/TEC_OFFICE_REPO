# TEC Office Repository Makefile
# Provides common development tasks

.PHONY: setup install test docker-build docker-up docker-down lint clean wp-test hf-upload help

# Default target
help:
	@echo "TEC Office Makefile"
	@echo "==================="
	@echo "Available targets:"
	@echo "  setup         - Initialize the project structure and virtual environment"
	@echo "  install       - Install dependencies from requirements.txt"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linting checks"
	@echo "  docker-build  - Build the Docker image"
	@echo "  docker-up     - Start Docker containers"
	@echo "  docker-down   - Stop Docker containers"
	@echo "  wp-test       - Test WordPress connection"
	@echo "  hf-upload     - Upload to Hugging Face Space"
	@echo "  clean         - Remove build artifacts and cache files"
	@echo "  help          - Show this help message"

# Setup the project structure and virtual environment
setup:
	python setup.py

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest -vv tests/

# Run linting checks
lint:
	flake8 src/ tests/ scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src/ tests/ scripts/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Docker operations
docker-build:
	python scripts/docker_manager.py build

docker-up:
	python scripts/docker_manager.py up --detached

docker-down:
	python scripts/docker_manager.py down

# WordPress testing
wp-test:
	python scripts/test_wordpress_connection.py

# Hugging Face Space upload
hf-upload:
	@echo "Please provide a Hugging Face username and space name"
	@read -p "Username: " username; \
	read -p "Space name: " spacename; \
	python scripts/huggingface_connection.py upload $$username $$spacename

# Clean up build artifacts and cache files
clean:
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
