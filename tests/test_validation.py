# Tests for src/validation.py

from src.validation import all_fields_filled, validate_age, validate_study_hours


class TestValidateAge:
    def test_valid_ages_accepted(self):
        for value in ["18", "24", "34"]:
            assert validate_age(value).valid is True

    def test_out_of_range_rejected(self):
        for value in ["17", "35"]:
            assert validate_age(value).valid is False

    def test_non_numeric_rejected(self):
        for value in ["abc", "", "25.5"]:
            assert validate_age(value).valid is False


class TestValidateStudyHours:
    def test_valid_hours_accepted(self):
        for value in ["0", "8", "12"]:
            assert validate_study_hours(value).valid is True

    def test_out_of_range_rejected(self):
        for value in ["13", "100"]:
            assert validate_study_hours(value).valid is False

    def test_non_numeric_rejected(self):
        for value in ["abc", "", "8.5"]:
            assert validate_study_hours(value).valid is False


class TestAllFieldsFilled:
    def test_all_filled(self):
        assert all_fields_filled({"a": ["x"], "b": [1]}) is True

    def test_none_means_unfilled(self):
        assert all_fields_filled({"a": [None]}) is False
