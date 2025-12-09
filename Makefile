# --- Configuration ---
PYTHON ?= python3
UV_BIN := $(shell command -v uv 2>/dev/null)
UV_VENV ?= .venv
UV_INSTALLED := .uv-installed
DEPS_STAMP := ${UV_VENV}/.deps-installed
APP := app/main.py
IMAGE := eobi-app:latest

# --- Color Setup ---
GREEN := \033[0;32m
CYAN := \033[0;36m
YELLOW := \033[1;33m
RESET := \033[0m

# --- Help Command ---
help:
	@echo "\n${YELLOW}Available commands:${RESET}\n"
	@echo "  ${CYAN}venv${RESET}              - Create local virtual environment @ \"${UV_VENV}/\" replete with dependencies using uv"
	@echo "  ${CYAN}dev${RESET}               - Run dev server"
	@echo "  ${CYAN}requirements${RESET}      - Render dependencies as requirements.txt"
	@echo "  ${CYAN}build${RESET}             - Build Docker image for the app"
	@echo "  ${CYAN}tests${RESET}             - Run all tests"
	@echo "  ${CYAN}unit-tests${RESET}        - Run unit tests"
	@echo "  ${CYAN}integration-tests${RESET} - Run container tests"
	@echo "  ${CYAN}clean${RESET}             - Clean build artifacts and dependency state"
	@echo

${UV_INSTALLED}:
ifndef UV_BIN
	@echo "${GREEN}Installing uv...${RESET}"
	@curl -LsSf https://astral.sh/uv/install.sh | sh
else
	@echo "${CYAN}uv already installed.${RESET}"
endif
	@touch ${UV_INSTALLED}

install-test: ${UV_INSTALLED}
	@uv sync --extra test

install: ${UV_INSTALLED} install-test
	@echo "${GREEN}Installing dependencies with uv...${RESET}"
	@uv sync

requirements: ${UV_INSTALLED}
	@uv export -o requirements.txt --no-extra test --no-hashes --no-editable --format requirements-txt

dev: ${UV_INSTALLED} ${DEPS_STAMP}
	@uv run fastapi run $(APP) --reload

build: requirements
	@echo "${GREEN}Building Docker image: $(IMAGE)${RESET}"
	docker build -t $(IMAGE) .

unit-tests: ${UV_INSTALLED} ${DEPS_STAMP}
	@uv run pytest -s -v tests/unit

integration-tests: ${UV_INSTALLED} build ${DEPS_STAMP}
	@uv run pytest -s -v tests/integration

tests: unit-tests integration-tests

${UV_VENV}: ${UV_INSTALLED}
	@echo "${GREEN}Creating local virtual environment (${UV_VENV})...${RESET}"
	@uv venv ${UV_VENV}

${DEPS_STAMP}: pyproject.toml uv.lock | ${UV_VENV}
	@echo "Syncing dependencies into ${UV_VENV}"
	@UV_VENV=${UV_VENV} uv sync --extra test
	@touch ${DEPS_STAMP}

venv: ${UV_INSTALLED} ${DEPS_STAMP}
	@echo "${GREEN}Installing all dependencies into ${UV_VENV}...${RESET}"
	@UV_VENV=${UV_VENV} uv sync --extra test
	@echo "${CYAN}Done.${RESET}"
	@echo "${CYAN}Activate with:${RESET} source ${UV_VENV}/bin/activate"

clean:
	@echo "${GREEN}Cleaning build artifacts and dependency state...${RESET}"
	@rm -f ${DEPS_STAMP} ${UV_INSTALLED}
	@rm -rf ${UV_VENV} .uv_cache .pytest_cache
	@find . -type d -name __pycache__ -exec rm -rf {} +


.PHONY: help install install-test requirements dev build unit-tests integration-tests tests venv clean