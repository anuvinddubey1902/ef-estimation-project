"""MCP server exposing the experimental survival risk tool."""

import json
from pydantic import BaseModel, ConfigDict, Field
from mcp.server import MCPServer

from risk.risk_tool import risk_assessment_tool as run_risk_assessment


class PatientData(BaseModel):
    """Clinical inputs required by the survival model."""

    model_config = ConfigDict(extra="forbid")

    age: float = Field(description="Age in years")
    anaemia: int = Field(description="Anaemia indicator, source coding 0 or 1")
    creatinine_phosphokinase: float = Field(
        description="Creatinine phosphokinase, mcg/L"
    )
    diabetes: int = Field(description="Diabetes indicator, source coding 0 or 1")
    ejection_fraction: float = Field(description="Ejection fraction, percent")
    high_blood_pressure: int = Field(
        description="High blood pressure indicator, source coding 0 or 1"
    )
    platelets: float = Field(description="Platelet count in source-dataset units")
    serum_creatinine: float = Field(description="Serum creatinine, mg/dL")
    serum_sodium: float = Field(description="Serum sodium, mEq/L")
    sex: int = Field(description="Sex indicator using source-dataset coding 0 or 1")
    smoking: int = Field(description="Smoking indicator, source coding 0 or 1")


server = MCPServer(
    name="experimental-heart-failure-risk",
    version="0.1.0",
    instructions=(
        "Experimental survival probability estimation tool. "
        "Require all 11 clinical inputs. Never infer missing values. "
        "Not clinically validated; not a diagnostic tool."
    ),
)


@server.tool(
    name="risk_assessment_tool",
    description=(
        "Estimate survival and event probabilities using 11 required clinical "
        "inputs. Experimental; not clinically validated."
    ),
)
def risk_assessment_tool(
    patient_data: PatientData,
    horizon_days: float = 100,
) -> str:
    """Run the model and return a JSON response."""
    result = run_risk_assessment(
        patient_data=patient_data.model_dump(),
        horizon_days=horizon_days,
    )
    return json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    server.run(transport="streamable-http", host="127.0.0.1", port=8000,
               json_response=True)
