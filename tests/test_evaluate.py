# Tests for src/evaluate.py

from src.evaluate import baseline_logistic_regression, evaluate_model


class TestEvaluateModel:
    def test_returns_all_metrics(self):
        metrics = evaluate_model()
        for key in ("accuracy", "precision", "recall", "f1", "roc_auc", "confusion_matrix"):
            assert key in metrics

    def test_metrics_in_valid_range(self):
        metrics = evaluate_model()
        for key in ("accuracy", "precision", "recall", "f1", "roc_auc"):
            assert 0.0 <= metrics[key] <= 1.0

    def test_accuracy_above_baseline(self):
        metrics = evaluate_model()
        assert metrics["accuracy"] > 0.60


class TestLogisticRegressionBaseline:
    def test_baseline_runs_and_returns_metrics(self):
        results = baseline_logistic_regression()
        for key in ("accuracy", "f1", "roc_auc"):
            assert key in results
            assert 0.0 <= results[key] <= 1.0
