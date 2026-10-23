set shell := ["bash", "-cu"]

# Override with PYTHON=/path/to/venv/bin/python (the pre-push hook inherits it).
py := env("PYTHON", "python")

default:
    @just --list

# Activate a Python environment with requirements-dev.txt installed first.

install:
    {{py}} -m pip install -r requirements.txt -r requirements-dev.txt -c constraints.txt
    npm --prefix frontend ci

dev:
    docker compose up --build

format:
    {{py}} -m black app/ scripts/ tests/

lint:
    {{py}} -m pylint app/ --disable=C0114,C0115,C0116,R0903,W0611 --fail-under=7.0
    npm --prefix frontend run lint

typecheck:
    {{py}} -m mypy app/ --ignore-missing-imports --no-strict-optional

test:
    {{py}} -m pytest

build:
    npm --prefix frontend run build

security:
    {{py}} -m bandit -r app/ -ll -q

browser: build
    cd frontend && npm run test:hydration

check: lint typecheck security test build

# Personal tooling (meto-ai recipes) lives in the untracked justfile.local.
import? 'justfile.local'
