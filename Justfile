set shell := ["bash", "-c"]

default:
    @just --list

# Initializes the project (uv-based)
setup:
    uv venv
    uv sync --extra dev
    cp -n .env.example .env || true

# Starts development environment (fast prototyping)
dev:
    bash docker/entrypoint.sh

# Formats code (Black)
format:
    uv run --with black black src tests

# Checks code quality (read-only)
lint:
    uv run ruff check src tests
    uv run --with black black --check src tests
    uv run --with flake8 flake8 src tests

# Runs tests
test:
    uv run pytest

# Complete quality check (CI simulation)
check: lint typecheck test

# Build package (CI parity)
build:
    uv run --with build python -m build
    uv run --with twine twine check dist/*

# Build binaries (optional, CI parity)
binary:
    uv run --with pyinstaller python build_binary.py

# Full CI pipeline locally
ci: check build

# Type checking
typecheck:
    uv run mypy src

# Starts Docker containers (deployment testing)
docker-up:
    docker-compose up -d --build
    docker-compose logs -f

# Stops Docker containers
docker-down:
    docker-compose down

# Cleans artifacts
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache .coverage htmlcov .ruff_cache
