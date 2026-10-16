"""Create leakage-controlled historical establishment features.

The script adds two features to the existing sample-level modeling dataset:

* ``prior_sample_count``: number of eligible samples from the same
  establishment in earlier fiscal years present in the supplied dataset.
* ``prior_positive_rate``: positive outcomes divided by eligible samples from
  the same establishment in those earlier fiscal years.

Important: history is aggregated at the establishment-year level and the
current fiscal year's outcomes are excluded. This is appropriate for a
fiscal-year-ahead evaluation, but it does not guarantee that those historical
results would have been available in real time. For operational prediction,
use actual result-availability timestamps where possible.

Example:
    python src/feature_engineering.py \
        --input data/processed/salmonella_chicken_parts_v1.parquet \
        --output data/processed/salmonella_chicken_parts_history_v1.parquet
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "establishment_id",
    "fiscal_year",
    "target_salmonella",
}

HISTORY_COLUMNS = ["prior_sample_count", "prior_positive_rate"]


def add_historical_establishment_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with prior-fiscal-year establishment features.

    For each establishment in a given fiscal year, history is calculated from
    that establishment's records in strictly earlier fiscal years represented
    in the input. The function never uses same-year outcomes to construct the
    historical features.

    Missing historical positivity rate is retained as NaN when an
    establishment has no earlier records. It is not changed to zero.

    Raises:
        ValueError: If required columns are missing, identifiers are missing,
            fiscal years are invalid, or target labels are not binary.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing:
        raise ValueError(f"Required columns are missing: {missing}")

    result = df.copy()

    if result["establishment_id"].isna().any():
        raise ValueError(
            "establishment_id contains missing values; resolve them before "
            "calculating establishment history."
        )

    years = pd.to_numeric(result["fiscal_year"], errors="coerce")
    if years.isna().any() or not np.all(years == np.floor(years)):
        raise ValueError("fiscal_year must contain valid integer years")
    result["fiscal_year"] = years.astype(int)

    labels = pd.to_numeric(result["target_salmonella"], errors="coerce")
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError(
            "target_salmonella must contain only binary values 0 and 1; "
            "filter or resolve unlabeled rows before feature engineering."
        )
    result["target_salmonella"] = labels.astype("int8")

    # Avoid silently replacing pre-existing columns if the function is run
    # on a dataset that already contains history fields.
    existing = [col for col in HISTORY_COLUMNS if col in result.columns]
    if existing:
        raise ValueError(
            "Input already contains historical feature columns: "
            f"{existing}. Use the original v1 file as input to avoid "
            "overwriting or duplicating them."
        )

    annual = (
        result.groupby(
            ["establishment_id", "fiscal_year"],
            as_index=False,
            sort=True,
        )
        .agg(
            samples_in_year=("target_salmonella", "size"),
            positives_in_year=("target_salmonella", "sum"),
        )
        .sort_values(["establishment_id", "fiscal_year"])
        .reset_index(drop=True)
    )

    grouped = annual.groupby("establishment_id", sort=False)

    annual["prior_sample_count"] = (
        grouped["samples_in_year"].cumsum() - annual["samples_in_year"]
    ).astype("int64")

    annual["prior_positive_count"] = (
        grouped["positives_in_year"].cumsum() - annual["positives_in_year"]
    ).astype("int64")

    annual["prior_positive_rate"] = (
        annual["prior_positive_count"]
        / annual["prior_sample_count"].replace(0, np.nan)
    )

    lookup = annual[
        [
            "establishment_id",
            "fiscal_year",
            "prior_sample_count",
            "prior_positive_rate",
        ]
    ]

    # Many sample rows map to one establishment/fiscal-year history row.
    result = result.merge(
        lookup,
        on=["establishment_id", "fiscal_year"],
        how="left",
        validate="many_to_one",
        sort=False,
    )

    if len(result) != len(df):
        raise AssertionError(
            f"Row count changed from {len(df)} to {len(result)}"
        )

    if result["prior_sample_count"].isna().any():
        raise AssertionError("prior_sample_count should never be missing")

    if (result["prior_sample_count"] < 0).any():
        raise AssertionError("Negative historical sample counts found")

    valid_rates = result["prior_positive_rate"].dropna()
    if not valid_rates.between(0, 1).all():
        raise AssertionError("Historical positivity rates must be in [0, 1]")

    return result


def build_parser() -> argparse.ArgumentParser:
    """Create command-line arguments with repository-relative defaults."""
    repo_root = Path(__file__).resolve().parents[1]
    default_input = (
        repo_root / "data" / "processed" / "salmonella_chicken_parts_v1.parquet"
    )
    default_output = (
        repo_root
        / "data"
        / "processed"
        / "salmonella_chicken_parts_history_v1.parquet"
    )

    parser = argparse.ArgumentParser(
        description="Add historical establishment features to Salmonella data."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help=f"Input Parquet file (default: {default_input})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help=f"Output Parquet file (default: {default_output})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input.exists():
        parser.error(
            f"Input file not found: {args.input}. "
            "Download the source data and create the prepared v1 dataset first."
        )

    if args.input.resolve() == args.output.resolve():
        parser.error(
            "Input and output paths must differ; the source dataset must not be overwritten."
        )

    df = pd.read_parquet(args.input)
    enriched = add_historical_establishment_features(df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_parquet(args.output, index=False)

    print("Historical feature engineering completed.")
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print(f"Rows preserved: {len(df):,} -> {len(enriched):,}")
    print(
        "Rows with earlier establishment samples: "
        f"{int(enriched['prior_sample_count'].gt(0).sum()):,}"
    )
    print(
        "Rows without earlier establishment samples: "
        f"{int(enriched['prior_sample_count'].eq(0).sum()):,}"
    )
    print(
        "Rows with undefined prior positivity rate: "
        f"{int(enriched['prior_positive_rate'].isna().sum()):,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
