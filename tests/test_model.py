# Tests for the model class, the saved files, and predict()

import torch

from src.config import INPUT_SIZE, MODEL_DIR
from src.model_definition import DepressionModel, predict, risk_level

MODEL_PATH = MODEL_DIR / "depression_model.pth"
ENCODER_PATH = MODEL_DIR / "encoder.joblib"
SCALER_PATH = MODEL_DIR / "scaler.joblib"


class TestDepressionModel:
    def test_output_shape_and_probabilities(self):
        model = DepressionModel(input_size=INPUT_SIZE)
        logits = model(torch.randn(1, INPUT_SIZE))
        assert logits.shape == (1, 2)
        probs = torch.nn.functional.softmax(logits, dim=1)
        assert torch.allclose(probs.sum(dim=1), torch.tensor([1.0]), atol=1e-5)

    def test_deterministic_in_eval(self):
        model = DepressionModel(input_size=INPUT_SIZE)
        model.eval()
        x = torch.randn(1, INPUT_SIZE)
        with torch.no_grad():
            assert torch.allclose(model(x), model(x))

    def test_layer_dimensions(self):
        model = DepressionModel(input_size=INPUT_SIZE)
        assert model.fc1.in_features == INPUT_SIZE
        assert model.fc3.out_features == 2


class TestModelFiles:
    def test_all_artifacts_exist(self):
        assert MODEL_PATH.exists()
        assert ENCODER_PATH.exists()
        assert SCALER_PATH.exists()

    def test_model_loads_and_runs(self):
        model = DepressionModel(input_size=INPUT_SIZE)
        model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
        model.eval()
        assert model(torch.randn(1, INPUT_SIZE)).shape == (1, 2)


class TestPredict:
    def test_returns_valid_probability(self, sample_answers):
        result = predict(sample_answers)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_low_and_high_risk_profiles(self, low_risk_answers, high_risk_answers):
        low = predict(low_risk_answers)
        high = predict(high_risk_answers)
        assert 0.0 <= low <= 1.0
        assert 0.0 <= high <= 1.0


class TestRiskLevel:
    def test_high_above_70(self):
        assert risk_level(90) == "high"
        assert risk_level(70) == "high"

    def test_moderate_between_40_and_69(self):
        assert risk_level(50) == "moderate"
        assert risk_level(40) == "moderate"
        assert risk_level(69.99) == "moderate"

    def test_low_below_40(self):
        assert risk_level(20) == "low"
        assert risk_level(0) == "low"
        assert risk_level(39.99) == "low"
