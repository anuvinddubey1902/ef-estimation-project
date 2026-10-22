from pathlib import Path
import json
import pickle

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "random_survival_forest.pkl"
FEATURE_PATH = PROJECT_ROOT / "models" / "rsf_feature_names.json"


def load_model():
    """Load the trained Random Survival Forest and its feature list."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    if not FEATURE_PATH.exists():
        raise FileNotFoundError(f"Feature file not found: {FEATURE_PATH}")

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    with open(FEATURE_PATH, "r") as f:
        feature_names = json.load(f)

    return model, feature_names


def predict_risk(patient_data, horizon_days=100):
    """
    Predict survival and event probabilities at a specified time horizon.

    patient_data must contain all 11 model features as named fields.
    Returns probabilities, not a clinically validated diagnosis.
    """
    if not isinstance(patient_data, dict):
        raise TypeError("patient_data must be a dictionary.")

    if not isinstance(horizon_days, (int, float)) or isinstance(horizon_days, bool):
        raise TypeError("horizon_days must be a positive number.")

    if horizon_days <= 0:
        raise ValueError("horizon_days must be greater than zero.")

    model, feature_names = load_model()

    missing = [name for name in feature_names if name not in patient_data]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    values = {}
    for name in feature_names:
        value = patient_data[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Feature '{name}' must be numeric.")
        if not pd.notna(value):
            raise ValueError(f"Feature '{name}' must be finite.")
        if not __import__("math").isfinite(value):
            raise ValueError(f"Feature '{name}' must be finite.")
        values[name] = value

    X_input = pd.DataFrame([values], columns=feature_names)

    # Ensure the requested horizon is supported by the fitted model.
    lower_time = float(model.unique_times_[0])
    upper_time = float(model.unique_times_[-1])
    if horizon_days < lower_time or horizon_days > upper_time:
        raise ValueError(
            f"horizon_days must be between {lower_time:g} and {upper_time:g}."
        )

    survival_function = model.predict_survival_function(X_input)[0]
    survival_probability = float(survival_function(horizon_days))
    event_probability = 1.0 - survival_probability

    return {
        "horizon_days": horizon_days,
        "survival_probability": survival_probability,
        "event_probability": event_probability,
        "model": "Random Survival Forest",
    }
