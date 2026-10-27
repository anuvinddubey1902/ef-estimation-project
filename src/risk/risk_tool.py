"""Agent-facing wrapper for the experimental survival risk model."""

from risk.predict_risk import predict_risk, RiskToolError


TOOL_NAME = "risk_assessment_tool"

TOOL_DESCRIPTION = (
    "Estimate survival and event probabilities at a specified time horizon "
    "from 11 required clinical inputs. This model is not clinically validated. "
    "Do not infer missing clinical inputs or assign unsupported risk categories."
)


def risk_assessment_tool(patient_data, horizon_days=100):
    """Return a structured result suitable for an agent to consume."""
    try:
        prediction = predict_risk(
            patient_data=patient_data,
            horizon_days=horizon_days,
        )
        return prediction

    except RiskToolError as exc:
        return exc.to_dict()

    except Exception:
        # Do not expose internal exception details to the calling agent.
        return {
            "status": "error",
            "risk_assessed": False,
            "error": {
                "code": "internal_error",
                "message": "The risk assessment could not be completed.",
            },
        }
