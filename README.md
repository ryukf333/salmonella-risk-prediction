# Predicting Salmonella Positivity in Raw Chicken Parts with Interpretable Machine Learning

A machine-learning project using USDA Food Safety and Inspection Service (FSIS) raw poultry sampling records to predict whether a selected raw chicken-part sample has a **recorded positive Salmonella test result**.


## Research question

Can sampling and product characteristics, together with an establishment's historical Salmonella results, help predict recorded Salmonella positivity in raw chicken breast, leg, and wing samples from later fiscal years?

This project predicts the recorded **positive/negative laboratory result**. It does not predict bacterial concentration, establish causes of contamination, diagnose food safety, or estimate nationwide prevalence.

## Data source

The source is the USDA FSIS [Laboratory Sampling Data](https://www.fsis.usda.gov/science-data/data-sets-visualizations/laboratory-sampling-data) page, specifically the Raw Poultry Sampling data product. Download the relevant fiscal-year files from FSIS and review each file's metadata and data dictionary before reproducing the analysis.

FSIS notes that its sampling datasets include metadata describing variables and changes in laboratory testing, and that a poultry sample may have a result for one pathogen but not another. FSIS also cautions that these sampling data alone are not sufficient to determine an association with human illness.

The repository intentionally does **not** include the original ZIP archives, extracted JSON records, or generated Parquet datasets. See [`data/README.md`](data/README.md) for data setup instructions.

## Study population

The analysis dataset used during development contains **66,939 labeled records** from FY2022–FY2026, filtered to:

- `sample_source_name == "Product-Raw-Intact-Chicken"`
- `product_type` in `Breast`, `Leg`, and `Wing`
- valid `target_salmonella` values, where Positive = `1` and Negative = `0`

The observed label distribution in that dataset was:

| Product type | Total samples | Positive | Observed positive rate |
|---|---:|---:|---:|
| Breast | 31,042 | 2,719 | 8.76% |
| Leg | 22,987 | 1,773 | 7.71% |
| Wing | 12,910 | 1,226 | 9.50% |
| **Total** | **66,939** | **5,718** | **8.54%** |

These are descriptive results for the selected FSIS records, not estimates of population-wide contamination prevalence. The filtered data include both routine and follow-up sampling projects, which may represent different sample-selection processes.

## Methodology

### Target

`target_salmonella` is a binary target derived from the original `salmonella_sp_analysis` field:

- `Positive` → `1`
- `Negative` → `0`
- missing or other values are not treated as negative

### Candidate predictors

Initial predictors were:

- `establishment_state`
- `project_code`
- `product_type`
- `collection_month`

The improved model also used two historical features calculated from **earlier fiscal years only** for each establishment:

- `prior_sample_count`: number of previously recorded eligible samples
- `prior_positive_rate`: positive results divided by prior recorded samples

`establishment_id` is used to calculate history, not as a direct predictor. Identifiers, the original target label, source row numbers, and the fiscal-year label are not included as model predictors.

Historical features can reflect surveillance intensity and selection effects as well as underlying patterns. Their real-time availability would need to be confirmed before any operational use.

### Temporal design

| Split | Fiscal years | Role |
|---|---|---|
| Training | FY2022–FY2024 | Fit the initial baseline models |
| Validation | FY2025 | Compare/tune models and choose a classification threshold |
| Later-period evaluation | FY2026 | Temporal evaluation on available FY2026 records |

FY2026 is a **partial fiscal year** in the supplied snapshot. Also, FY2026 results were inspected during development before all final model decisions were complete. They should therefore not be described as a completely untouched independent test set. A later, previously unexamined dataset would provide stronger independent validation.

### Models

- DummyClassifier reference baseline
- Logistic Regression
- Random Forest
- XGBoost

Preprocessing uses imputation and one-hot encoding for categorical predictors. Model comparison emphasizes Average Precision because the positive class is uncommon; ROC-AUC, precision, recall, F1, and balanced accuracy are also reported.

## Results available from validation

### Initial baseline comparison (FY2025)

| Model | Average Precision | ROC-AUC |
|---|---:|---:|
| DummyClassifier | 0.0881 | 0.5000 |
| Logistic Regression | 0.1240 | 0.5756 |
| Random Forest | 0.1144 | 0.5601 |
| XGBoost | 0.1189 | 0.5681 |

### Historical-feature experiment (FY2025)

Adding the two historical establishment features to Logistic Regression improved the reported validation metrics:

| Model | Average Precision | ROC-AUC |
|---|---:|---:|
| Existing baseline Logistic Regression | 0.1239 | 0.5826 |
| Logistic Regression + establishment history | 0.1548 | 0.6265 |

### Bounded hyperparameter tuning (FY2025)

| Model | Best Average Precision | Best ROC-AUC |
|---|---:|---:|
| Logistic Regression (`C=0.01`, balanced class weights) | **0.1597** | 0.6335 |
| Random Forest | 0.1582 | **0.6353** |
| XGBoost | 0.1562 | 0.6346 |

Logistic Regression was selected by the prespecified primary metric, Average Precision. These validation results indicate improvement over the DummyClassifier, but discrimination remains limited.


## Limitations

1. FSIS surveillance samples may not represent all raw chicken products available in the market.
2. Routine and follow-up projects can differ in how samples are selected; project-related predictors may capture sampling design.
3. The available predictors are largely categorical, which limits how much sample-level information the model can learn.
4. Establishment history can be influenced by sampling volume and selection policies, not only by underlying Salmonella risk.
5. FY2026 is incomplete, and its results were viewed during model development.
6. The current performance is too modest to support claims of reliable operational screening without further independent validation.
7. The target records test positivity, not bacterial concentration or causal contamination mechanisms.

## Next steps

- Seek validation on a later, previously unexamined fiscal-year snapshot before making stronger generalization claims.

## Acknowledgment

Data source: U.S. Department of Agriculture, Food Safety and Inspection Service (USDA FSIS), Laboratory Sampling Data.
