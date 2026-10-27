# MCP Risk Tool Handoff for Archita

## Purpose

The `risk_assessment_tool` MCP tool exposes Anuvind's experimental Random Survival Forest model for use by the LangGraph/report agent.

## Connection

- Transport: MCP Streamable HTTP
- Local Colab endpoint: `http://127.0.0.1:8000/mcp`
- Tool name: `risk_assessment_tool`

The endpoint is local to the current Colab runtime, not a public URL. The MCP server must be running in that runtime.

## Required inputs

The tool accepts `patient_data` and optional `horizon_days` (default: 100). All 11 fields in `patient_data` are required:

- `age`
- `anaemia`
- `creatinine_phosphokinase`
- `diabetes`
- `ejection_fraction`
- `high_blood_pressure`
- `platelets`
- `serum_creatinine`
- `serum_sodium`
- `sex`
- `smoking`

Binary fields use 0/1 coding. Verify units and coding against the source dataset before using real clinical records.

## Example tool arguments

Synthetic values for software testing only:

    {
      "patient_data": {
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
        "smoking": 0
      },
      "horizon_days": 100
    }

## Successful result

The result includes `status`, `risk_assessed`, `horizon_days`, `survival_probability`, `event_probability`, and `model`.

The survival and event probabilities should sum to approximately 1. Parse JSON returned inside an MCP text content item before using it in a report.

## Missing or invalid inputs

All 11 clinical fields are required. Missing data must not be guessed or inferred from an echo image.

Live MCP tests confirmed that missing required fields and unexpected fields are rejected by schema validation. Invalid binary values (for example, `smoking = 2`) and unsupported prediction horizons return structured wrapper errors.

The verified supported prediction horizon is 4–285 days. The tool must reject horizons outside this range.

Validation failures may arrive as an MCP tool error (`isError: true`). Wrapper-level errors may instead return JSON with `status: error`, `risk_assessed: false`, and an `error` object, even when MCP reports `isError: false`.

Therefore, inspect both the MCP error flag and the returned tool payload. Never present an error as a risk estimate.

## Agent requirements and limitations

- State the prediction horizon.
- Describe probabilities as experimental model estimates, not a diagnosis.
- Do not invent low/medium/high risk categories or unsupported thresholds.
- Do not claim clinical validation or clinical utility.
- An EF estimate alone does not provide the other required clinical inputs.
- The model was developed using 299 records from the UCI Heart Failure Clinical Records dataset and has not been externally validated.

## Verified implementation status

- Python wrapper tested.
- MCP Streamable HTTP server tested in Colab.
- Tool discovery verified; all 11 required fields are in the schema.
- Synthetic valid-input call tested successfully through MCP Streamable HTTP; HTTP 200 and isError=false.
- Missing-input validation tested; missing required fields are rejected.
- Unexpected-field validation tested; extra fields are rejected.
- Invalid binary input tested; structured `invalid_input` error returned.
- Out-of-range horizon tested; structured `invalid_input` error returned.
- Successful synthetic response verified; probability sum and requested horizon checked.
- Automated regression suite: 15 tests passed in the current environment.
- Public/remote deployment is not configured.
- External clinical validation is not completed.

## 9. Separation of responsibilities

The model, reporting agent, and human reviewer have distinct responsibilities.

- The model produces experimental survival and event probability estimates; it does not diagnose or assign clinical risk categories.
- The reporting agent must check prediction status and output validity before including estimates in an individual report.
- Individual reports must identify the prediction horizon, describe the output as an experimental model estimate, and disclose relevant limitations.
- Statistical analysis must document the cohort, inclusion criteria, missing-data handling, method, prediction horizon, uncertainty reporting, and limitations.
- Statistical metadata checks establish documentation completeness only; they do not prove scientific or clinical validity.
- Risk categories must remain null until independently validated thresholds have been documented and approved for the intended use.
- Failed predictions, invalid outputs, or missing required clinical inputs must not be represented as valid estimates.
- Human review remains necessary for consequential interpretation. Model outputs must not be the sole basis for diagnosis or treatment decisions.

Implementation:
- Contract: `risk_tool_handoff/PREDICTION_USE_CONTRACT.json`
- Eligibility checks: `src/risk/report_eligibility.py`
- Individual-report function: `check_individual_report_eligibility`
- Statistical-analysis function: `check_statistical_analysis_eligibility`

The eligibility functions perform software and metadata checks only. They do not establish clinical validation or authorize clinical use.
