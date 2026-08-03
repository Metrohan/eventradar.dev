set shell := ["bash", "-cu"]

default:
    @just --list

# Replace placeholders with real commands.

install:
    @echo "Configure dependency installation"

dev:
    @echo "Configure development startup"

format:
    @echo "Configure formatting"

lint:
    @echo "Configure linting"

typecheck:
    @echo "Configure type checking"

test:
    @echo "Configure tests"

check: lint typecheck test
    @echo "Configured checks completed"

task id title:
    meto-ai task "{{id}}" "{{title}}"

next id="":
    meto-ai next "{{id}}"

review id="":
    meto-ai review "{{id}}"

checkpoint id="":
    meto-ai checkpoint "{{id}}"

doctor:
    meto-ai doctor
