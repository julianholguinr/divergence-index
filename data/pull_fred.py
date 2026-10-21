"""Pull macroeconomic data from FRED (Federal Reserve Economic Data).

Fetches Federal Funds Rate, headline CPI, and other macro context
for the 2021-2025 analysis period.

Usage:
    python -m data.pull_fred
"""

from pathlib import Path

import pandas as pd
import requests

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FRED_API_KEY, START_YEAR, END_YEAR

RAW_DIR = Path(__file__).parent / "raw"
RAW_DIR.mkdir(exist_ok=True)

FRED_SERIES = {
    "FEDFUNDS":    "Federal Funds Rate (%)",
    "CPIAUCSL":    "CPI-U All Items (seasonally adjusted)",
    "CPILFESL":    "Core CPI (less food and energy)",
    "UNRATE":      "Unemployment Rate (%)",
    "DPCERA3M086SBEA": "Real Personal Consumption Expenditures",
    "PSAVERT":     "Personal Savings Rate (%)",
    "MORTGAGE30US": "30-Year Fixed Mortgage Rate (%)",
}


def pull_fred_series(series_id: str, start: str, end: str) -> pd.DataFrame:
    """Pull a single FRED series via the public API or direct CSV download."""
    # Use FRED's direct CSV download (no API key needed)
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start}-01-01&coed={end}-12-31"
    try:
        df = pd.read_csv(url, parse_dates=["observation_date"])
        df.columns = ["date", "value"]
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])
        return df
    except Exception as e:
        print(f"[FRED] Error fetching {series_id}: {e}")
        return pd.DataFrame()


def pull_all_fred_data() -> pd.DataFrame:
    """Pull all FRED series and save."""
    all_data = []

    for series_id, label in FRED_SERIES.items():
        print(f"[FRED] Pulling {label} ({series_id})...")
        df = pull_fred_series(series_id, str(START_YEAR), str(END_YEAR))
        if not df.empty:
            df["series_id"] = series_id
            df["series_name"] = label
            all_data.append(df)
            print(f"  -> {len(df)} observations")

    if not all_data:
        print("[FRED] No data retrieved.")
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)
    output_path = RAW_DIR / "fred_macro_data.csv"
    combined.to_csv(output_path, index=False)
    print(f"\n[FRED] Saved {len(combined)} total rows to {output_path}")

    # Create annual summary
    combined["year"] = combined["date"].dt.year
    annual = combined.groupby(["series_name", "year"])["value"].mean().reset_index()
    annual_pivot = annual.pivot_table(index="year", columns="series_name", values="value")
    annual_path = RAW_DIR / "fred_annual_summary.csv"
    annual_pivot.to_csv(annual_path)
    print(f"[FRED] Annual summary saved to {annual_path}")

    return combined


if __name__ == "__main__":
    pull_all_fred_data()
