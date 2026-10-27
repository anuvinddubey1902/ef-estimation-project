# Risk Assessment Tool — Agent Integration Contract

## 1. Tool identity

- Tool name: `risk_assessment_tool`
- Python module: `risk.risk_tool`
- Purpose: Estimate survival and event probabilities at a specified time horizon.
- Status: Experimental; not clinically validated.

## 2. Invocation

The Python wrapper is exposed through an MCP server using Streamable HTTP.

The MCP tool name is `risk_assessment_tool`. Its arguments are `patient_data` and optional `horizon_days` (default 100).

In the current Colab runtime, the server listens at `http://127.0.0.1:8000/mcp`. This address is local to that runtime and is not a public endpoint.

## 3. Required clinical inputs

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

All 11 inputs are required. Binary inputs use 0/1 coding.
Verify units and coding against the source dataset before using real clinical records.
Never invent or infer missing clinical measurements.

## 4. Successful response

A successful response contains `status`, `risk_assessed`, `horizon_days`,
`survival_probability`, `event_probability`, and `model`.

- `status` must be `success`.
- `risk_assessed` must be `true`.
- `survival_probability` and `event_probability` should each be probabilities.
- The two probabilities should sum to approximately 1.
- Confirm that the returned horizon matches the requested horizon.

A successful synthetic MCP call was verified in the current Colab runtime.
Its numerical output is a software integration test, not clinical evidence.

## 5. Error handling

The live MCP tests verified these rejection cases:

- Missing required clinical field: rejected by MCP schema validation.
- Unexpected clinical field: rejected by MCP schema validation.
- Invalid binary value (for example, `smoking = 2`): returned as a structured
  `invalid_input` error by the risk tool.
- Unsupported prediction horizon: returned as a structured `invalid_input`
  error. The verified supported horizon range is 4–285 days.

Two error paths must be handled separately:

1. MCP/schema-level errors can return `result.isError = true`.
2. The tool can return `result.isError = false` while its text content contains
   JSON with `status = "error"` and `risk_assessed = false`.

The agent must inspect the tool payload and must never treat an error as a
risk estimate. Do not rely on `isError` alone.

## 6. Agent behavior requirements

- Never fabricate missing clinical measurements.
- Do not assign low, medium, or high risk categories without a separately validated threshold system.
- State the prediction horizon and clarify that the output is a model estimate, not a diagnosis.
- Do not claim clinical validation or clinical utility.
- Do not substitute model output for professional judgment.

## 7. Model limitations

The model was developed using the UCI Heart Failure Clinical Records dataset (299 records).
It has not been externally validated for clinical use.
Cross-validation metrics do not establish clinical safety or effectiveness.
An EF estimate from an image does not provide the other ten required clinical inputs.

## 8. Integration status

- Python wrapper: implemented and tested.
- JSON input schema: created and structurally checked.
- Automated tests: 15 passed in the current environment (predictor, wrapper, and input-gate tests).
- MCP Streamable HTTP server: implemented and tested in the current Colab runtime.
- MCP tool discovery: verified; all 11 required clinical fields are exposed through the input schema.
- MCP valid-input call: tested successfully with synthetic data.
- MCP missing-input validation: tested; incomplete data is rejected.
- Public/remote deployment: not implemented.
- External clinical validation: not completed.

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
