# Risk Tool Setup Guide

## Purpose

The risk tool uses a trained Random Survival Forest to estimate survival
and event probabilities at a specified time horizon.

These are experimental model estimates, not a diagnosis or clinically
validated decision.

## Required files

- `src/risk/predict_risk.py`
- `src/risk/risk_tool.py`
- `src/risk/risk_input_gate.py`
- `src/risk/mcp_server.py`
- `run_mcp_http.py`
- `models/random_survival_forest.pkl`
- `models/rsf_feature_names.json`
- `requirements.txt`

## Environment setup

Run commands from the repository root.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest -v
```

## Direct prediction interface

The `predict_risk` function accepts all 11 required clinical features
and an optional `horizon_days` argument.

Do not infer missing clinical values from EF, uncertainty, images, or masks.

## MCP server

Start from the repository root:

```bash
python run_mcp_http.py
```

Transport: Streamable HTTP

Endpoint: `http://127.0.0.1:8000/mcp`

The loopback address is for the same machine or runtime. A remote agent
cannot access it directly without an appropriate network deployment.
Do not expose the server publicly without suitable access controls.

MCP tool name: `risk_assessment_tool`

The MCP server may reject invalid inputs before the wrapper runs. Callers
must handle both MCP protocol errors and structured tool errors.

## Successful output fields

- `status`
- `risk_assessed`
- `horizon_days`
- `survival_probability`
- `event_probability`
- `model`

Event probability is one minus survival probability at the requested horizon.

## Error handling and missing data

The tool can return structured errors for invalid inputs, missing data,
model-loading failures, prediction failures, and internal errors.

Missing clinical inputs must not be guessed or silently imputed. Risk
assessment must remain unavailable if any required input is missing.

## Limitations

The model has not been clinically validated for patient care. Do not assign
low, medium, or high risk categories without validated thresholds.
Predictions must not be presented as diagnoses or clinical advice.

Distinguish individual experimental estimates from aggregate research
metrics. Evaluation results do not establish clinical utility or reliability.

## Model artifact security

Only load trusted model pickle files. Loading an untrusted pickle can
execute arbitrary code.
