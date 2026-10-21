"""Master pipeline runner for the Divergence Index analysis.

Usage:
    python3 run_pipeline.py          # Run full pipeline
    python3 run_pipeline.py --skip-pull  # Skip data pull (use cached)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def main():
    skip_pull = "--skip-pull" in sys.argv

    if not skip_pull:
        print("\n[STAGE 1] Pulling BLS CPI data...")
        from data.pull_bls_cpi import pull_all_cpi_data
        pull_all_cpi_data()

        print("\n[STAGE 2] Pulling FRED macro data...")
        from data.pull_fred import pull_all_fred_data
        pull_all_fred_data()
    else:
        print("\n[STAGE 1-2] Skipping data pull (using cached data)")

    print("\n[STAGE 3] Running Divergence Index analysis...")
    from analysis.divergence_index import run_full_analysis
    run_full_analysis()

    print("\n[STAGE 4] Generating visualizations...")
    from visualizations.charts import generate_all_charts
    generate_all_charts()

    print("\n[STAGE 5] Generating executive summary...")
    from analysis.executive_summary import generate_summary
    generate_summary()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Charts:  {Path('output').resolve()}/")
    print(f"  Summary: {Path('output/executive_summary.txt').resolve()}")
    print(f"  Data:    {Path('data/processed').resolve()}/")


if __name__ == "__main__":
    main()
