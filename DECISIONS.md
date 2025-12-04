# DECISIONS.md
Decision Log for FAFSA Validation Service

This document records key architectural choices, trade-offs, and reasoning that shaped the design of the FAFSA Validation Service. It provides maintainers and reviewers with a clear understanding of why the system is built the way it is.

---

## 1. Makefile as a Developer Workflow Orchestrator
**Decision:** Provide Make targets for common workflows.

**Rationale:**
- Ensures consistent behavior across developer machines.
- Reduces onboarding complexity.
- Encourages reproducible builds and test runs.

---

## 2. Dockerfile Strategy

**Decision:** Use a single-stage Dockerfile based on `python:3.14-slim`.

**Rationale:**
- Keeps the container build simple and easy to understand.
- Avoids premature complexity while the project is in early development.
- The `slim` base image provides a good balance of size and compatibility.
- Direct `pip install` keeps iterations quick for local development and testing.

**Trade-offs:**
- The final image includes both build and runtime dependencies, making it larger than an optimized multi-stage image.
- Installing dependencies directly in the image reduces cache efficiency—any change to `requirements.txt` or `pyproject.toml` invalidates the whole layer.
- Future production deployments may benefit from a multi-stage or uv-based build for improved security, size, and reproducibility.

**Future Considerations:**
- Introduce a multi-stage Dockerfile separating build and runtime environments.
- Explore using `uv` for deterministic dependency resolution and smaller images.
- Add build caching optimization once the dependency set stabilizes.

---

## 3. Use of uv as the Build + Dependency Tool
**Decision:** Adopt `uv` for dependency management and runtime execution.

**Rationale:**
- Extremely fast dependency syncing.
- Deterministic lockfile (`uv.lock`).
- Works seamlessly with FastAPI and pytest.
- Simplifies container builds by avoiding heavy virtualenv tools.

---

## 4. Directory Structure Organization
**Decision:** Separate tests into `unit/` and `integration/`.

```
tests/
  unit/          # Engine logic, pure Python
  integration/   # API tests using Docker & Testcontainers
```

**Rationale:**
- Unit tests should never require Docker.
- Integration tests should validate real HTTP behavior and startup lifecycle.
- Supports CI pipelines with stage gating.

---

## 5. Use of FastAPI for the Application Layer
**Decision:** Build the HTTP API using FastAPI.

**Rationale:**
- Native support for Pydantic models and async execution.
- Automatic OpenAPI documentation reduces development overhead.
- Clear dependency injection model for testability.
- Excellent developer ergonomics.

**Alternatives Considered:**
- Flask — requires more manual validation work.
- Django REST Framework — too heavy for a small microservice.

---

## Future Considerations
- Rules Engine architecture and output formats
- Versioned rule sets for policy changes across academic years.
- Rule caching and hot-reload for operational environments.
- A rules authoring UI for non-engineering stakeholders.
- Moving rule definitions to a database or remote config service.
- Adding INFO or SKIPPED rule severities for deeper audit logging.

---

## Summary
The above decisions create a service that is:

- maintainable  
- auditable  
- extendable  
- consistent  
- easy to integrate  

This document should be updated anytime a significant architectural or policy-impacting decision is made.
