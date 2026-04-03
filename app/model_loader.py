import joblib
import os

MODEL_PATH = os.path.join("models", "random_forest_model.pkl")
PREPROCESSOR_PATH = os.path.join("models", "preprocessor.pkl")

model = None
preprocessor = None

try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    print("✅ Models loaded successfully")
except Exception as e:
    print("❌ Error loading models:", e)
