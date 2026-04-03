from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.schemas import LoanInput
from app.model_loader import model, preprocessor

import pandas as pd
import numpy as np 

app = FastAPI(title="Smart Loan Predictor")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- STATIC FILES ----------------
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

# ---------------- FEATURE GROUPS ----------------
NUMERIC_COLS = [
    "person_age",
    "person_income",
    "person_emp_exp",
    "loan_amnt",
    "loan_int_rate",
    "loan_percent_income",
    "cb_person_cred_hist_length",
    "credit_score"
]

CATEGORICAL_COLS = [
    "person_gender",
    "person_education",
    "person_home_ownership",
    "loan_intent",
    "previous_loan_defaults_on_file"
]

# ---------------- ENCODING MAPPINGS ----------------
GENDER_MAP = {"male": 0, "female": 1}
EDUCATION_MAP = {"High School": 0, "Bachelor": 1, "Master": 2, "Doctor": 3}
HOME_OWNERSHIP_MAP = {"RENT": 0, "OWN": 1, "MORTGAGE": 2}
LOAN_INTENT_MAP = {"PERSONAL": 0, "EDUCATION": 1, "MEDICAL": 2, "VENTURE": 3, "HOME": 4}
DEFAULTS_MAP = {"NO": 0, "YES": 1}

# ---------------- PREDICTION ----------------
@app.post("/predict")
def predict(data: LoanInput):

    if model is None or preprocessor is None:
        raise HTTPException(status_code=500, detail="Models not loaded")

    # Encode categorical features
    gender_encoded = GENDER_MAP.get(data.person_gender.lower(), 0)
    education_encoded = EDUCATION_MAP.get(data.person_education, 0)
    home_ownership_encoded = HOME_OWNERSHIP_MAP.get(data.person_home_ownership, 0)
    loan_intent_encoded = LOAN_INTENT_MAP.get(data.loan_intent, 0)
    defaults_encoded = DEFAULTS_MAP.get(data.previous_loan_defaults_on_file, 0)

    # Create feature array with all 12 features (order matters!)
    X_features = np.array([
        gender_encoded,
        data.person_age,
        0,  # marital_status placeholder
        education_encoded,
        0,  # employment_type placeholder
        data.person_emp_exp,
        data.person_income,
        home_ownership_encoded,
        data.credit_score,
        defaults_encoded,
        data.loan_amnt,
        loan_intent_encoded
    ], dtype=np.float64).reshape(1, -1)

    # Scale features
    X_scaled = preprocessor.transform(X_features)

    # Make prediction
    prediction = model.predict(X_scaled)[0]
    probability = model.predict_proba(X_scaled)[0][1]

    return {
        "prediction": "Approved" if prediction == 1 else "Rejected",
        "probability": round(probability, 3)
    }
