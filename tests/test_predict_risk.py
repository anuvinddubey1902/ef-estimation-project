import pytest

from src.risk.predict_risk import predict_risk, load_model


@pytest.fixture
def sample_patient():
    _, feature_names = load_model()
    return {name: 1.0 for name in feature_names}


def test_missing_feature_is_rejected(sample_patient):
    sample_patient.pop("age")
    with pytest.raises(ValueError, match="Missing required features"):
        predict_risk(sample_patient)


def test_non_numeric_feature_is_rejected(sample_patient):
    sample_patient["age"] = "unknown"
    with pytest.raises(TypeError, match="must be numeric"):
        predict_risk(sample_patient)


def test_invalid_horizon_is_rejected(sample_patient):
    with pytest.raises(ValueError, match="greater than zero"):
        predict_risk(sample_patient, horizon_days=-10)


def test_wrong_input_type_is_rejected():
    with pytest.raises(TypeError, match="must be a dictionary"):
        predict_risk([1, 2, 3])


def test_prediction_probabilities_are_valid():
    from pathlib import Path
    import pandas as pd

    project = Path("/content/ef-estimation-project")
    csv_path = project / "data/uci_heart_failure/heart_failure_clinical_records_dataset.csv"
    df = pd.read_csv(csv_path)

    _, feature_names = load_model()
    sample_patient = df.iloc[0][feature_names].to_dict()

    result = predict_risk(sample_patient, horizon_days=100)

    assert 0 <= result["survival_probability"] <= 1
    assert 0 <= result["event_probability"] <= 1
    assert abs(
        result["survival_probability"]
        + result["event_probability"] - 1
    ) < 1e-9
