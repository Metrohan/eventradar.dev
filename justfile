set shell := ["bash", "-cu"]

default:
    @just --list

# Activate a Python environment with requirements-dev.txt installed first.

install:
    python -m pip install -r requirements.txt -r requirements-dev.txt
    npm --prefix frontend ci

dev:
    docker compose up --build

format:
    python -m black app/ scripts/ tests/

lint:
    python -m pylint app/ --disable=C0114,C0115,C0116,R0903,W0611 --fail-under=7.0
    npm --prefix frontend run lint

typecheck:
    python -m mypy app/ --ignore-missing-imports --no-strict-optional

test:
    python -m pytest

build:
    npm --prefix frontend run build

security:
    python -m bandit -r app/ -ll -q

browser: build
    cd frontend && npm run test:hydration

check: lint typecheck security test build

# Personal tooling (meto-ai recipes) lives in the untracked justfile.local.
import? 'justfile.local'
