"""Divergence Index Calculator.

Computes demographic-specific inflation rates by weighting CPI sub-category
changes according to each group's actual spending patterns.

The Divergence Index reveals how much each group's experienced inflation
deviates from the headline CPI average.

Methodology:
    DI_g(t) = SUM_i [ w_g,i * ((CPI_i(t) - CPI_i(t-1)) / CPI_i(t-1)) ]

    Where:
        g = demographic group
        i = expenditure category
        w_g,i = weight (share of wallet) for group g, category i
        CPI_i(t) = CPI index for category i in year t
"""

from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    WEIGHTS, CPI_SERIES, NON_DISCRETIONARY, DISCRETIONARY,
    MEDIAN_INCOMES, START_YEAR, END_YEAR,
)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


def load_cpi_data() -> pd.DataFrame:
    """Load the annual CPI pivot table."""
    path = RAW_DIR / "cpi_annual_pivot.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"CPI data not found at {path}. Run data/pull_bls_cpi.py first."
        )
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(int)
    df.index.name = "year"
    return df


def calculate_yoy_changes(cpi_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate year-over-year percentage changes for each CPI category."""
    pct = cpi_df.pct_change() * 100
    pct = pct.dropna(how="all")
    return pct


def calculate_divergence_index(
    cpi_changes: pd.DataFrame,
    weights: dict[str, dict[str, float]],
) -> pd.DataFrame:
    """Calculate the weighted Divergence Index for each demographic group.

    Returns DataFrame with columns: year, group, divergence_index, headline_cpi
    """
    results = []

    for year in cpi_changes.index:
        headline = cpi_changes.loc[year].get("all_items", np.nan)

        for group_name, group_weights in weights.items():
            weighted_inflation = 0.0
            total_weight_used = 0.0

            for category, weight in group_weights.items():
                if category in cpi_changes.columns:
                    cat_change = cpi_changes.loc[year, category]
                    if pd.notna(cat_change):
                        weighted_inflation += weight * cat_change
                        total_weight_used += weight

            # Normalize if some categories were missing
            if total_weight_used > 0 and total_weight_used < 0.95:
                weighted_inflation = weighted_inflation / total_weight_used

            divergence = weighted_inflation - headline if pd.notna(headline) else np.nan

            results.append({
                "year": year,
                "group": group_name,
                "group_inflation": round(weighted_inflation, 2),
                "headline_cpi": round(headline, 2) if pd.notna(headline) else np.nan,
                "divergence": round(divergence, 2) if pd.notna(divergence) else np.nan,
            })

    df = pd.DataFrame(results)
    return df


def calculate_cumulative_inflation(
    cpi_df: pd.DataFrame,
    weights: dict[str, dict[str, float]],
    base_year: int = 2021,
) -> pd.DataFrame:
    """Calculate cumulative inflation by compounding weighted YoY rates.

    This matches the YoY rates displayed on the chart: for each year we
    compute the weighted group inflation rate, then compound across years.
    """
    cpi_changes = calculate_yoy_changes(cpi_df)
    results = []

    for group_name, group_weights in weights.items():
        cumulative_factor = 1.0

        for year in cpi_df.index:
            if year < base_year:
                continue

            if year == base_year:
                results.append({
                    "year": year,
                    "group": group_name,
                    "cumulative_inflation": 0.0,
                })
                continue

            yoy_rate = 0.0
            total_weight = 0.0
            for category, weight in group_weights.items():
                if category in cpi_changes.columns and year in cpi_changes.index:
                    cat_change = cpi_changes.loc[year, category]
                    if pd.notna(cat_change):
                        yoy_rate += weight * cat_change
                        total_weight += weight

            if total_weight > 0 and total_weight < 0.95:
                yoy_rate = yoy_rate / total_weight

            cumulative_factor *= (1 + yoy_rate / 100)

            results.append({
                "year": year,
                "group": group_name,
                "cumulative_inflation": round((cumulative_factor - 1) * 100, 2),
            })

    return pd.DataFrame(results)


def calculate_nondiscretionary_burden(
    cpi_df: pd.DataFrame,
    weights: dict[str, dict[str, float]],
    incomes: dict[str, dict[int, float]],
    base_year: int = 2021,
) -> pd.DataFrame:
    """Calculate the non-discretionary spending burden for each group.

    Shows what % of income goes to must-pay expenses and how it shifts.
    """
    results = []

    for group_name, group_weights in weights.items():
        group_income = incomes.get(group_name, {})
        base_income = group_income.get(base_year, 50000)

        # Calculate base-year dollar amounts per category
        base_spending = {}
        for cat, weight in group_weights.items():
            base_spending[cat] = weight * base_income

        for year in cpi_df.index:
            if year < base_year:
                continue

            income = group_income.get(year, base_income)
            nondiscretionary_cost = 0.0
            discretionary_cost = 0.0
            total_cost = 0.0

            for cat, weight in group_weights.items():
                if cat not in cpi_df.columns:
                    continue

                base_cpi = cpi_df.loc[base_year, cat] if base_year in cpi_df.index else np.nan
                curr_cpi = cpi_df.loc[year, cat]

                if pd.notna(base_cpi) and pd.notna(curr_cpi) and base_cpi > 0:
                    price_ratio = curr_cpi / base_cpi
                    adjusted_cost = base_spending.get(cat, 0) * price_ratio
                else:
                    adjusted_cost = base_spending.get(cat, 0)

                total_cost += adjusted_cost

                if cat in NON_DISCRETIONARY:
                    nondiscretionary_cost += adjusted_cost
                elif cat in DISCRETIONARY:
                    discretionary_cost += adjusted_cost

            nondiscretionary_pct = (nondiscretionary_cost / income * 100) if income > 0 else 0
            discretionary_pct = (discretionary_cost / income * 100) if income > 0 else 0
            total_burden = (total_cost / income * 100) if income > 0 else 0
            disposable_pct = max(0, 100 - total_burden)

            results.append({
                "year": year,
                "group": group_name,
                "income": income,
                "nondiscretionary_cost": round(nondiscretionary_cost),
                "discretionary_cost": round(discretionary_cost),
                "total_cost": round(total_cost),
                "nondiscretionary_pct": round(nondiscretionary_pct, 1),
                "discretionary_pct": round(discretionary_pct, 1),
                "total_burden_pct": round(total_burden, 1),
                "disposable_pct": round(disposable_pct, 1),
            })

    return pd.DataFrame(results)


def calculate_cumulative_dec_to_dec(
    raw_csv: str = "data/raw/cpi_midwest_raw.csv",
    weights: dict[str, dict[str, float]] = None,
    base_year: int = 2020,
) -> pd.DataFrame:
    """Calculate cumulative inflation using December index levels.

    Base = December of base_year. Each subsequent December is compared
    to that base via a weighted cost index per group.
    """
    if weights is None:
        weights = WEIGHTS
    df = pd.read_csv(raw_csv)
    dec = df[df["month"] == 12]
    pivot = dec.pivot_table(index="year", columns="series_name", values="value")
    base = pivot.loc[base_year]

    results = []
    for year in sorted(pivot.index):
        # Midwest CPI headline
        mw_cum = ((pivot.loc[year, "all_items"] / base["all_items"]) - 1) * 100

        for group_name, group_weights in weights.items():
            cost_index = sum(
                w * (pivot.loc[year, cat] / base[cat])
                for cat, w in group_weights.items()
                if cat in pivot.columns
            )
            cum = (cost_index - 1) * 100
            results.append({
                "year": year,
                "group": group_name,
                "cumulative_inflation": round(cum, 2),
                "midwest_cpi_cumulative": round(mw_cum, 2),
            })

    return pd.DataFrame(results)


def run_full_analysis() -> dict:
    """Execute the complete Divergence Index analysis pipeline."""
    print("=" * 60)
    print("DIVERGENCE INDEX ANALYSIS PIPELINE")
    print("=" * 60)

    # Load CPI data
    print("\n[1/4] Loading CPI data...")
    cpi_df = load_cpi_data()
    print(f"  Loaded {len(cpi_df)} years, {len(cpi_df.columns)} categories")

    # Calculate YoY changes
    print("\n[2/4] Calculating year-over-year CPI changes...")
    cpi_changes = calculate_yoy_changes(cpi_df)
    cpi_changes.to_csv(PROCESSED_DIR / "cpi_yoy_changes.csv")
    print(f"  Computed changes for {len(cpi_changes)} years")

    # Calculate Divergence Index
    print("\n[3/4] Computing Divergence Index...")
    di_df = calculate_divergence_index(cpi_changes, WEIGHTS)
    di_df.to_csv(PROCESSED_DIR / "divergence_index.csv", index=False)
    print(f"  Computed index for {di_df['group'].nunique()} groups")

    # Print Divergence Index table
    print("\n  DIVERGENCE INDEX RESULTS:")
    print("  " + "-" * 56)
    for _, row in di_df.iterrows():
        print(
            f"  {row['year']}  {row['group']:30s}  "
            f"Group: {row['group_inflation']:+.1f}%  "
            f"CPI: {row['headline_cpi']:+.1f}%  "
            f"Gap: {row['divergence']:+.1f}%"
        )

    # Cumulative inflation
    print("\n  CUMULATIVE INFLATION (since 2021):")
    cum_df = calculate_cumulative_inflation(cpi_df, WEIGHTS)
    cum_df.to_csv(PROCESSED_DIR / "cumulative_inflation.csv", index=False)
    for _, row in cum_df[cum_df["year"] == END_YEAR].iterrows():
        print(f"  {row['group']:30s}  {row['cumulative_inflation']:+.1f}% total")

    # Dec-to-Dec cumulative
    cum_d2d = calculate_cumulative_dec_to_dec()
    cum_d2d.to_csv(PROCESSED_DIR / "cumulative_dec_to_dec.csv", index=False)
    print("\n  CUMULATIVE INFLATION (Dec-to-Dec, base Dec 2020):")
    for _, row in cum_d2d[cum_d2d["year"] == END_YEAR].iterrows():
        print(f"  {row['group']:30s}  {row['cumulative_inflation']:+.1f}%")
    mw_end = cum_d2d[cum_d2d["year"] == END_YEAR].iloc[0]["midwest_cpi_cumulative"]
    print(f"  {'Midwest CPI':30s}  {mw_end:+.1f}%")

    # Non-discretionary burden
    print("\n[4/4] Analyzing non-discretionary burden...")
    burden_df = calculate_nondiscretionary_burden(cpi_df, WEIGHTS, MEDIAN_INCOMES)
    burden_df.to_csv(PROCESSED_DIR / "nondiscretionary_burden.csv", index=False)

    print("\n  NON-DISCRETIONARY BURDEN (% of income):")
    print("  " + "-" * 56)
    for group in WEIGHTS:
        g = burden_df[burden_df["group"] == group]
        if len(g) >= 2:
            first = g.iloc[0]
            last = g.iloc[-1]
            shift = last["nondiscretionary_pct"] - first["nondiscretionary_pct"]
            print(
                f"  {group:30s}  "
                f"{first['year']}: {first['nondiscretionary_pct']:.1f}%  ->  "
                f"{last['year']}: {last['nondiscretionary_pct']:.1f}%  "
                f"(shift: {shift:+.1f}pp)"
            )

    print("\n" + "=" * 60)
    print("Analysis complete. Results saved to data/processed/")
    print("=" * 60)

    return {
        "cpi": cpi_df,
        "cpi_changes": cpi_changes,
        "divergence_index": di_df,
        "cumulative": cum_df,
        "burden": burden_df,
    }


if __name__ == "__main__":
    run_full_analysis()
