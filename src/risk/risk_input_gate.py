"""Preflight checks for deciding whether risk assessment can be attempted."""

from risk.predict_risk import EXPECTED_FEATURES, SANITY_RANGES, BINARY_FEATURES


def check_risk_inputs(patient_data):
    """Return readiness status without running model inference."""
    if not isinstance(patient_data, dict):
        return {
            "status": "error",
            "risk_assessed": False,
            "error": {
                "code": "invalid_input",
                "message": "patient_data must be an object.",
            },
        }

    missing = sorted(
        name for name in EXPECTED_FEATURES
        if name not in patient_data or patient_data[name] is None
    )
    if missing:
        return {
            "status": "unavailable",
            "risk_assessed": False,
            "reason": "missing_required_data",
            "missing_fields": missing,
            "message": "Risk assessment is unavailable until all required clinical inputs are supplied.",
        }

    extra = sorted(set(patient_data) - EXPECTED_FEATURES)
    if extra:
        return {
            "status": "error",
            "risk_assessed": False,
            "error": {
                "code": "invalid_input",
                "message": f"Unexpected input fields: {extra}",
            },
        }

    import math
    for name, value in patient_data.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            return {
                "status": "error",
                "risk_assessed": False,
                "error": {
                    "code": "invalid_input",
                    "message": f"Field {name!r} must be a finite number.",
                },
            }
        if name in BINARY_FEATURES and value not in (0, 1):
            return {
                "status": "error",
                "risk_assessed": False,
                "error": {
                    "code": "invalid_input",
                    "message": f"Field {name!r} must be 0 or 1.",
                },
            }
        if name in SANITY_RANGES:
            low, high = SANITY_RANGES[name]
            if not low <= value <= high:
                return {
                    "status": "error",
                    "risk_assessed": False,
                    "error": {
                        "code": "invalid_input",
                        "message": f"Field {name!r} is outside its configured software sanity range [{low}, {high}].",
                    },
                }

    return {"status": "ready", "risk_assessed": False, "missing_fields": []}
