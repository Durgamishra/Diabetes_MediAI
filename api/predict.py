from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np
import os

# ──────────────────────────────────────────────
#  App setup
# ──────────────────────────────────────────────
app = FastAPI(
    title="AI Diabetes Prediction API",
    description="Machine Learning REST API for predicting diabetes risk.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://diabetes-medi-ai.vercel.app",
        "http://localhost:3000",   # local React dev
        "http://localhost:5173",   # local Vite dev
        "http://127.0.0.1:5500",  # local Live Server dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
#  Resolve paths robustly (works in Vercel serverless)
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)  # one level up from api/

MODEL_PATH  = os.path.join(ROOT_DIR, "Diabetes_pred.sav")
SCALER_PATH = os.path.join(ROOT_DIR, "scaler.sav")

# ──────────────────────────────────────────────
#  Load model & scaler at startup (not per-request)
# ──────────────────────────────────────────────
diabetes_model = None
scaler = None

try:
    with open(MODEL_PATH, "rb") as f:
        diabetes_model = pickle.load(f)
    print(f"✅ Model loaded from: {MODEL_PATH}")
except FileNotFoundError:
    print(f"⚠️  Model file not found at: {MODEL_PATH}")
except Exception as e:
    print(f"❌ Failed to load model: {e}")

try:
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    print(f"✅ Scaler loaded from: {SCALER_PATH}")
except FileNotFoundError:
    print(f"⚠️  Scaler file not found at: {SCALER_PATH}")
except Exception as e:
    print(f"❌ Failed to load scaler: {e}")

# ──────────────────────────────────────────────
#  Request schema
# ──────────────────────────────────────────────
class DiabetesInput(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    diabetes_pedigree_function: float
    age: int

    class Config:
        json_schema_extra = {
            "example": {
                "pregnancies": 2,
                "glucose": 120.0,
                "blood_pressure": 70.0,
                "skin_thickness": 20.0,
                "insulin": 80.0,
                "bmi": 28.5,
                "diabetes_pedigree_function": 0.45,
                "age": 33,
            }
        }

# ──────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────
@app.get("/")
def home():
    return {
        "status": "online",
        "message": "AI Diabetes Prediction API is running",
        "model_loaded": diabetes_model is not None,
        "scaler_loaded": scaler is not None,
    }


@app.get("/health")
def health():
    """Quick health-check endpoint for uptime monitors."""
    if diabetes_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded — service unavailable")
    return {"status": "healthy"}


@app.post("/api/predict")
async def predict(data: DiabetesInput):
    if diabetes_model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Check that 'Diabetes_pred.sav' exists in the project root.",
        )

    try:
        input_array = np.array(
            [[
                data.pregnancies,
                data.glucose,
                data.blood_pressure,
                data.skin_thickness,
                data.insulin,
                data.bmi,
                data.diabetes_pedigree_function,
                data.age,
            ]],
            dtype=float,
        )

        # Scale only if scaler was loaded
        processed = scaler.transform(input_array) if scaler is not None else input_array

        if hasattr(diabetes_model, "predict_proba"):
            proba = float(diabetes_model.predict_proba(processed)[0][1])
            threshold = 0.4
            outcome = "Diabetic" if proba >= threshold else "Not Diabetic"
        else:
            prediction = int(diabetes_model.predict(processed)[0])
            outcome = "Diabetic" if prediction == 1 else "Not Diabetic"
            proba = None

        return {
            "outcome": outcome,
            "risk_score": round(proba, 4) if proba is not None else None,
            "threshold_used": 0.4 if proba is not None else None,
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid input values: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
