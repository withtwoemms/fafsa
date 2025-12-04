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
