"""Report eligibility checks for experimental survival predictions.

These checks validate software output only. They do not establish clinical
validity, clinical suitability, or permission to make treatment decisions.
"""

from math import isclose, isfinite


def check_individual_report_eligibility(prediction):
    """Return whether a prediction passes the individual-report output checks.

    The function does not generate a report, diagnose a patient, or assign
    a clinical risk category.
    """
    if not isinstance(prediction, dict):
        return {
            "eligible": False,
            "reason": "invalid_output",
            "message": "Prediction must be a JSON-style object.",
            "risk_category": None,
        }

    if prediction.get("status") != "success":
        return {
            "eligible": False,
            "reason": "prediction_not_successful",
            "message": "Prediction status is not success.",
            "risk_category": None,
        }

    if prediction.get("risk_assessed") is not True:
        return {
            "eligible": False,
            "reason": "risk_not_assessed",
            "message": "Risk assessment was not completed successfully.",
            "risk_category": None,
        }

    required = [
        "horizon_days",
        "survival_probability",
        "event_probability",
    ]
    missing = [key for key in required if key not in prediction]
    if missing:
        return {
            "eligible": False,
            "reason": "missing_output_fields",
            "message": "Missing required output fields: " + ", ".join(missing),
            "risk_category": None,
        }

    try:
        horizon = float(prediction["horizon_days"])
        survival = float(prediction["survival_probability"])
        event = float(prediction["event_probability"])
    except (TypeError, ValueError):
        return {
            "eligible": False,
            "reason": "invalid_output",
            "message": "Horizon and probabilities must be numeric.",
            "risk_category": None,
        }

    if not all(isfinite(x) for x in (horizon, survival, event)):
        reason = "Horizon and probabilities must be finite numbers."
        return {
            "eligible": False,
            "reason": "invalid_output",
            "message": reason,
            "risk_category": None,
        }

    if not 4 <= horizon <= 285:
        return {
            "eligible": False,
            "reason": "invalid_horizon",
            "message": "Prediction horizon must be between 4 and 285 days.",
            "risk_category": None,
        }

    if not all(0 <= x <= 1 for x in (survival, event)):
        return {
            "eligible": False,
            "reason": "invalid_probability",
            "message": "Probabilities must be between 0 and 1.",
            "risk_category": None,
        }

    if not isclose(survival + event, 1.0, rel_tol=0, abs_tol=1e-6):
        return {
            "eligible": False,
            "reason": "inconsistent_probabilities",
            "message": "Survival and event probabilities must sum to 1.",
            "risk_category": None,
        }

    return {
        "eligible": True,
        "reason": None,
        "message": (
            "Output passed software checks only. It remains an experimental "
            "model estimate and is not a diagnosis."
        ),
        "horizon_days": horizon,
        "risk_category": None,
        "clinical_validation_established": False,
    }


def check_statistical_analysis_eligibility(metadata):
    """Check whether aggregate analysis metadata meets documentation rules.

    Passing these checks does not establish scientific or clinical validity.
    """
    if not isinstance(metadata, dict):
        return {
            "eligible": False,
            "missing_requirements": ["metadata must be an object"],
            "risk_category": None,
        }

    required = [
        "cohort_description",
        "cohort_size",
        "inclusion_criteria",
        "missing_data_handling",
        "analysis_method",
        "uncertainty_reporting",
        "prediction_horizon_days",
        "limitations",
    ]

    missing = [
        key for key in required
        if key not in metadata
        or metadata[key] is None
        or (isinstance(metadata[key], str) and not metadata[key].strip())
    ]

    if "cohort_size" in metadata:
        size = metadata["cohort_size"]
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            missing.append("cohort_size must be a positive integer")

    if "prediction_horizon_days" in metadata:
        horizon = metadata["prediction_horizon_days"]
        if (
            isinstance(horizon, bool)
            or not isinstance(horizon, (int, float))
            or not 4 <= horizon <= 285
        ):
            missing.append(
                "prediction_horizon_days must be between 4 and 285"
            )

    return {
        "eligible": len(missing) == 0,
        "missing_requirements": missing,
        "risk_category": None,
        "clinical_validation_established": False,
        "message": (
            "Metadata checks only; passing does not establish scientific "
            "validity, external validation, or clinical utility."
        ),
    }
