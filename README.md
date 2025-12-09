# FAFSA Validation Service
*A rules-driven FastAPI service for evaluating FAFSA-style application data*

This project implements a configurable validation engine that evaluates student financial aid application data (FAFSA-like payloads). Rules are defined externally in YAML and applied dynamically during validation, enabling clear separation between policy and code.

The service exposes a simple HTTP API for validating applications and returns structured errors, warnings, and passing rule results.

---

## 🚀 Features

- FastAPI-based API with automatic OpenAPI documentation
- Pydantic-based application model
- YAML-driven rules engine
- Structured validation output (`errors`, `warnings`, `successes`)
- Makefile workflows
- Unit + integration tests (Testcontainers)

---

## 🛠️ Requirements

- Python 3.10+
- uv (auto-installed by Makefile)
- Docker (optional, for integration tests or containerized run)

---

## 🚦 Quickstart Guide

View all available buildtool commands with `make`.
Below are the key Makefile commands:

| Command | Description |
|---------|-------------|
| `make dev` | run a local dev server |
| `make tests` | run entire test suite |
| `make clean` | reset build state |

If you've got the dev server running, endpoints can be visited at:

- http://localhost:8000/docs
- http://localhost:8000/health

---

## 🐳 Docker Usage

Build:

```
make build
```

Run:

```
docker run -p 8000:8000 eobi-app:latest
```

---

## 🧵 API Overview

POST `/validate` validates an application and returns:

```
{
  "valid": true/false,
  "errors": [...],
  "warnings": [...],
  "successes": [...]
}
```

---

## 📚 Notes

- Uses uv for dependency and environment management.
- Rules are externalized via YAML for flexibility and auditability.
- Integration tests use Testcontainers for realistic API testing.
