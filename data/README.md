# Data access and handling

The raw USDA FSIS sampling archives and derived Parquet datasets are not stored in this repository. Obtain the appropriate **Raw Poultry Sampling** fiscal-year data from the official [FSIS Laboratory Sampling Data page](https://www.fsis.usda.gov/science-data/data-sets-visualizations/laboratory-sampling-data), and read the metadata/data dictionary distributed with each file before analysis.

Place the downloaded archives in `data/raw/`. Build the prepared sample-level dataset through the notebooks in `notebooks/`, or provide the prepared Parquet file at the path documented in `src/feature_engineering.py`.

The source data can change as FSIS updates published snapshots. Record download dates and archive names when reproducing the study. Do not assume every sample was tested for every pathogen; the FSIS metadata explains differences in test availability and methods.
