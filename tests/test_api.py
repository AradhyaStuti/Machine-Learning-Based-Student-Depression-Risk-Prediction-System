# Tests for the REST API

import pytest
from fastapi.testclient import TestClient

from src.api import app

VALID_PAYLOAD = {
    "gender": "Male",
    "age": 24.0,
    "study_hours": 8.0,
    "academic_pressure": 3.0,
    "financial_stress": 3.0,
    "study_satisfaction": 3.0,
    "sleep_duration": "5-6 hours",
    "dietary_habits": "Moderate",
    "suicidal_thoughts": "No",
    "family_history": "No",
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Point the DB at a temp file for tests
    monkeypatch.setattr("src.database.DB_PATH", tmp_path / "test.db")
    with TestClient(app) as c:
        yield c


class TestRoot:
    def test_returns_name_and_disclaimer(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data and "disclaimer" in data
        assert "medical" in data["disclaimer"].lower()


class TestHealth:
    def test_returns_ok_with_model_status(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["model_loaded"] is True


class TestPredict:
    def test_valid_prediction(self, client):
        resp = client.post("/predict", json=VALID_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert 0 <= data["probability"] <= 100
        assert data["risk_level"] in ("low", "moderate", "high")
        assert "request_id" in data

    def test_deterministic(self, client):
        r1 = client.post("/predict", json=VALID_PAYLOAD).json()
        r2 = client.post("/predict", json=VALID_PAYLOAD).json()
        assert r1["probability"] == r2["probability"]

    def test_missing_field_returns_422(self, client):
        assert client.post("/predict", json={"gender": "Male"}).status_code == 422

    def test_age_out_of_range(self, client):
        assert client.post("/predict", json={**VALID_PAYLOAD, "age": 10.0}).status_code == 422
        assert client.post("/predict", json={**VALID_PAYLOAD, "age": 50.0}).status_code == 422

    def test_invalid_yes_no(self, client):
        bad = {**VALID_PAYLOAD, "suicidal_thoughts": "Maybe"}
        assert client.post("/predict", json=bad).status_code == 422

    def test_invalid_gender(self, client):
        bad = {**VALID_PAYLOAD, "gender": "Other"}
        assert client.post("/predict", json=bad).status_code == 422

    def test_invalid_sleep_duration(self, client):
        bad = {**VALID_PAYLOAD, "sleep_duration": "All day"}
        assert client.post("/predict", json=bad).status_code == 422

    def test_invalid_dietary_habits(self, client):
        bad = {**VALID_PAYLOAD, "dietary_habits": "Vegan"}
        assert client.post("/predict", json=bad).status_code == 422


class TestPredictions:
    def test_predict_then_retrieve_history(self, client):
        resp = client.post("/predict", json=VALID_PAYLOAD)
        rid = resp.json()["request_id"]
        history = client.get("/predictions").json()
        matching = [p for p in history if p["request_id"] == rid]
        assert len(matching) == 1

    def test_limit_is_clamped(self, client):
        # Even with a huge limit, the response shouldn't exceed the cap
        for _ in range(3):
            client.post("/predict", json=VALID_PAYLOAD)
        history = client.get("/predictions?limit=99999").json()
        assert len(history) <= 200
