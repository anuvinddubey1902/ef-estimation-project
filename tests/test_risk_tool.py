import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from risk.risk_tool import risk_assessment_tool


VALID_PATIENT = {
    "age": 60,
    "anaemia": 0,
    "creatinine_phosphokinase": 250,
    "diabetes": 0,
    "ejection_fraction": 40,
    "high_blood_pressure": 1,
    "platelets": 250000,
    "serum_creatinine": 1.2,
    "serum_sodium": 137,
    "sex": 1,
    "smoking": 0,
}


def test_valid_request_returns_probabilities():
    result = risk_assessment_tool(VALID_PATIENT, horizon_days=100)

    assert result["status"] == "success"
    assert result["risk_assessed"] is True
    assert 0 <= result["survival_probability"] <= 1
    assert 0 <= result["event_probability"] <= 1
    assert abs(
        result["survival_probability"]
        + result["event_probability"] - 1
    ) < 1e-6


def test_missing_data_returns_structured_error():
    result = risk_assessment_tool({"age": 60}, horizon_days=100)

    assert result["status"] == "error"
    assert result["risk_assessed"] is False
    assert result["error"]["code"] == "missing_required_data"


def test_invalid_horizon_returns_structured_error():
    result = risk_assessment_tool(VALID_PATIENT, horizon_days=-10)

    assert result["status"] == "error"
    assert result["risk_assessed"] is False


def test_unexpected_field_is_rejected():
    patient = {**VALID_PATIENT, "unknown_feature": 123}
    result = risk_assessment_tool(patient, horizon_days=100)

    assert result["status"] == "error"
    assert result["risk_assessed"] is False
