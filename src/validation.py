# Input validation for the GUI

from dataclasses import dataclass

AGE_MIN = 18
AGE_MAX = 34
STUDY_HOURS_MIN = 0
STUDY_HOURS_MAX = 12


@dataclass
class ValidationResult:
    valid: bool
    error: str = ""


def validate_age(value):
    # Age must be a whole number between 18 and 34
    value = value.strip()
    if not value.isnumeric():
        return ValidationResult(False, "Age must be a number.")
    age = int(value)
    if age < AGE_MIN or age > AGE_MAX:
        return ValidationResult(False, f"Age must be between {AGE_MIN} and {AGE_MAX}.")
    return ValidationResult(True)


def validate_study_hours(value):
    # Study hours must be a whole number between 0 and 12
    value = value.strip()
    if not value.isnumeric():
        return ValidationResult(False, "Study hours must be a number.")
    hours = int(value)
    if hours < STUDY_HOURS_MIN or hours > STUDY_HOURS_MAX:
        return ValidationResult(
            False,
            f"Study hours must be between {STUDY_HOURS_MIN} and {STUDY_HOURS_MAX}.",
        )
    return ValidationResult(True)


def all_fields_filled(answers):
    # True only if every field has a value
    return all(v[0] is not None for v in answers.values())
