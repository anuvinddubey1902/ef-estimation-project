from pathlib import Path
import json
import math
import pickle

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "random_survival_forest.pkl"
FEATURE_PATH = PROJECT_ROOT / "models" / "rsf_feature_names.json"

EXPECTED_FEATURES = {
    "age",
    "anaemia",
    "creatinine_phosphokinase",
    "diabetes",
    "ejection_fraction",
    "high_blood_pressure",
    "platelets",
    "serum_creatinine",
    "serum_sodium",
    "sex",
    "smoking",
}

BINARY_FEATURES = {
    "anaemia",
    "diabetes",
    "high_blood_pressure",
    "sex",
    "smoking",
}

# Basic plausibility checks only; these are NOT clinical decision thresholds.
SANITY_RANGES = {
    "age": (0, 120),
    "creatinine_phosphokinase": (0, 1_000_000),
    "ejection_fraction": (0, 100),
    "platelets": (0, 10_000_000),
    "serum_creatinine": (0, 100),
    "serum_sodium": (0, 250),
}


class RiskToolError(Exception):
    """Base class for risk-tool errors."""

    code = "risk_tool_error"

    def to_dict(self):
        return {
            "status": "error",
            "error": {
                "code": self.code,
                "message": str(self),
            },
            "risk_assessed": False,
        }


class InvalidInputError(RiskToolError, ValueError, TypeError):
    code = "invalid_input"


class MissingDataError(RiskToolError, ValueError):
    code = "missing_required_data"


class ModelLoadError(RiskToolError):
    code = "model_load_failed"


class PredictionError(RiskToolError):
    code = "prediction_failed"


def load_model():
    """Load the trained RSF and verify its feature list."""
    if not MODEL_PATH.exists():
        raise ModelLoadError(f"Model file not found: {MODEL_PATH}")

    if not FEATURE_PATH.exists():
        raise ModelLoadError(f"Feature file not found: {FEATURE_PATH}")

    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)

        with open(FEATURE_PATH, "r") as f:
            feature_names = json.load(f)

    except Exception as exc:
        raise ModelLoadError(
            f"Could not load model artifacts: {exc}"
        ) from exc

    if (
        not isinstance(feature_names, list)
        or set(feature_names) != EXPECTED_FEATURES
        or len(feature_names) != len(EXPECTED_FEATURES)
    ):
        raise ModelLoadError(
            "Model feature list does not match the expected 11 features."
        )

    return model, feature_names


def validate_patient_data(patient_data, feature_names):
    """Validate required clinical inputs before model inference."""
    if not isinstance(patient_data, dict):
        raise InvalidInputError("patient_data must be a dictionary.")

    missing = [
        name for name in feature_names
        if name not in patient_data
        or patient_data[name] is None
    ]
    if missing:
        raise MissingDataError(
            f"Missing required features: {missing}"
        )

    extra = sorted(set(patient_data) - set(feature_names))
    if extra:
        raise InvalidInputError(
            f"Unexpected input fields: {extra}"
        )

    values = {}

    for name in feature_names:
        value = patient_data[name]

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidInputError(
                f"Feature '{name}' must be numeric."
            )

        if not math.isfinite(value):
            raise InvalidInputError(
                f"Feature '{name}' must be finite."
            )

        if name in BINARY_FEATURES and value not in (0, 1):
            raise InvalidInputError(
                f"Feature '{name}' must be 0 or 1."
            )

        if name in SANITY_RANGES:
            lower, upper = SANITY_RANGES[name]
            if not lower <= value <= upper:
                raise InvalidInputError(
                    f"Feature '{name}' is outside the configured "
                    f"software sanity range [{lower}, {upper}]."
                )

    # Preserve the model's expected column order.
    for name in feature_names:
        values[name] = patient_data[name]

    return pd.DataFrame([values], columns=feature_names)


def predict_risk(patient_data, horizon_days=100):
    """
    Estimate survival and event probabilities at a specified horizon.

    Returns a prediction dictionary on success.
    Raises RiskToolError subclasses for anticipated tool errors.

    This function does not provide a diagnosis or validated clinical
    risk category. The caller should convert RiskToolError exceptions
    into their structured to_dict() responses.
    """
    if (
        isinstance(horizon_days, bool)
        or not isinstance(horizon_days, (int, float))
        or not math.isfinite(horizon_days)
        or horizon_days <= 0
    ):
        raise InvalidInputError(
            "horizon_days must be greater than zero and finite."
        )

    model, feature_names = load_model()
    X_input = validate_patient_data(patient_data, feature_names)

    try:
        lower_time = float(model.unique_times_[0])
        upper_time = float(model.unique_times_[-1])

        if not lower_time <= horizon_days <= upper_time:
            raise InvalidInputError(
                f"horizon_days must be between "
                f"{lower_time:g} and {upper_time:g}."
            )

        survival_function = model.predict_survival_function(X_input)[0]
        survival_probability = float(survival_function(horizon_days))

        if (
            not math.isfinite(survival_probability)
            or not 0.0 <= survival_probability <= 1.0
        ):
            raise PredictionError(
                "Model returned an invalid survival probability."
            )

        event_probability = 1.0 - survival_probability

        return {
            "status": "success",
            "risk_assessed": True,
            "horizon_days": horizon_days,
            "survival_probability": survival_probability,
            "event_probability": event_probability,
            "model": "Random Survival Forest",
        }

    except RiskToolError:
        raise
    except Exception as exc:
        raise PredictionError(
            f"Model inference failed: {exc}"
        ) from exc
