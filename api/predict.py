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
MODEL_PATH = "Diabetes_pred.sav"
diabetes_model = None

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as file:
        diabetes_model = pickle.load(file)
else:
    print(f"Warning: Model file '{MODEL_PATH}' not found. Prediction endpoint will fail.")

# Uncomment if a scaler is required:
# SCALER_PATH = "scaler.sav"
# if os.path.exists(SCALER_PATH):
#     scaler = pickle.load(open(SCALER_PATH, "rb"))

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

@app.post("/predict")
async def predict(data: DiabetesInput):
    if diabetes_model is None:
        raise HTTPException(status_code=500, detail="Machine Learning model is not loaded on the server.")

    try:
        # Format input data
        input_data = np.array([[
            data.pregnancies,
            data.glucose,
            data.blood_pressure,
            data.skin_thickness,
            data.insulin,
            data.bmi,
            data.diabetes_pedigree_function,
            data.age
        ]])

        # If scaler used:
        # input_data = scaler.transform(input_data)

        # Generate Prediction
        prediction = diabetes_model.predict(input_data)

        # Output resolution
        result = "Diabetic" if prediction[0] == 1 else "Not Diabetic"

        return {"outcome": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction Error: {str(e)}")
