from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
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
    allow_origins=["https://diabetes-medi-ai.vercel.app/"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
#  Resolve paths — api/index.py → project root
# ──────────────────────────────────────────────

import os

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "Diabetes_pred.sav")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.sav")

# Remove ROOT_DIR completely — not needed anymore
# ──────────────────────────────────────────────
#  Load model & scaler once at cold start
# ──────────────────────────────────────────────
diabetes_model = None
scaler = None
try:
    diabetes_model = joblib.load(MODEL_PATH)
    print(f"✅ Model loaded: {MODEL_PATH}")
except FileNotFoundError:
    print(f"⚠️  Model not found: {MODEL_PATH}")
except Exception as e:
    print(f"❌ Model load error: {e}")

try:
    scaler = joblib.load(SCALER_PATH)
    print(f"✅ Scaler loaded: {SCALER_PATH}")
except FileNotFoundError:
    print(f"⚠️  Scaler not found: {SCALER_PATH}")
except Exception as e:
    print(f"❌ Scaler load error: {e}")
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

    model_config = {
        "json_schema_extra": {
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
@app.get("/debug")
def debug():
    return {
        "cwd": os.getcwd(),
        "file": __file__,
        "model_path": MODEL_PATH,
        "model_exists": os.path.exists(MODEL_PATH),
        "scaler_path": SCALER_PATH,
        "scaler_exists": os.path.exists(SCALER_PATH),
    }

@app.get("/health")
def health():
    if diabetes_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy"}


@app.post("/api/index")
async def predict(data: DiabetesInput):
    if diabetes_model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Ensure 'Diabetes_pred.sav' is committed to the repo root.",
        )

    try:
        input_array = np.array([[
            data.pregnancies,
            data.glucose,
            data.blood_pressure,
            data.skin_thickness,
            data.insulin,
            data.bmi,
            data.diabetes_pedigree_function,
            data.age,
        ]], dtype=float)

        processed = scaler.transform(input_array) if scaler is not None else input_array

        if hasattr(diabetes_model, "predict_proba"):
            proba = float(diabetes_model.predict_proba(processed)[0][1])
            outcome = "Diabetic" if proba >= 0.4 else "Not Diabetic"
        else:
            prediction = int(diabetes_model.predict(processed)[0])
            outcome = "Diabetic" if prediction == 1 else "Not Diabetic"
            proba = None

        return {
            "outcome": outcome,
            "risk_score": round(proba, 4) if proba is not None else None,
            "threshold_used": 0.4,
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid input: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
