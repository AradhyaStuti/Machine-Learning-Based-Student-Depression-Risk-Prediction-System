# Project paths, dataset columns, and training settings

import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "model_files"
DATA_DIR = PROJECT_ROOT / "data"
DATA_PATH = DATA_DIR / "Student Depression Dataset.csv"

# DB path can be overridden via APP_DB_PATH (used by docker-compose so the
# sqlite file can live inside a named volume).
DB_PATH = Path(os.environ.get("APP_DB_PATH", str(PROJECT_ROOT / "predictions.db")))

# Model
INPUT_SIZE = 23

# Training
TRAIN_TEST_SPLIT = 0.2
RANDOM_STATE = 17
BATCH_SIZE = 32
LEARNING_RATE = 0.001
NUM_EPOCHS = 50

# Dataset columns
FEATURE_COLUMNS = [
    "Gender",
    "Age",
    "Work/Study Hours",
    "Academic Pressure",
    "Financial Stress",
    "Study Satisfaction",
    "Sleep Duration",
    "Dietary Habits",
    "Have you ever had suicidal thoughts ?",
    "Family History of Mental Illness",
]
TARGET_COLUMN = "Depression"

CATEGORICAL_COLUMNS = [
    "Gender",
    "Sleep Duration",
    "Dietary Habits",
    "Have you ever had suicidal thoughts ?",
    "Family History of Mental Illness",
]
NUMERICAL_COLUMNS = [
    "Age",
    "Work/Study Hours",
    "Academic Pressure",
    "Financial Stress",
    "Study Satisfaction",
]

# Valid options for the categorical fields. These have to match the values
# the encoder was trained on, so the GUI and the API both pull from here.
GENDER_OPTIONS = ["Male", "Female"]
SLEEP_OPTIONS = ["More than 8 hours", "7-8 hours", "5-6 hours", "Less than 5 hours", "Others"]
DIET_OPTIONS = ["Healthy", "Moderate", "Unhealthy", "Others"]


def options_pattern(options):
    # Build a "^(a|b|c)$" regex from a list of allowed values
    return r"^(" + "|".join(options) + r")$"


GENDER_PATTERN = options_pattern(GENDER_OPTIONS)
SLEEP_PATTERN = options_pattern(SLEEP_OPTIONS)
DIET_PATTERN = options_pattern(DIET_OPTIONS)
