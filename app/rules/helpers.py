import datetime
from typing import Any, Callable, Dict, Optional


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def get_by_path(obj: Dict[str, Any], path: str) -> Any:
    """Safely navigate nested dicts using dotted paths."""
    if not path:
        return None
    current: Any = obj
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def set_by_path(obj: Dict[str, Any], path: str, value: Any) -> None:
    """Set nested property using dotted path, creating intermediate dicts."""
    if not path:
        return
    parts = path.split(".")
    current = obj
    for p in parts[:-1]:
        if p not in current or not isinstance(current[p], dict):
            current[p] = {}
        current = current[p]
    current[parts[-1]] = value


# ---------------------------------------------------------------------------
# Transform library (age, etc.)
# ---------------------------------------------------------------------------

def transform_age_years(value: Any) -> Optional[int]:
    """Transform a date string (ISO format) into age in years."""
    if value is None:
        return None
    try:
        dob = datetime.date.fromisoformat(str(value))
    except ValueError:
        return None
    today = datetime.date.today()
    years = today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )
    return years


TRANSFORM_REGISTRY: Dict[str, Callable[[Any], Any]] = {
    "age_years": transform_age_years,
}
