# Tests for the SQLite prediction history

import json
from unittest.mock import patch

import pytest

from src.database import (
    clear_predictions,
    count_by_risk_level,
    get_predictions,
    init_db,
    save_prediction,
)


@pytest.fixture(autouse=True)
def _use_temp_db(tmp_path):
    # Point the DB at a temp file for each test
    db_file = tmp_path / "test.db"
    with patch("src.database.DB_PATH", db_file):
        init_db()
        yield


class TestSavePrediction:
    def test_save_and_retrieve(self):
        save_prediction("req-001", {"age": 24, "gender": "Male"}, 72.5, "high")
        rows = get_predictions(limit=10)
        assert len(rows) == 1
        assert rows[0]["request_id"] == "req-001"
        assert rows[0]["probability"] == 72.5

    def test_input_stored_as_json(self):
        save_prediction("req-002", {"key": "value"}, 50.0, "moderate")
        rows = get_predictions(limit=10)
        assert json.loads(rows[0]["input_json"]) == {"key": "value"}

    def test_ordering_newest_first(self):
        for i in range(5):
            save_prediction(f"req-{i}", {}, float(i * 10), "low")
        rows = get_predictions(limit=10)
        assert rows[0]["request_id"] == "req-4"

    def test_limit_works(self):
        for i in range(10):
            save_prediction(f"req-{i}", {}, 0.0, "low")
        assert len(get_predictions(limit=3)) == 3

    def test_timestamp_is_set(self):
        save_prediction("req-ts", {}, 0.0, "low")
        assert get_predictions(limit=1)[0]["timestamp"] is not None


class TestClearAndCount:
    def test_clear_empties_the_table(self):
        save_prediction("req-1", {}, 0.0, "low")
        save_prediction("req-2", {}, 0.0, "high")
        assert len(get_predictions()) == 2
        clear_predictions()
        assert get_predictions() == []

    def test_count_by_risk_level(self):
        save_prediction("a", {}, 10.0, "low")
        save_prediction("b", {}, 50.0, "moderate")
        save_prediction("c", {}, 80.0, "high")
        save_prediction("d", {}, 85.0, "high")
        counts = count_by_risk_level()
        assert counts == {"low": 1, "moderate": 1, "high": 2}

    def test_count_when_empty(self):
        assert count_by_risk_level() == {}
