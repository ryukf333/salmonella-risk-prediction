# Discussion (working draft)

> **Status:** Draft for a portfolio project. Do not present the FY2026 classification metrics as final until the saved prediction file and reported confusion matrix are reconciled. The interpretation below distinguishes completed validation results from provisional test output.

## Main findings

This project examined whether recorded sampling and product characteristics could predict Salmonella positivity in raw chicken breast, leg, and wing samples. The working dataset contained 66,939 labeled records from FY2022–FY2026, with 5,718 positives (8.54%). The data were class-imbalanced, making accuracy alone an inadequate performance measure.

In the initial FY2025 validation comparison, Logistic Regression achieved an Average Precision (AP) of 0.1240 and ROC-AUC of 0.5756. Random Forest and XGBoost produced similar but slightly lower Average Precision (0.1144 and 0.1189, respectively). The DummyClassifier AP was 0.0881, close to the validation positive-class prevalence of 8.81%. These values suggest that the original predictor set contained some signal, but discrimination was weak.

Adding establishment-history features improved the reported FY2025 validation results. Logistic Regression AP rose from 0.1239 to 0.1548, while ROC-AUC increased from 0.5826 to 0.6265. This suggests that previous observations at an establishment may provide useful information beyond broad state, project, product, and month categories.

The bounded hyperparameter search produced the following best validation results: Logistic Regression AP 0.1597 / ROC-AUC 0.6335; Random Forest AP 0.1582 / ROC-AUC 0.6353; and XGBoost AP 0.1562 / ROC-AUC 0.6346. The differences were small. Logistic Regression was selected based on the predefined primary metric, Average Precision, and its relative simplicity.

## Interpretation of establishment history

The historical features were calculated using the same establishment's records from earlier fiscal years only. `prior_sample_count` measures prior recorded sample volume, while `prior_positive_rate` represents the fraction of prior recorded samples with positive results. These variables may make predictions more informative because they summarize earlier surveillance outcomes.

However, an establishment's historical positivity rate is not a direct measurement of its true contamination risk. It depends on which products were sampled, how frequently the establishment was sampled, the purpose of the sampling program, and which results were available in the source data. Historical features may therefore capture surveillance selection and sampling intensity as well as persistent differences between establishments.

The features are leakage-controlled at the fiscal-year level: current-year outcomes are excluded from the features for that year. This supports the stated annual temporal split. For a real-time prediction system, the actual dates at which earlier test results became available would need to be verified.

## Sampling program and population definition

The analysis retained breast, leg, and wing records from `Product-Raw-Intact-Chicken`, including both routine and follow-up sampling projects. Earlier descriptive analysis showed substantially different positive rates between the two project codes. This suggests that project membership may reflect different sample-selection processes. Predictive relationships should not be interpreted as causal effects, and performance may depend on the sampling program represented in the evaluation data.

The selected records constitute a surveillance dataset, not a probability sample of all chicken sold to consumers. The observed positive rates should therefore be described as rates among these recorded samples rather than national prevalence estimates.

## Test-evaluation status

One FY2026 run reported AP 0.1789, ROC-AUC 0.6621, precision 0.1729, recall 0.3844, and F1 0.2386 at a threshold selected on FY2025. That run's confusion matrix was reported as 7,901 true negatives, 1,607 false positives, 538 false negatives, and 336 true positives.

A subsequent summary of the saved individual predictions reported a different set of counts: 8,089 true negatives, 1,419 false positives, 553 false negatives, and 321 true positives. Both summaries total 10,382 samples, but they cannot both describe the same predictions at the same threshold. Possible causes include stale/overwritten prediction files, a changed model or threshold, or a mismatch between prediction records and evaluation output.

Accordingly, these FY2026 numbers must be considered provisional until the model, threshold, predictions, and metrics are regenerated and read from one consistent run. In addition, FY2026 was inspected during development, so it is more accurate to call it a temporal evaluation set than a completely untouched independent test. A future fiscal-year snapshot that has not influenced model decisions would provide a stronger final generalization test.

## Practical significance

The current model should be viewed as an exploratory risk-ranking model rather than a ready-to-deploy screening tool. In the initial baseline, precision near 11% and recall below 50% at a 0.5 threshold indicated many false-positive predictions and missed positives. Threshold choice changes the precision–recall trade-off but does not fix weak ranking performance. Operational use would require a clearly defined use case, a decision-cost analysis, calibration checks if probabilities are to be interpreted as risks, and independent validation.

## Limitations

- The predictor set is limited and primarily categorical.
- The source reflects FSIS sampling and laboratory practices, which may change over time.
- Routine and follow-up sampling can involve different selection mechanisms.
- Historical establishment features may encode surveillance volume or selection patterns.
- Establishments appear across multiple fiscal years, so temporal evaluation does not automatically test transfer to entirely unseen establishments.
- FY2026 covers only part of the fiscal year in the available snapshot.
- FY2026 results were reviewed during development, reducing their status as an untouched holdout.
- The final FY2026 confusion matrix and individual-prediction summary are inconsistent and must be reconciled.
- The target is binary test positivity; quantitative Salmonella concentration is not predicted.

## Conclusion

The analysis shows that historical establishment information improved validation ranking performance over the initial feature set, but the overall discrimination remains modest. The most defensible conclusion is that the current data and features contain some predictive signal for recorded Salmonella positivity in the selected chicken-part samples, while substantial uncertainty and sampling-design limitations remain. The project is suitable as a transparent portfolio study, provided final test outputs are reconciled and the limitations are reported clearly.

## Source

USDA Food Safety and Inspection Service (FSIS), [Laboratory Sampling Data](https://www.fsis.usda.gov/science-data/data-sets-visualizations/laboratory-sampling-data). FSIS advises users to review the included metadata because it describes dataset fields, testing-method changes, and why results for different pathogens may not be present for every sample. The page also warns that these product-testing datasets alone do not establish associations with human illnesses.
