from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import joblib
import os
import traceback

# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title="AI Diabetes Prediction API",
    description="Machine Learning REST API for Diabetes Prediction",
    version="1.0.0"
)

# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://diabetes-medi-ai.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "Diabetes_pred.sav")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.sav")

# --------------------------------------------------
# Load Model & Scaler
# --------------------------------------------------

diabetes_model = None
scaler = None
model_error = None
scaler_error = None

try:
    print(f"Loading model from: {MODEL_PATH}")

    if os.path.exists(MODEL_PATH):
        diabetes_model = joblib.load(MODEL_PATH)
        print("✅ Model loaded successfully")
    else:
        model_error = f"File not found: {MODEL_PATH}"
        print(model_error)

except Exception as e:
    model_error = str(e)
    print("❌ Model loading failed:")
    print(traceback.format_exc())

try:
    print(f"Loading scaler from: {SCALER_PATH}")

    if os.path.exists(SCALER_PATH):
        scaler = joblib.load(SCALER_PATH)
        print("✅ Scaler loaded successfully")
    else:
        scaler_error = f"File not found: {SCALER_PATH}"
        print(scaler_error)

except Exception as e:
    scaler_error = str(e)
    print("❌ Scaler loading failed:")
    print(traceback.format_exc())

# --------------------------------------------------
# Request Model
# --------------------------------------------------

class DiabetesInput(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    diabetes_pedigree_function: float
    age: int

# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "online",
        "model_loaded": diabetes_model is not None,
        "scaler_loaded": scaler is not None
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": diabetes_model is not None,
        "scaler_loaded": scaler is not None
    }


@app.get("/debug")
def debug():
    return {
        "current_directory": os.getcwd(),
        "base_dir": BASE_DIR,
        "model_path": MODEL_PATH,
        "model_exists": os.path.exists(MODEL_PATH),
        "scaler_path": SCALER_PATH,
        "scaler_exists": os.path.exists(SCALER_PATH),
        "model_loaded": diabetes_model is not None,
        "scaler_loaded": scaler is not None,
        "model_error": model_error,
        "scaler_error": scaler_error
    }


@app.post("/api/predict")
async def predict(data: DiabetesInput):

    if diabetes_model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded. Error: {model_error}"
        )

    try:

        features = np.array([[
            data.pregnancies,
            data.glucose,
            data.blood_pressure,
            data.skin_thickness,
            data.insulin,
            data.bmi,
            data.diabetes_pedigree_function,
            data.age
        ]])

        if scaler is not None:
            features = scaler.transform(features)

        prediction = int(diabetes_model.predict(features)[0])

        probability = None

        if hasattr(diabetes_model, "predict_proba"):
            probability = float(
                diabetes_model.predict_proba(features)[0][1]
            )

        return {
            "prediction": prediction,
            "outcome": "Diabetic" if prediction == 1 else "Not Diabetic",
            "risk_score": round(probability, 4) if probability is not None else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
