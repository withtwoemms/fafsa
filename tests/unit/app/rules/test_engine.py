import copy
import pytest
from datetime import date, timedelta

from app.rules.engine import RulesEngine
from tests.fixtures import FIXTURESPATH


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture(scope="module")
def rules_engine():
    """Load the configured rules.yaml once."""
    rules_path = FIXTURESPATH / "rules.yaml"
    return RulesEngine.from_yaml(rules_path)


@pytest.fixture
def sample_application():
    """A baseline valid application; tests override fields as needed."""
    base = {
        "studentInfo": {
            "firstName": "John",
            "lastName": "Doe",
            "ssn": "123456789",
            "dateOfBirth": "2000-01-01",
        },
        "dependencyStatus": "dependent",
        "maritalStatus": "single",
        "household": {
            "numberInHousehold": 4,
            "numberInCollege": 1
        },
        "income": {
            "studentIncome": 15000,
            "parentIncome": 40000,
        },
        "stateOfResidence": "CA",
        "spouseInfo": None,
    }

    return copy.deepcopy(base)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def has_error(summary, rule_name: str) -> bool:
    return any(r.name == rule_name for r in summary.errors)

def has_warning(summary, rule_name: str) -> bool:
    return any(r.name == rule_name for r in summary.warnings)

def has_success(summary, rule_name: str) -> bool:
    return any(r.name == rule_name for r in summary.successes)

# ----------------------------------------------------------------------

def test_valid_application_passes(rules_engine, sample_application):
    summary = rules_engine.validate(sample_application)
    assert summary.valid
    assert len(summary.errors) == 0
    assert len(summary.warnings) == 0
    assert len(summary.successes) > 0


def test_age_must_be_at_least_14(rules_engine, sample_application):
    young_dob = date.today() - timedelta(days=10 * 365)
    sample_application["studentInfo"]["dateOfBirth"] = young_dob.isoformat()

    summary = rules_engine.validate(sample_application)

    assert has_error(summary, "student_age_minimum")
    err = next(r for r in summary.errors if r.name == "student_age_minimum")
    assert "14 years old" in (err.message or "")


def test_ssn_must_be_9_digits(rules_engine, sample_application):
    # First: valid case
    summary = rules_engine.validate(sample_application)
    assert not has_error(summary, "student_ssn_format")

    # Now violate rule
    sample_application["studentInfo"]["ssn"] = "invalid"
    summary = rules_engine.validate(sample_application)
    assert has_error(summary, "student_ssn_format")


def test_parent_income_required_for_dependents(rules_engine, sample_application):
    sample_application["dependencyStatus"] = "dependent"
    sample_application["income"]["parentIncome"] = None  # violate

    summary = rules_engine.validate(sample_application)

    assert has_error(summary, "parent_income_required_if_dependent")


def test_income_must_not_be_negative(rules_engine, sample_application):
    # Valid case
    summary = rules_engine.validate(sample_application)
    assert not has_error(summary, "student_income_non_negative")
    assert not has_error(summary, "parent_income_non_negative")

    # Now violate student income
    sample_application["income"]["studentIncome"] = -10
    summary = rules_engine.validate(sample_application)
    assert has_error(summary, "student_income_non_negative")

    # Now violate parent income
    sample_application["income"]["parentIncome"] = -20
    summary = rules_engine.validate(sample_application)
    assert has_error(summary, "parent_income_non_negative")


def test_college_count_not_exceed_household(rules_engine, sample_application):
    summary = rules_engine.validate(sample_application)
    assert not has_error(summary, "college_not_exceed_household")

    # Violate
    sample_application["household"]["numberInCollege"] = 10
    summary = rules_engine.validate(sample_application)
    assert has_error(summary, "college_not_exceed_household")


def test_state_code_valid(rules_engine, sample_application):
    summary = rules_engine.validate(sample_application)
    assert not has_error(summary, "state_code_valid")

    # Now invalid
    sample_application["stateOfResidence"] = "XX"
    summary = rules_engine.validate(sample_application)
    assert has_error(summary, "state_code_valid")


def test_married_requires_spouse_info(rules_engine, sample_application):
    # Valid married case
    sample_application["maritalStatus"] = "married"
    sample_application["spouseInfo"] = {
        "name": "Jane Doe",
        "ssn": "987654321"
    }
    summary = rules_engine.validate(sample_application)
    assert not has_error(summary, "married_requires_spouse_info")

    # Missing spouse name
    sample_application["spouseInfo"] = {"name": "", "ssn": "987654321"}
    summary = rules_engine.validate(sample_application)
    assert has_error(summary, "married_requires_spouse_info")

    # Missing spouse SSN
    sample_application["spouseInfo"] = {"name": "Jane Doe", "ssn": ""}
    summary = rules_engine.validate(sample_application)
    assert has_error(summary, "married_requires_spouse_info")
