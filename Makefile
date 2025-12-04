# --- Configuration ---
PYTHON ?= python3
UV_BIN := $(shell command -v uv 2>/dev/null)
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
	@echo "  ${CYAN}uv${RESET}                - Download uv if not installed"
	@echo "  ${CYAN}venv${RESET}              - Create a local virtual environment (.venv) using uv"
	@echo "  ${CYAN}install${RESET}           - Install dependencies via uv"
	@echo "  ${CYAN}install-test${RESET}      - Install test dependencies via uv"
	@echo "  ${CYAN}requirements${RESET}      - Render dependencies as requirements.txt"
	@echo "  ${CYAN}run${RESET}               - Run dev server"
	@echo "  ${CYAN}build${RESET}             - Build Docker image for the app"
	@echo "  ${CYAN}tests${RESET}             - Run all tests"
	@echo "  ${CYAN}unit-tests${RESET}        - Run unit tests"
	@echo "  ${CYAN}integration-tests${RESET} - Run container tests"
	@echo

uv:
ifndef UV_BIN
	@echo "${GREEN}Installing uv...${RESET}"
	@curl -LsSf https://astral.sh/uv/install.sh | sh
else
	@echo "${CYAN}uv already installed.${RESET}"
endif

install-test:
	@uv sync --extra test

install: uv install-test
	@echo "${GREEN}Installing dependencies with uv...${RESET}"
	@uv sync

requirements:
	@uv export -o requirements.txt --no-extra test --no-hashes --no-editable --format requirements-txt

run: install
	@uv run fastapi run $(APP) --reload

build: requirements
	@echo "${GREEN}Building Docker image: $(IMAGE)${RESET}"
	docker build -t $(IMAGE) .

unit-tests:
	@pytest -s -v tests/unit

integration-tests: build
	@pytest -s -v tests/integration

tests: unit-tests integration-tests

venv:
	@echo "${GREEN}Creating local virtual environment (.venv) with uv...${RESET}"
	@uv venv .venv
	@echo "${CYAN}To activate:${RESET} source .venv/bin/activate"

.PHONY: help uv install install-test requirements run build unit-tests integration-tests tests venv