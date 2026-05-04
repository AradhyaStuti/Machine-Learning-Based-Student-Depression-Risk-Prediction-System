# Entry point: launch the depression prediction GUI

import sys

from src.config import MODEL_DIR
from src.database import init_db
from src.GUI import initialize
from src.logging_config import setup_logging


def main():
    setup_logging()

    # Make sure the trained model is on disk before launching the GUI
    required = ["depression_model.pth", "encoder.joblib", "scaler.joblib"]
    missing = [f for f in required if not (MODEL_DIR / f).exists()]
    if missing:
        print("Could not find these model files in", MODEL_DIR)
        for f in missing:
            print(" -", f)
        print("Train the model first or copy the files into model_files/.")
        sys.exit(1)

    init_db()
    initialize()


if __name__ == "__main__":
    main()
