from risk.risk_input_gate import check_risk_inputs


COMPLETE_INPUT = {
    "age": 60,
    "anaemia": 0,
    "creatinine_phosphokinase": 250,
    "diabetes": 0,
    "ejection_fraction": 40,
    "high_blood_pressure": 0,
    "platelets": 250000,
    "serum_creatinine": 1.0,
    "serum_sodium": 137,
    "sex": 1,
    "smoking": 0,
}


def test_ef_only_input_is_unavailable():
    result = check_risk_inputs({
        "ejection_fraction": 40,
        "uncertainty": 0.08,
    })
    assert result["status"] == "unavailable"
    assert result["risk_assessed"] is False
    assert "age" in result["missing_fields"]


def test_incomplete_input_is_unavailable():
    result = check_risk_inputs({
        "age": 60,
        "ejection_fraction": 40,
    })
    assert result["status"] == "unavailable"
    assert len(result["missing_fields"]) == 9


def test_complete_input_is_ready_not_assessed():
    result = check_risk_inputs(COMPLETE_INPUT)
    assert result["status"] == "ready"
    assert result["risk_assessed"] is False


def test_invalid_binary_value_is_rejected():
    data = COMPLETE_INPUT.copy()
    data["smoking"] = 2
    result = check_risk_inputs(data)
    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_input"


def test_extra_field_is_rejected():
    data = COMPLETE_INPUT.copy()
    data["uncertainty"] = 0.08
    result = check_risk_inputs(data)
    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_input"


def test_non_finite_value_is_rejected():
    data = COMPLETE_INPUT.copy()
    data["serum_creatinine"] = float("nan")
    result = check_risk_inputs(data)
    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_input"
