# Simple REST API for the depression model
# Run with: uvicorn src.api:app --reload

import logging
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import MODEL_DIR
from src.database import get_predictions, init_db, save_prediction
from src.logging_config import setup_logging
from src.model_definition import FIELD_NAME_MAP, predict, risk_level

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Student Depression Prediction API")


@app.on_event("startup")
def _startup():
    init_db()


class PredictionRequest(BaseModel):
    gender: str
    age: float = Field(..., ge=18, le=34)
    study_hours: float = Field(..., ge=0, le=12)
    academic_pressure: float = Field(..., ge=1, le=5)
    financial_stress: float = Field(..., ge=1, le=5)
    study_satisfaction: float = Field(..., ge=1, le=5)
    sleep_duration: str
    dietary_habits: str
    suicidal_thoughts: str = Field(..., pattern=r"^(Yes|No)$")
    family_history: str = Field(..., pattern=r"^(Yes|No)$")


class PredictionResponse(BaseModel):
    probability: float
    risk_level: str
    request_id: str


@app.get("/health")
def health():
    # Report whether the trained model is on disk
    model_loaded = (MODEL_DIR / "depression_model.pth").exists()
    return {"status": "ok", "model_loaded": model_loaded}


@app.post("/predict", response_model=PredictionResponse)
def make_prediction(payload: PredictionRequest):
    # Build the dict shape the model expects from the API payload
    payload_dict = payload.model_dump()
    answers = {model_key: [payload_dict[api_key]] for model_key, api_key in FIELD_NAME_MAP.items()}

    try:
        probability = predict(answers) * 100
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc

    level = risk_level(probability)
    rid = str(uuid.uuid4())

    save_prediction(
        request_id=rid,
        input_data=payload.model_dump(),
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
    # Cap the limit so a huge ?limit=999999 doesn't dump the whole table
    limit = max(1, min(limit, 200))
    return get_predictions(limit=limit)
