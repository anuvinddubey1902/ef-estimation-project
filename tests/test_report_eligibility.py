from risk.report_eligibility import (
    check_individual_report_eligibility,
    check_statistical_analysis_eligibility,
)


def valid_prediction():
    return {
        "status": "success",
        "risk_assessed": True,
        "horizon_days": 100,
        "survival_probability": 0.96,
        "event_probability": 0.04,
        "model": "Random Survival Forest",
    }


def valid_metadata():
    return {
        "cohort_description": "UCI Heart Failure Clinical Records",
        "cohort_size": 299,
        "inclusion_criteria": "Records included in the analysis",
        "missing_data_handling": "Missingness checked and documented",
        "analysis_method": "Five-fold cross-validation",
        "uncertainty_reporting": "Mean and standard deviation reported",
        "prediction_horizon_days": 100,
        "limitations": "No external clinical validation",
    }


def test_valid_individual_prediction_is_eligible():
    assert check_individual_report_eligibility(
        valid_prediction()
    )["eligible"] is True


def test_failed_prediction_is_rejected():
    prediction = valid_prediction()
    prediction["status"] = "error"
    prediction["risk_assessed"] = False

    assert check_individual_report_eligibility(
        prediction
    )["eligible"] is False


def test_invalid_probability_is_rejected():
    prediction = valid_prediction()
    prediction["event_probability"] = 1.2

    result = check_individual_report_eligibility(prediction)
    assert result["eligible"] is False
    assert result["reason"] == "invalid_probability"


def test_inconsistent_probabilities_are_rejected():
    prediction = valid_prediction()
    prediction["survival_probability"] = 0.8

    result = check_individual_report_eligibility(prediction)
    assert result["eligible"] is False
    assert result["reason"] == "inconsistent_probabilities"


def test_individual_risk_category_remains_null():
    assert check_individual_report_eligibility(
        valid_prediction()
    )["risk_category"] is None


def test_complete_statistical_metadata_is_eligible():
    assert check_statistical_analysis_eligibility(
        valid_metadata()
    )["eligible"] is True


def test_incomplete_statistical_metadata_is_rejected():
    metadata = valid_metadata()
    metadata.pop("limitations")

    result = check_statistical_analysis_eligibility(metadata)
    assert result["eligible"] is False
    assert "limitations" in result["missing_requirements"]


def test_invalid_cohort_size_is_rejected():
    metadata = valid_metadata()
    metadata["cohort_size"] = 0

    assert check_statistical_analysis_eligibility(
        metadata
    )["eligible"] is False


def test_statistical_risk_category_remains_null():
    assert check_statistical_analysis_eligibility(
        valid_metadata()
    )["risk_category"] is None
