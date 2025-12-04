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

## 📦 Installing Dependencies

```
make install
```

Install only test dependencies:

```
make install-test
```

---

## ▶️ Running the Development Server

```
make run
```

Visit:

- http://localhost:8000/docs
- http://localhost:8000/health

---

## 🧪 Running Tests

Run unit tests:

```
make unit-tests
```

Run integration tests:

```
make integration-tests
```

Run all tests:

```
make tests
```

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

## 👨‍💻 Development Workflow Summary

| Task | Command |
|------|---------|
| Install deps | make install |
| Run dev server | make run |
| Unit tests | make unit-tests |
| Integration tests | make integration-tests |
| Build Docker image | make build |

---

## 📚 Notes

- Uses uv for dependency and environment management.
- Rules are externalized via YAML for flexibility and auditability.
- Integration tests use Testcontainers for realistic API testing.
