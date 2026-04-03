"""
Script to create mock ML models for testing the Smart Loan Predictor API
Run this script to generate the required model files
"""
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path

def create_mock_models():
    """Create and save mock ML models"""
    
    # Create sample training data (12 features now with all the categorical fields)
    np.random.seed(42)
    n_samples = 1000
    
    # Generate sample features
    X_train = np.random.rand(n_samples, 12)
    
    # Scale features to realistic ranges
    X_train[:, 0] = X_train[:, 0]  # gender (0-1)
    X_train[:, 1] = X_train[:, 1] * 50 + 18  # age (18-68)
    X_train[:, 2] = X_train[:, 2] * 3  # marital_status (0-3)
    X_train[:, 3] = X_train[:, 3] * 3  # education (0-3)
    X_train[:, 4] = X_train[:, 4] * 3  # employment_type (0-3)
    X_train[:, 5] = X_train[:, 5] * 40  # employment_years (0-40)
    X_train[:, 6] = X_train[:, 6] * 150000 + 20000  # income (20k-170k)
    X_train[:, 7] = X_train[:, 7] * 2  # home_ownership (0-2)
    X_train[:, 8] = X_train[:, 8] * 350 + 500  # credit_score (500-850)
    X_train[:, 9] = X_train[:, 9] * 5  # existing_loans (0-5)
    X_train[:, 10] = X_train[:, 10] * 100000 + 5000  # loan_amount (5k-105k)
    X_train[:, 11] = X_train[:, 11] * 5  # loan_purpose (0-5)
    
    # Generate labels based on simple rules for realistic predictions
    y_train = np.zeros(n_samples)
    for i in range(n_samples):
        credit_score = X_train[i, 8]
        income = X_train[i, 6]
        loan_amount = X_train[i, 10]
        existing_loans = X_train[i, 9]
        
        # Simple approval logic
        if credit_score > 650 and income > loan_amount * 0.3 and existing_loans < 3:
            y_train[i] = 1  # Approved
        elif credit_score > 700 and income > loan_amount * 0.2:
            y_train[i] = 1  # Approved
        else:
            y_train[i] = 0  # Rejected
    
    # Create and train preprocessor (StandardScaler)
    print("Creating preprocessor...")
    preprocessor = StandardScaler()
    X_train_scaled = preprocessor.fit_transform(X_train)
    
    # Create and train Random Forest model
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # Calculate accuracy
    accuracy = model.score(X_train_scaled, y_train)
    print(f"Model training accuracy: {accuracy:.2%}")
    
    # Create models directory if it doesn't exist
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Save the model
    model_path = models_dir / "random_forest_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✓ Model saved to: {model_path}")
    
    # Save the preprocessor
    preprocessor_path = models_dir / "preprocessor.pkl"
    with open(preprocessor_path, 'wb') as f:
        pickle.dump(preprocessor, f)
    print(f"✓ Preprocessor saved to: {preprocessor_path}")
    
    print("\n✓ Mock models created successfully!")
    print("You can now run the API server with: python -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    create_mock_models()
