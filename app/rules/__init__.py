from typing import Any, Dict


def _get_by_path(data: Dict[str, Any], path: str) -> Any:
    """
    Safely get a nested field from a dict using a dotted path, e.g.
    'studentInfo.dateOfBirth' -> data["studentInfo"]["dateOfBirth"].
    Returns None if any part of the path is missing.
    """
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current
