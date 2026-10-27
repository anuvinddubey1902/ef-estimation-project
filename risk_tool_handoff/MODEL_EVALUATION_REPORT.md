# Risk Model Evaluation Report

## 1. Purpose

This report documents the currently saved evaluation evidence for the experimental heart-failure survival-risk tool. It does not establish clinical validity or suitability for treatment decisions.

## 2. Dataset

- Dataset: UCI Heart Failure Clinical Records
- Records: 299
- Columns: 13
- Random state for RSF cross-validation: 42

## 3. Random Survival Forest discrimination

The saved evaluation used 5-fold cross-validation.

| Model | Mean C-index | Standard deviation |
|---|---:|---:|
| EF-only RSF | 0.6274 | 0.0818 |
| Full-feature RSF | 0.7266 | 0.0653 |

The mean C-index difference (full-feature minus EF-only) was 0.0992. This is a descriptive comparison; it does not by itself establish statistical significance or clinical benefit.

## 4. Prediction error at 100 days

- Model: Full-feature Random Survival Forest
- Evaluation: 5-fold cross-validation
- Time horizon: 100 days
- Mean Brier score: 0.1553
- Standard deviation: 0.0261

The calibration evaluation used 5-fold cross-validation with inverse-probability-of-censoring weighting, with 4 bins. Its saved mean Brier score and standard deviation are 0.1553 and 0.0261, respectively. The Brier score measures probabilistic prediction error; lower values are generally preferable when evaluations are comparable.

## 5. Cox survival analysis

- Apparent training-data C-index: 0.7408
- Log-rank statistic: 1.6745
- Log-rank p-value: 0.195651
- EF proportional-hazards test p-value: 0.0127

The Cox C-index is an apparent training-data estimate, not a cross-validated estimate. The EF proportional-hazards test result suggests a potential violation of the proportional-hazards assumption. The log-rank result should not be interpreted as proof that groups are equivalent.

## 6. Limitations and permitted interpretation

- These are preliminary results on the UCI Heart Failure Clinical Records dataset.
- No external validation or prospective clinical validation is documented in these results.
- The metrics do not establish clinical utility, safety, or treatment suitability.
- The Cox apparent C-index must not be compared as if it were obtained under the same validation protocol as the RSF cross-validation results.
- These aggregate evaluation metrics are not individual-patient risk thresholds.
- Risk assessment must remain unavailable when any required clinical input is missing.
- EF alone, an image, a segmentation mask, or an uncertainty estimate must not be used to fabricate missing clinical inputs.
- Individual predictions, if used for research, must be labelled experimental estimates and not diagnoses or clinical advice.

## 7. Source files

This report was generated from:

- `results/rsf_cv_metrics.json`
- `results/brier_score_100_days_metrics.json`
- `results/calibration_100_days_metrics.json`
- `results/survival_analysis_metrics.json`

## 8. Validation status

**Experimental; not clinically validated.** Further independent validation, assessment of calibration and discrimination, and clinical review would be required before clinical use.

## 9. Evaluation sample-count limitation

The source dataset contains 299 records. The saved fold-level C-index and
100-day Brier-score files each contain five metric rows, one per fold.
Those files do not record the number of validation samples contributing to
each fold's metric. Therefore, per-fold validation sample counts are not
reported here. The 299-record dataset size must not be interpreted as the
number of samples evaluated in each individual fold.
