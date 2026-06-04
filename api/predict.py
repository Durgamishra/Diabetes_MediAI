from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np
import os

app = FastAPI(
    title="AI Diabetes Prediction API",
    description="Machine Learning REST API for predicting diabetes risk.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://diabetes-medi-ai.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load model safely
MODEL_PATH = os.path.join(os.path.dirname(__file__),'..',"Diabetes_pred.sav")
diabetes_model = None

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as file:
        diabetes_model = pickle.load(file)
else:
    print(f"Warning: Model file '{MODEL_PATH}' not found. Prediction endpoint will fail.")

SCALER_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "scaler.sav"
)
scaler = None
if os.path.exists(SCALER_PATH):
    with open(SCALER_PATH, "rb") as file:
        scaler = pickle.load(file)
else:
    print(f"Warning: Scaler file '{SCALER_PATH}' not found. Predictions will proceed without scaling.")

class DiabetesInput(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    diabetes_pedigree_function: float
    age: int

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Premium AI Diabetes Prediction System Running",
        "model_loaded": diabetes_model is not None
    }
@app.post("/api/predict")
async def predict(data: DiabetesInput):
    if diabetes_model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        input_data = np.array([[ 
            data.pregnancies,
            data.glucose,
            data.blood_pressure,
            data.skin_thickness,
            data.insulin,
            data.bmi,
            data.diabetes_pedigree_function,
            data.age
        ]], dtype=float)

        print("RAW INPUT:", input_data)

        # Apply scaler if available
        if scaler is not None:
            input_data = scaler.transform(input_data)

        if hasattr(diabetes_model, "predict_proba"):
            proba = diabetes_model.predict_proba(input_data)[0][1]
            proba = float(proba)  # IMPORTANT FIX

            threshold = 0.4
            result = "Diabetic" if proba >= threshold else "Not Diabetic"
        else:
            pred = diabetes_model.predict(input_data)
            result = "Diabetic" if int(pred[0]) == 1 else "Not Diabetic"
            proba = None
        return {
            "outcome": result,
            "risk_score": proba
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
