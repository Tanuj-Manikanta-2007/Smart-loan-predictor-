from pydantic import BaseModel

class LoanInput(BaseModel):
    person_age: int
    person_gender: str
    person_education: str
    person_income: float
    person_emp_exp: int
    person_home_ownership: str
    loan_amnt: float
    loan_intent: str
    loan_int_rate: float
    loan_percent_income: float
    cb_person_cred_hist_length: int
    credit_score: int
    previous_loan_defaults_on_file: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "person_age": 28,
                "person_gender": "male",
                "person_education": "Bachelor",
                "person_income": 550000,
                "person_emp_exp": 4,
                "person_home_ownership": "RENT",
                "loan_amnt": 120000,
                "loan_intent": "EDUCATION",
                "loan_int_rate": 11.5,
                "loan_percent_income": 0.22,
                "cb_person_cred_hist_length": 6,
                "credit_score": 720,
                "previous_loan_defaults_on_file": "NO"
            }
        }
    }
