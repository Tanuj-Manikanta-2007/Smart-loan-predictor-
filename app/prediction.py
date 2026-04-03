import numpy as np
from app.schemas import LoanPredictionRequest, LoanPredictionResponse
from app.model_loader import check_models_available

def predict_loan(request: LoanPredictionRequest, models: dict) -> LoanPredictionResponse:
    """Predict loan approval using the trained model"""
    # Make sure models are loaded
    if not check_models_available(models):
        raise ValueError("ML models are not loaded. Please ensure model files are available.")
    
    # Convert categorical fields to numeric
    gender_map = {"male": 1, "female": 0}
    marital_map = {"single": 0, "married": 1, "divorced": 2, "widowed": 3}
    education_map = {"high_school": 0, "bachelor": 1, "master": 2, "phd": 3}
    employment_map = {"unemployed": 0, "self_employed": 1, "salaried": 2, "business": 3}
    ownership_map = {"rent": 0, "mortgage": 1, "own": 2}
    purpose_map = {"personal": 0, "education": 1, "car": 2, "home": 3, "business": 4, "debt_consolidation": 5}
    
    # Extract features from request
    features = np.array([[
        gender_map.get(request.gender, 0),
        request.age,
        marital_map.get(request.marital_status, 0),
        education_map.get(request.education, 0),
        employment_map.get(request.employment_type, 0),
        request.employment_years,
        request.income,
        ownership_map.get(request.home_ownership, 0),
        request.credit_score,
        request.existing_loans,
        request.loan_amount,
        purpose_map.get(request.loan_purpose, 0)
    ]])
    
    try:
        preprocessor = models['preprocessor']
        features_processed = preprocessor.transform(features)
    except Exception as e:
        raise ValueError(f"Error preprocessing features: {e}")
    
    try:
        model = models['model']
        prediction = model.predict(features_processed)[0]
        probability = model.predict_proba(features_processed)[0][1]
    except Exception as e:
        raise ValueError(f"Error making prediction: {e}")
    
    risk_level = determine_risk_level(
        probability,
        request.credit_score,
        request.existing_loans,
        request.loan_amount,
        request.income
    )
    recommendation = generate_recommendation(prediction, probability, risk_level)
    
    return LoanPredictionResponse(
        prediction="Approved" if prediction == 1 else "Rejected",
        probability=float(probability),
        risk_level=risk_level,
        recommendation=recommendation
    )

def determine_risk_level(probability: float, credit_score: int, 
                        existing_loans: int, loan_amount: float, income: float) -> str:
    """Figure out how risky this loan looks"""
    # Calculate debt-to-income ratio
    monthly_income = income / 12
    debt_to_income = (loan_amount / 12) / monthly_income if monthly_income > 0 else 1
    risk_score = 0
    
    if credit_score < 600:
        risk_score += 3
    elif credit_score < 700:
        risk_score += 2
    elif credit_score < 750:
        risk_score += 1
    
    if probability < 0.3:
        risk_score += 3
    elif probability < 0.6:
        risk_score += 2
    elif probability < 0.8:
        risk_score += 1
    
    if existing_loans > 3:
        risk_score += 2
    elif existing_loans > 1:
        risk_score += 1
    
    if debt_to_income > 0.5:
        risk_score += 2
    elif debt_to_income > 0.3:
        risk_score += 1
    
    if risk_score <= 2:
        return "Low"
    elif risk_score <= 5:
        return "Medium"
    else:
        return "High"

def generate_recommendation(prediction: str, probability: float, risk_level: str) -> str:
    """Give friendly advice based on the prediction"""
    if prediction == "Approved":
        if risk_level == "Low":
            return "Applicant is eligible for the requested loan amount with favorable terms."
        elif risk_level == "Medium":
            return "Applicant is eligible but may be offered loan with standard terms and conditions."
        else:
            return "Applicant is eligible but may require additional documentation or higher interest rate."
    else:
        if probability > 0.4:
            return "Applicant was rejected. Consider reapplying after improving credit score or reducing existing debt."
        else:
            return "Applicant does not meet current lending criteria. Please reapply when financial situation improves."
