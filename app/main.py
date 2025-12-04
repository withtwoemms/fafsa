from pathlib import Path
from typing import Any, Dict

from fastapi import Depends, FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse

from app.models import ApplicationData
from app.rules.engine import RulesEngine, ValidationSummary


app = FastAPI(
    title="FAFSA Validation Service",
    version="1.0.0",
    description="Applies FAFSA edit rules to application data."
)


# ---------------------------------------------------------------------------
# Load rules once at startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup ---------------------------------------------------------------
    configured_rules_filepath = Path(__file__).parent / "config/rules.yaml"
    app.state.rules_engine = RulesEngine.from_yaml(
        configured_rules_filepath.absolute()
    )

    yield   # <-- application runs here

    # Shutdown --------------------------------------------------------------
    # (no-op for now, but here's the place for future cleanup)
    # e.g., close DB connections, release cached data, etc.


def get_rules_engine(request: Request) -> RulesEngine:
    if not hasattr(request.app.state, "rules_engine"):
        rules_path = Path(__file__).parent / "config" / "rules.yaml"
        request.app.state.rules_engine = RulesEngine.from_yaml(rules_path)
    return request.app.state.rules_engine


# ---------------------------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Validation Endpoint
# ---------------------------------------------------------------------------

@app.post("/validate")
def validate_application(payload: ApplicationData, engine: RulesEngine = Depends(get_rules_engine),):
    """
    Accepts FAFSA application data, applies the configured rules,
    and returns the validation summary.
    """
    data: Dict[str, Any] = payload.model_dump()
    summary: ValidationSummary = engine.validate(data)

    response = {
        "valid": summary.valid,
        "errors": [
            {
                "rule": err.name,
                "severity": err.severity.value,
                "message": err.message,
                "details": err.details,
            }
            for err in summary.errors
        ],
        "warnings": [
            {
                "rule": warn.name,
                "severity": warn.severity.value,
                "message": warn.message,
                "details": warn.details,
            }
            for warn in summary.warnings
        ],
        "passed": [
            {
                "rule": res.name,
                "passed": res.passed,
                "severity": res.severity.value,
                "message": res.message,
                "details": res.details,
            }
            for res in summary.successes
        ],
    }

    # HTTP 200 always; validity is reported in the body
    return JSONResponse(content=response)
