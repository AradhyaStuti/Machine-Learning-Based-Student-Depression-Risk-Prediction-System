# Project paths, dataset columns, and training settings

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "model_files"
DATA_DIR = PROJECT_ROOT / "data"
DATA_PATH = DATA_DIR / "Student Depression Dataset.csv"
DB_PATH = PROJECT_ROOT / "predictions.db"

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
