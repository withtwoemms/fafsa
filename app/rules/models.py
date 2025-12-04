import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.rules.helpers import get_by_path


# ---------------------------------------------------------------------------
# Core types
# ---------------------------------------------------------------------------

class RuleSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class Condition:
    field: str
    equals: Any


@dataclass
class RuleResult:
    name: str
    passed: bool
    severity: RuleSeverity
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationSummary:
    valid: bool
    errors: List[RuleResult]
    warnings: List[RuleResult]
    successes: List[RuleResult]


# ---------------------------------------------------------------------------
# Base Rule interface
# ---------------------------------------------------------------------------

class Rule(ABC):
    name: str
    severity: RuleSeverity
    when: Optional[Condition]

    @abstractmethod
    def apply(self, data: Dict[str, Any]) -> RuleResult:
        ...


# ---------------------------------------------------------------------------
# Rule shapes (discriminated by "type" in YAML)
# ---------------------------------------------------------------------------

@dataclass
class PresenceRule(Rule):
    name: str
    field: str
    severity: RuleSeverity = RuleSeverity.ERROR
    message: Optional[str] = None
    when: Optional[Condition] = None

    def apply(self, data: Dict[str, Any]) -> RuleResult:
        value = get_by_path(data, self.field)
        passed = value not in (None, "")
        return RuleResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=None if passed else self.message,
            details={"field": self.field, "value": value},
        )


@dataclass
class StringMatchRule(Rule):
    name: str
    field: str
    pattern: str
    severity: RuleSeverity = RuleSeverity.ERROR
    message: Optional[str] = None
    when: Optional[Condition] = None

    def apply(self, data: Dict[str, Any]) -> RuleResult:
        value = get_by_path(data, self.field)
        # "if present" semantics: missing value -> pass
        if value is None:
            return RuleResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message=None,
                details={"reason": "field_missing_treated_as_pass", "field": self.field},
            )

        passed = re.fullmatch(self.pattern, str(value)) is not None
        return RuleResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=None if passed else self.message,
            details={"field": self.field, "value": value, "pattern": self.pattern},
        )


@dataclass
class ValueComparisonRule(Rule):
    """
    Compare a field against a literal value (numeric).
    """
    name: str
    field: str
    operator: str  # "lt", "lte", "gt", "gte", "eq", "neq"
    value: Any
    severity: RuleSeverity = RuleSeverity.ERROR
    message: Optional[str] = None
    when: Optional[Condition] = None

    def apply(self, data: Dict[str, Any]) -> RuleResult:
        raw = get_by_path(data, self.field)
        if raw is None:
            # Missing field: treat as pass; separate rules handle "required"
            return RuleResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message=None,
                details={"reason": "field_missing_treated_as_pass", "field": self.field},
            )

        try:
            v = float(raw)
            threshold = float(self.value)
        except (TypeError, ValueError):
            return RuleResult(
                name=self.name,
                passed=False,
                severity=self.severity,
                message=self.message,
                details={"reason": "non_numeric", "field": self.field, "value": raw},
            )

        op_map = {
            "lt": v < threshold,
            "lte": v <= threshold,
            "gt": v > threshold,
            "gte": v >= threshold,
            "eq": v == threshold,
            "neq": v != threshold,
        }
        passed = op_map.get(self.operator, False)
        return RuleResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=None if passed else self.message,
            details={
                "field": self.field,
                "value": v,
                "operator": self.operator,
                "threshold": threshold,
            },
        )


@dataclass
class FieldComparisonRule(Rule):
    """
    Compare one field against another field (numeric).
    """
    name: str
    left_field: str
    operator: str  # "lt", "lte", "gt", "gte", "eq", "neq"
    right_field: str
    severity: RuleSeverity = RuleSeverity.ERROR
    message: Optional[str] = None
    when: Optional[Condition] = None

    def apply(self, data: Dict[str, Any]) -> RuleResult:
        left_raw = get_by_path(data, self.left_field)
        right_raw = get_by_path(data, self.right_field)

        try:
            left_val = float(left_raw)
            right_val = float(right_raw)
        except (TypeError, ValueError):
            return RuleResult(
                name=self.name,
                passed=False,
                severity=self.severity,
                message=self.message,
                details={
                    "reason": "non_numeric",
                    "left_field": self.left_field,
                    "left_value": left_raw,
                    "right_field": self.right_field,
                    "right_value": right_raw,
                },
            )

        op_map = {
            "lt": left_val < right_val,
            "lte": left_val <= right_val,
            "gt": left_val > right_val,
            "gte": left_val >= right_val,
            "eq": left_val == right_val,
            "neq": left_val != right_val,
        }
        passed = op_map.get(self.operator, False)
        return RuleResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=None if passed else self.message,
            details={
                "left_field": self.left_field,
                "left_value": left_val,
                "operator": self.operator,
                "right_field": self.right_field,
                "right_value": right_val,
            },
        )


@dataclass
class ValueInSetRule(Rule):
    name: str
    field: str
    allowed_values: List[Any]
    severity: RuleSeverity = RuleSeverity.ERROR
    message: Optional[str] = None
    when: Optional[Condition] = None

    def apply(self, data: Dict[str, Any]) -> RuleResult:
        value = get_by_path(data, self.field)
        passed = value in self.allowed_values
        return RuleResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=None if passed else self.message,
            details={
                "field": self.field,
                "value": value,
                "allowed_values": self.allowed_values,
            },
        )


@dataclass
class RequiresRule(Rule):
    """
    IF condition (when) holds, THEN all required_fields must be present and non-empty.
    """
    name: str
    required_fields: List[str]
    severity: RuleSeverity = RuleSeverity.ERROR
    message: Optional[str] = None
    when: Optional[Condition] = None

    def apply(self, data: Dict[str, Any]) -> RuleResult:
        missing: List[str] = []
        for path in self.required_fields:
            val = get_by_path(data, path)
            if val in (None, ""):
                missing.append(path)

        passed = not missing
        return RuleResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=None if passed else self.message,
            details={"missing_fields": missing} if not passed else None,
        )


# Transform rules don’t produce validation results; they mutate data.
@dataclass
class TransformRule:
    name: str
    field: str
    transform: str
    output_field: str
