# Simple REST API for the depression model
# Run with: uvicorn src.api:app --reload

import logging
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import DIET_PATTERN, GENDER_PATTERN, MODEL_DIR, SLEEP_PATTERN
from src.database import get_predictions, init_db, save_prediction
from src.logging_config import setup_logging
from src.model_definition import FIELD_NAME_MAP, predict, risk_level

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Student Depression Prediction API")

# Open CORS so the API is callable from anywhere - it's a demo API, not a
# private one. Tighten this if the API ever serves a single frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


DISCLAIMER = (
    "This is a final-year class project, not a medical tool. "
    "Predictions come from a public Kaggle survey dataset and are not "
    "clinical advice. If you or someone you know is struggling, please "
    "speak to a qualified professional."
)


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/")
def root():
    # Landing endpoint - tells anyone hitting the bare URL what this is
    return {
        "name": "Student Depression Prediction API",
        "disclaimer": DISCLAIMER,
        "endpoints": ["/health", "/predict", "/predictions", "/docs"],
    }


class PredictionRequest(BaseModel):
    # The string fields are validated against the same option lists the GUI
    # uses (see src/config.py) - otherwise unknown categories would silently
    # become zero-vectors at encode time and skew the prediction.
    gender: str = Field(..., pattern=GENDER_PATTERN)
    age: float = Field(..., ge=18, le=34)
    study_hours: float = Field(..., ge=0, le=12)
    academic_pressure: float = Field(..., ge=1, le=5)
    financial_stress: float = Field(..., ge=1, le=5)
    study_satisfaction: float = Field(..., ge=1, le=5)
    sleep_duration: str = Field(..., pattern=SLEEP_PATTERN)
    dietary_habits: str = Field(..., pattern=DIET_PATTERN)
    suicidal_thoughts: str = Field(..., pattern=r"^(Yes|No)$")
    family_history: str = Field(..., pattern=r"^(Yes|No)$")


class PredictionResponse(BaseModel):
    probability: float
    risk_level: str
    request_id: str


@app.get("/health")
def health():
    # Quick health check - also tells you if the trained model file is there
    model_loaded = (MODEL_DIR / "depression_model.pth").exists()
    return {"status": "ok", "model_loaded": model_loaded}


@app.post("/predict", response_model=PredictionResponse)
def make_prediction(payload: PredictionRequest):
    # Turn the request into the dict shape predict() expects
    payload_dict = payload.model_dump()
    answers = {model_key: [payload_dict[api_key]] for model_key, api_key in FIELD_NAME_MAP.items()}

    try:
        probability = predict(answers) * 100
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed")

    level = risk_level(probability)
    rid = str(uuid.uuid4())

    save_prediction(
        request_id=rid,
        input_data=payload_dict,
        probability=round(probability, 2),
        risk_level=level,
    )

    logger.info("Prediction: %.2f%% (%s)", probability, level)
    return PredictionResponse(
        probability=round(probability, 2),
        risk_level=level,
        request_id=rid,
    )


@app.get("/predictions")
def list_predictions(limit: int = 50):
    # Don't let someone ask for thousands of rows
    limit = max(1, min(limit, 200))
    return get_predictions(limit=limit)
