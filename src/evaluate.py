# Evaluate the saved model and compare against a logistic regression baseline
# Run with: python -m src.evaluate

import logging

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from src.config import (
    DATA_PATH,
    FEATURE_COLUMNS,
    INPUT_SIZE,
    MODEL_DIR,
    RANDOM_STATE,
    TARGET_COLUMN,
    TRAIN_TEST_SPLIT,
)
from src.model_definition import DepressionModel, add_interactions

logger = logging.getLogger(__name__)


def _prepare_split():
    # Load the dataset, transform it, and return the same train/test split
    # the neural net was trained on
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. "
            "Place the Kaggle 'Student Depression Dataset.csv' in data/."
        )
    df = pd.read_csv(DATA_PATH)
    df = df[[*FEATURE_COLUMNS, TARGET_COLUMN]].dropna()

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    categorical_cols = X.select_dtypes(include=["object"]).columns
    numerical_cols = X.select_dtypes(exclude=["object"]).columns

    encoder = joblib.load(MODEL_DIR / "encoder.joblib")
    scaler = joblib.load(MODEL_DIR / "scaler.joblib")

    encoded = encoder.transform(X[categorical_cols])
    scaled = scaler.transform(X[numerical_cols])
    X_processed = add_interactions(np.hstack((encoded, scaled)))

    X_train, X_test, y_train, y_test = train_test_split(
        X_processed,
        y,
        test_size=TRAIN_TEST_SPLIT,
        random_state=RANDOM_STATE,
    )
    return X_train, X_test, y_train.values, y_test.values


def evaluate_model():
    # Compute metrics for the saved neural network on the test split
    logger.info("Evaluating neural network from %s", MODEL_DIR)
    _, X_test, _, y_test = _prepare_split()

    model = DepressionModel(input_size=INPUT_SIZE)
    model.load_state_dict(torch.load(MODEL_DIR / "depression_model.pth", weights_only=True))
    model.eval()

    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
    with torch.no_grad():
        logits = model(X_test_tensor)
        probs = F.softmax(logits, dim=1)[:, 1].numpy()
        y_pred = probs.round().astype(int)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probs),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "classification_report": classification_report(y_test, y_pred, zero_division=0),
    }

    logger.info(
        "Accuracy: %.4f | F1: %.4f | ROC-AUC: %.4f",
        metrics["accuracy"],
        metrics["f1"],
        metrics["roc_auc"],
    )
    return metrics


def baseline_logistic_regression():
    # Train a quick logistic regression on the same features as a sanity check
    X_train, X_test, y_train, y_test = _prepare_split()

    lr = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
    y_prob = lr.predict_proba(X_test)[:, 1]

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_prob),
    }


def _print_confusion_matrix(cm):
    # cm comes back as [[TN, FP], [FN, TP]] from sklearn for binary tasks
    tn, fp, fn, tp = cm.ravel()
    print(f"  True Negatives:  {tn}")
    print(f"  False Positives: {fp}")
    print(f"  False Negatives: {fn}")
    print(f"  True Positives:  {tp}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    nn_results = evaluate_model()
    print("\n=== Neural Network ===")
    print(f"Accuracy:   {nn_results['accuracy']:.4f}")
    print(f"Precision:  {nn_results['precision']:.4f}")
    print(f"Recall:     {nn_results['recall']:.4f}")
    print(f"F1 Score:   {nn_results['f1']:.4f}")
    print(f"ROC-AUC:    {nn_results['roc_auc']:.4f}")
    print("\nConfusion Matrix:")
    _print_confusion_matrix(nn_results["confusion_matrix"])
    print("\nClassification Report:")
    print(nn_results["classification_report"])

    print("=== Baseline: Logistic Regression ===")
    lr_results = baseline_logistic_regression()
    print(f"Accuracy:   {lr_results['accuracy']:.4f}")
    print(f"F1 Score:   {lr_results['f1']:.4f}")
    print(f"ROC-AUC:    {lr_results['roc_auc']:.4f}")
