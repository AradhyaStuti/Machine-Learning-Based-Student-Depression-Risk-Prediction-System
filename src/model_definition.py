# Neural network model: definition, training, and prediction

import logging

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from src.config import (
    BATCH_SIZE,
    CATEGORICAL_COLUMNS,
    DATA_PATH,
    FEATURE_COLUMNS,
    INPUT_SIZE,
    LEARNING_RATE,
    MODEL_DIR,
    NUM_EPOCHS,
    NUMERICAL_COLUMNS,
    RANDOM_STATE,
    TARGET_COLUMN,
    TRAIN_TEST_SPLIT,
)

logger = logging.getLogger(__name__)

# Display name -> API/snake_case name. Used by the GUI and the API.
FIELD_NAME_MAP = {
    "Gender": "gender",
    "Age": "age",
    "Work/Study Hours": "study_hours",
    "Academic Pressure": "academic_pressure",
    "Financial Stress": "financial_stress",
    "Study Satisfaction": "study_satisfaction",
    "Sleep Duration": "sleep_duration",
    "Dietary Habits": "dietary_habits",
    "Have you ever had suicidal thoughts ?": "suicidal_thoughts",
    "Family History of Mental Illness": "family_history",
}


def add_interactions(X):
    # Add 3 interaction features built from the scaled numerical columns
    num = X[:, X.shape[1] - len(NUMERICAL_COLUMNS):]
    work_hours = num[:, NUMERICAL_COLUMNS.index("Work/Study Hours")]
    academic = num[:, NUMERICAL_COLUMNS.index("Academic Pressure")]
    financial = num[:, NUMERICAL_COLUMNS.index("Financial Stress")]
    satisfaction = num[:, NUMERICAL_COLUMNS.index("Study Satisfaction")]

    interactions = np.column_stack([
        academic * financial,
        work_hours * satisfaction,
        academic * satisfaction,
    ])
    return np.hstack((X, interactions))


class DepressionModel(nn.Module):
    # Feedforward net: Input -> 64 -> 32 -> 2 logits, with dropout

    def __init__(self, input_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 2)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        return self.fc3(x)


# Load model, encoder and scaler from disk only once
_cached_model = None
_cached_encoder = None
_cached_scaler = None


def _load_artifacts():
    global _cached_model, _cached_encoder, _cached_scaler

    if _cached_model is not None:
        return _cached_model, _cached_encoder, _cached_scaler

    logger.info("Loading model artifacts from %s", MODEL_DIR)

    _cached_encoder = joblib.load(MODEL_DIR / "encoder.joblib")
    _cached_scaler = joblib.load(MODEL_DIR / "scaler.joblib")

    _cached_model = DepressionModel(input_size=INPUT_SIZE)
    _cached_model.load_state_dict(
        torch.load(MODEL_DIR / "depression_model.pth", weights_only=True)
    )
    _cached_model.eval()

    return _cached_model, _cached_encoder, _cached_scaler


def risk_level(probability_pct):
    # Bucket a 0-100 probability into low / moderate / high
    if probability_pct >= 70:
        return "high"
    if probability_pct >= 40:
        return "moderate"
    return "low"


def predict(answers):
    # Run the full pipeline on one row of answers and return P(depression)
    model, encoder, scaler = _load_artifacts()

    df = pd.DataFrame.from_dict(answers)

    encoded_cat = encoder.transform(df[CATEGORICAL_COLUMNS])
    scaled_num = scaler.transform(df[NUMERICAL_COLUMNS])
    processed = add_interactions(np.hstack((encoded_cat, scaled_num)))

    tensor = torch.tensor(processed, dtype=torch.float32)
    with torch.no_grad():
        logits = model(tensor)
        output = F.softmax(logits, dim=1)

    probability = output[:, 1].item()
    logger.debug("Prediction: %.4f", probability)
    return probability


def train_and_export_model():
    # Train the model from scratch and save artifacts to MODEL_DIR
    logger.info("Starting model training")

    df = pd.read_csv(DATA_PATH)
    df = df[[*FEATURE_COLUMNS, TARGET_COLUMN]]
    df = df.dropna()

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    categorical_cols = X.select_dtypes(include=["object"]).columns
    numerical_cols = X.select_dtypes(exclude=["object"]).columns

    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoded_cat_data = encoder.fit_transform(X[categorical_cols])
    joblib.dump(encoder, MODEL_DIR / "encoder.joblib")

    scaler = StandardScaler()
    scaled_num_data = scaler.fit_transform(X[numerical_cols])
    joblib.dump(scaler, MODEL_DIR / "scaler.joblib")

    X_processed = add_interactions(np.hstack((encoded_cat_data, scaled_num_data)))

    X_train, X_test, y_train, y_test = train_test_split(
        X_processed,
        y,
        test_size=TRAIN_TEST_SPLIT,
        random_state=RANDOM_STATE,
    )

    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train.values, dtype=torch.long)
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test.values, dtype=torch.long)

    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    input_size = X_train.shape[1]
    model = DepressionModel(input_size)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(params=model.parameters(), lr=LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=3,
    )

    best_loss = float("inf")
    patience_counter = 0
    patience_limit = 5

    for epoch in range(NUM_EPOCHS):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            running_loss += loss.item()

        avg_loss = running_loss / len(train_loader)
        accuracy = 100 * correct / total
        scheduler.step(avg_loss)

        logger.info(
            "Epoch [%d/%d] Loss: %.4f Accuracy: %.2f%%",
            epoch + 1,
            NUM_EPOCHS,
            avg_loss,
            accuracy,
        )

        # Early stopping: save best weights, stop if no improvement for 5 epochs
        if avg_loss < best_loss:
            best_loss = avg_loss
            patience_counter = 0
            torch.save(model.state_dict(), MODEL_DIR / "depression_model.pth")
        else:
            patience_counter += 1
            if patience_counter >= patience_limit:
                logger.info("Early stopping at epoch %d", epoch + 1)
                break

    # Reload best weights and report test accuracy
    model.load_state_dict(torch.load(MODEL_DIR / "depression_model.pth", weights_only=True))
    model.eval()
    with torch.no_grad():
        outputs = model(X_test_tensor)
        _, predicted = torch.max(outputs.data, 1)
        test_correct = (predicted == y_test_tensor).sum().item()
        test_accuracy = 100 * test_correct / len(y_test_tensor)

    logger.info("Test accuracy: %.2f%%", test_accuracy)
    logger.info("Model saved to %s", MODEL_DIR / "depression_model.pth")
