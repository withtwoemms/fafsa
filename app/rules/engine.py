import yaml
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from app.rules import helpers
from app.rules.models import (
    Condition,
    FieldComparisonRule,
    PresenceRule,
    RequiresRule,
    Rule,
    RuleResult,
    RuleSeverity,
    StringMatchRule,
    TransformRule,
    ValidationSummary,
    ValueComparisonRule,
    ValueInSetRule,
)


# ---------------------------------------------------------------------------
# Rule factory (discriminated by "type")
# ---------------------------------------------------------------------------

def _condition_from(raw: Optional[Dict[str, Any]]) -> Optional[Condition]:
    if not raw:
        return None
    return Condition(field=raw["field"], equals=raw["equals"])


def rule_from_dict(raw: Dict[str, Any]) -> Rule | TransformRule:
    rtype = raw["type"]

    if rtype == "transform":
        return TransformRule(
            name=raw["name"],
            field=raw["field"],
            transform=raw["transform"],
            output_field=raw["output_field"],
        )

    severity = RuleSeverity(raw.get("severity", "error"))
    message = raw.get("message")
    when = _condition_from(raw.get("when"))

    if rtype == "presence":
        return PresenceRule(
            name=raw["name"],
            field=raw["field"],
            severity=severity,
            message=message,
            when=when,
        )
    elif rtype == "string_match":
        return StringMatchRule(
            name=raw["name"],
            field=raw["field"],
            pattern=raw["pattern"],
            severity=severity,
            message=message,
            when=when,
        )
    elif rtype == "value_comparison":
        return ValueComparisonRule(
            name=raw["name"],
            field=raw["field"],
            operator=raw["operator"],
            value=raw["value"],
            severity=severity,
            message=message,
            when=when,
        )
    elif rtype == "field_comparison":
        return FieldComparisonRule(
            name=raw["name"],
            left_field=raw["left_field"],
            operator=raw["operator"],
            right_field=raw["right_field"],
            severity=severity,
            message=message,
            when=when,
        )
    elif rtype == "value_in_set":
        return ValueInSetRule(
            name=raw["name"],
            field=raw["field"],
            allowed_values=raw["allowed_values"],
            severity=severity,
            message=message,
            when=when,
        )
    elif rtype == "requires":
        return RequiresRule(
            name=raw["name"],
            required_fields=raw["required_fields"],
            severity=severity,
            message=message,
            when=when,
        )

    raise ValueError(f"Unsupported rule type: {rtype}")


# ---------------------------------------------------------------------------
# Rules Engine
# ---------------------------------------------------------------------------

class RulesEngine:
    def __init__(self, rules: List[Rule], transforms: List[TransformRule]):
        self._rules = rules
        self._transforms = transforms

    @classmethod
    def from_yaml(cls, path: str) -> RulesEngine:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        rules: List[Rule] = []
        transforms: List[TransformRule] = []

        for raw_rule in data.get("rules", []):
            rule = rule_from_dict(raw_rule)
            if isinstance(rule, TransformRule):
                transforms.append(rule)
            else:
                rules.append(rule)

        return cls(rules=rules, transforms=transforms)

    # Main entry point
    def validate(self, data: Dict[str, Any]) -> ValidationSummary:
        # 1. Apply all transforms (mutate data)
        self._apply_transforms(data)

        # 2. Apply real validation rules
        results: List[RuleResult] = []
        for rule in self._rules:
            # Skip if condition not met
            if rule.when and not self._condition_met(rule.when, data):
                results.append(
                    RuleResult(
                        name=rule.name,
                        passed=True,
                        severity=rule.severity,
                        message=None,
                        details={"reason": "condition_not_met"},
                    )
                )
                continue

            results.append(rule.apply(data))

        errors: List[RuleResult] = []
        warnings: List[RuleResult] = []
        successes: list[RuleResult] = []

        for result in results:
            if result.passed:
                successes.append(result)
            else:
                if result.severity == RuleSeverity.ERROR:
                    errors.append(result)
                elif result.severity == RuleSeverity.WARNING:
                    warnings.append(result)

        return ValidationSummary(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            successes=successes,
        )

    # Internal helpers

    def _apply_transforms(self, data: Dict[str, Any]) -> None:
        for t in self._transforms:
            func = helpers.TRANSFORM_REGISTRY.get(t.transform)
            if func is None:
                continue
            raw_value = helpers.get_by_path(data, t.field)
            derived = func(raw_value)
            helpers.set_by_path(data, t.output_field, derived)

    @staticmethod
    def _condition_met(cond: Condition, data: Dict[str, Any]) -> bool:
        return helpers.get_by_path(data, cond.field) == cond.equals
