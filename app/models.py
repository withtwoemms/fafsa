from datetime import date
from typing import Optional, Literal

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Simple Primitive Models
# ---------------------------------------------------------------------------

class StudentInfo(BaseModel):
    firstName: str
    lastName: str
    ssn: str                   # pattern rules handled by rules engine
    dateOfBirth: date          # parsed to actual datetime.date
    

class SpouseInfo(BaseModel):
    name: str
    ssn: str                   # validated by string_match rule if present


class Household(BaseModel):
    numberInHousehold: int
    numberInCollege: int


class Income(BaseModel):
    studentIncome: float
    parentIncome: Optional[float] = None


# ---------------------------------------------------------------------------
# Main FAFSA Application Model
# ---------------------------------------------------------------------------

class ApplicationData(BaseModel):
    studentInfo: StudentInfo
    household: Household
    income: Income
    spouseInfo: Optional[SpouseInfo] = None

    stateOfResidence: str  # validated by value_in_set rule

    dependencyStatus: Literal["dependent", "independent"]
    maritalStatus: Literal["single", "married"]

    # convenience: sometimes we modify the payload for rule engine
    # this ensures only known fields appear unless extra configured
    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
    }
