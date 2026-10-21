"""Pull CPI sub-category data from the Bureau of Labor Statistics API.

Fetches monthly CPI indices for the Midwest region across all spending
categories needed for the Divergence Index calculation.

Usage:
    python -m data.pull_bls_cpi
"""

import json
import time
from pathlib import Path

import pandas as pd
import requests

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import BLS_API_KEY, BLS_API_URL, CPI_SERIES, START_YEAR, END_YEAR

RAW_DIR = Path(__file__).parent / "raw"
RAW_DIR.mkdir(exist_ok=True)


def pull_bls_series(series_ids: list[str], start: int, end: int) -> dict:
    """Pull multiple series from BLS API v2.

    The BLS API accepts up to 50 series per request.
    Returns raw JSON response data.
    """
    payload = {
        "seriesid": series_ids,
        "startyear": str(start),
        "endyear": str(end),
        "annualaverage": True,
    }
    if BLS_API_KEY:
        payload["registrationkey"] = BLS_API_KEY

    headers = {"Content-type": "application/json"}

    print(f"[BLS] Requesting {len(series_ids)} series ({start}-{end})...")
    resp = requests.post(BLS_API_URL, data=json.dumps(payload), headers=headers, timeout=30)
    resp.raise_for_status()

    result = resp.json()

    if result.get("status") != "REQUEST_SUCCEEDED":
        print(f"[BLS] Warning: {result.get('message', 'Unknown error')}")
        for msg in result.get("message", []):
            print(f"  -> {msg}")

    return result


def parse_bls_response(result: dict, name_map: dict) -> pd.DataFrame:
    """Parse BLS API response into a clean DataFrame.

    Returns DataFrame with columns: year, month, period, value, series_name
    """
    all_rows = []

    for series in result.get("Results", {}).get("series", []):
        series_id = series["seriesID"]
        series_name = name_map.get(series_id, series_id)

        for item in series.get("data", []):
            period = item["period"]
            # M13 = annual average, M01-M12 = monthly
            if period.startswith("M"):
                month = int(period[1:])
                if month > 12:
                    month = 0  # annual average
            else:
                continue

            try:
                val = float(item["value"])
            except (ValueError, TypeError):
                continue

            all_rows.append({
                "series_id": series_id,
                "series_name": series_name,
                "year": int(item["year"]),
                "month": month,
                "period": period,
                "value": val,
            })

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df = df.sort_values(["series_name", "year", "month"]).reset_index(drop=True)
    return df


def pull_all_cpi_data() -> pd.DataFrame:
    """Pull all CPI series and save to CSV."""
    # Build reverse map: series_id -> friendly name
    id_to_name = {v: k for k, v in CPI_SERIES.items()}
    series_ids = list(CPI_SERIES.values())

    # BLS API allows max 50 series per request — we're under that
    result = pull_bls_series(series_ids, START_YEAR, END_YEAR)
    df = parse_bls_response(result, id_to_name)

    if df.empty:
        print("[BLS] No data returned. Check series IDs or API limits.")
        print("[BLS] Without API key, limit is 25 requests/day, 10 years max.")
        return df

    # Save raw data
    output_path = RAW_DIR / "cpi_midwest_raw.csv"
    df.to_csv(output_path, index=False)
    print(f"[BLS] Saved {len(df)} rows to {output_path}")

    # Create annual averages pivot table
    annual = df[df["month"] == 0].copy()  # M13 = annual average
    if annual.empty:
        # Fall back to computing annual mean from monthly data
        monthly = df[df["month"].between(1, 12)]
        annual = monthly.groupby(["series_name", "year"])["value"].mean().reset_index()

    pivot = annual.pivot_table(index="year", columns="series_name", values="value")
    pivot_path = RAW_DIR / "cpi_annual_pivot.csv"
    pivot.to_csv(pivot_path)
    print(f"[BLS] Annual pivot table saved to {pivot_path}")

    # Print summary
    print(f"\n[BLS] CPI Data Summary ({START_YEAR}-{END_YEAR}):")
    print(f"  Series retrieved: {df['series_name'].nunique()}")
    print(f"  Years: {sorted(df['year'].unique())}")
    missing = set(CPI_SERIES.keys()) - set(df["series_name"].unique())
    if missing:
        print(f"  Missing series: {missing}")

    return df


if __name__ == "__main__":
    pull_all_cpi_data()
