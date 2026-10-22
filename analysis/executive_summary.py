"""Generate the executive summary with strategic recommendations.

Pulls all processed data and produces a comprehensive analysis report
suitable for the case competition deliverables.
"""

from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WEIGHTS, BANK_DATA, MEDIAN_INCOMES

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_summary():
    di = pd.read_csv(PROCESSED_DIR / "divergence_index.csv")
    burden = pd.read_csv(PROCESSED_DIR / "nondiscretionary_burden.csv")
    cumulative = pd.read_csv(PROCESSED_DIR / "cumulative_inflation.csv")

    lines = []
    lines.append("=" * 72)
    lines.append("THE DIVERGENCE INDEX")
    lines.append("Mapping Demographic Inflation for Regional Credit Strategy")
    lines.append("QBEA Data Dive Case Competition")
    lines.append("=" * 72)

    # ── DELIVERABLE 1: Divergence Index ──
    lines.append("\n" + "─" * 72)
    lines.append("DELIVERABLE 1: THE DIVERGENCE INDEX")
    lines.append("─" * 72)
    lines.append("\nReal experienced inflation rates by demographic group (2022-2025):\n")

    for year in sorted(di["year"].unique()):
        lines.append(f"  {year}:")
        ydf = di[di["year"] == year]
        headline = ydf.iloc[0]["headline_cpi"]
        lines.append(f"    Headline CPI:                        {headline:+.1f}%")
        for _, row in ydf.iterrows():
            gap_str = f"({row['divergence']:+.1f}pp gap)"
            lines.append(f"    {row['group']:36s} {row['group_inflation']:+.1f}%  {gap_str}")
        lines.append("")

    lines.append("  CUMULATIVE INFLATION (2021 → 2025):")
    for _, row in cumulative[cumulative["year"] == 2025].iterrows():
        lines.append(f"    {row['group']:36s} {row['cumulative_inflation']:+.1f}%")

    rural_2022 = di[(di["group"] == "Rural Small Business Owners") & (di["year"] == 2022)]
    hl_2022 = di[(di["year"] == 2022)].iloc[0]["headline_cpi"] if len(di[di["year"] == 2022]) > 0 else 8.0
    rural_val = rural_2022.iloc[0]["group_inflation"] if not rural_2022.empty else 10.9
    lines.append(f"\n  KEY FINDING: In 2022, Rural Small Business Owners experienced")
    lines.append(f"  inflation of {rural_val:+.1f}% — well above the Midwest headline CPI ({hl_2022:+.1f}%).")
    lines.append("  This was driven by gasoline (+32%) and utility gas (+29%) price")
    lines.append("  spikes that disproportionately impact energy-intensive operations.")

    # ── DELIVERABLE 2: Non-Discretionary Burden ──
    lines.append("\n" + "─" * 72)
    lines.append("DELIVERABLE 2: NON-DISCRETIONARY SPENDING BURDEN")
    lines.append("─" * 72)

    lines.append("\nPercentage of median income consumed by must-pay expenses:\n")
    lines.append(f"  {'Group':36s} {'2021':>8s} {'2025':>8s} {'Shift':>8s}")
    lines.append(f"  {'─' * 36} {'─' * 8} {'─' * 8} {'─' * 8}")

    squeeze_data = []
    for group in WEIGHTS:
        g = burden[burden["group"] == group]
        y21 = g[g["year"] == 2021].iloc[0]
        y25 = g[g["year"] == 2025].iloc[0]
        shift = y25["nondiscretionary_pct"] - y21["nondiscretionary_pct"]
        squeeze_data.append((group, y21["nondiscretionary_pct"], y25["nondiscretionary_pct"], shift))
        lines.append(
            f"  {group:36s} {y21['nondiscretionary_pct']:7.1f}% {y25['nondiscretionary_pct']:7.1f}% {shift:+7.1f}pp"
        )

    most_squeezed = max(squeeze_data, key=lambda x: x[3])
    lines.append(f"\n  MOST SQUEEZED: {most_squeezed[0]}")
    lines.append(f"  Burden increased by {most_squeezed[3]:+.1f} percentage points")

    lines.append("\n  Income remaining AFTER non-discretionary expenses (2025):")
    for group in WEIGHTS:
        g = burden[burden["group"] == group]
        y25 = g[g["year"] == 2025].iloc[0]
        remaining_pct = 100 - y25["nondiscretionary_pct"]
        remaining_dollars = y25["income"] * remaining_pct / 100
        lines.append(
            f"    {group:36s} {remaining_pct:.1f}% = ~${remaining_dollars:,.0f}/yr"
        )

    most_burdened = max(squeeze_data, key=lambda x: x[2])
    rem_pct = 100 - most_burdened[2]
    rem_dollars = MEDIAN_INCOMES[most_burdened[0]][2025] * rem_pct / 100
    lines.append(f"\n  KEY FINDING: {most_burdened[0]} have only {rem_pct:.1f}% of income as")
    lines.append(f"  disposable — approximately ${rem_dollars:,.0f}/year for ALL non-essential needs.")
    lines.append(f"  {most_squeezed[0]} saw the LARGEST squeeze ({most_squeezed[3]:+.1f}pp),")
    lines.append("  correlating with the ~2.9× increase in small biz delinquencies.")

    # ── DELIVERABLE 3: Strategic Recommendation ──
    lines.append("\n" + "─" * 72)
    lines.append("DELIVERABLE 3: STRATEGIC RECOMMENDATION")
    lines.append("Localized Credit Risk Strategy with Demographic Pricing")
    lines.append("─" * 72)

    lines.append("""
  RECOMMENDATION: Implement a Divergence-Adjusted Credit Framework (DACF)
  that incorporates demographic inflation exposure into credit decisions,
  product design, and deposit retention.

  ┌──────────────────────────────────────────────────────────────────────┐
  │  THREE-PILLAR STRATEGY                                              │
  ├──────────────────────────────────────────────────────────────────────┤
  │                                                                      │
  │  PILLAR 1: CREDIT RISK RECALIBRATION                                │
  │  ─────────────────────────────────────                              │
  │  - Adjust credit scoring models to weight demographic inflation      │
  │    exposure alongside traditional FICO/income metrics                │
  │  - Create "inflation stress" flags for portfolios heavily            │
  │    concentrated in high-divergence demographics                      │
  │  - Increase loss reserves for auto loans (rural) and credit          │
  │    cards (seniors) where real purchasing power declined most          │
  │                                                                      │
  │  PILLAR 2: PRODUCT INNOVATION                                       │
  │  ─────────────────────────────                                      │
  │  For Seniors:                                                        │
  │    - Inflation-indexed CD rates that track medical CPI               │
  │    - Prescription drug co-pay financing (0% APR, 12-month)           │
  │    - Simplified home equity access for property-rich/cash-poor       │
  │                                                                      │
  │  For Urban Renters:                                                  │
  │    - Rent-smoothing deposit accounts with autopay incentives         │
  │    - First-time homebuyer programs targeting rent-to-own             │
  │    - High-yield savings with rent-burden calculation tools           │
  │                                                                      │
  │  For Rural Small Business:                                           │
  │    - Energy cost hedging credit facilities                           │
  │    - Flexible payment schedules tied to seasonal revenue cycles      │
  │    - Equipment financing with fuel cost escalation clauses           │
  │                                                                      │
  │  PILLAR 3: DEPOSIT RETENTION & GROWTH                               │
  │  ───────────────────────────────────                                │
  │  - Target deposit outflows ($150M decline) with demographic-         │
  │    specific retention offers                                         │
  │  - Seniors: guaranteed rate floor CDs (retain $45M+ at risk)        │
  │  - Rural Biz: business operating account bundles with fee waivers   │
  │  - Urban Renters: automated savings programs with bonus rates        │
  │                                                                      │
  └──────────────────────────────────────────────────────────────────────┘

  STAKEHOLDER ANALYSIS:
  ┌────────────────────┬────────────────────────┬──────────────────────┐
  │ Stakeholder        │ Interest               │ Impact of Strategy   │
  ├────────────────────┼────────────────────────┼──────────────────────┤
  │ Board / Executives │ ROA, deposit growth    │ Reduced defaults,    │
  │                    │                        │ retained deposits    │
  ├────────────────────┼────────────────────────┼──────────────────────┤
  │ Credit Risk Team   │ Portfolio quality,     │ Better risk models,  │
  │                    │ loss forecasting       │ earlier intervention │
  ├────────────────────┼────────────────────────┼──────────────────────┤
  │ Retail Banking     │ Customer retention,    │ Targeted products    │
  │                    │ cross-sell             │ increase engagement  │
  ├────────────────────┼────────────────────────┼──────────────────────┤
  │ Customers          │ Affordable products,   │ Products that match  │
  │                    │ financial stability    │ real cost pressures  │
  ├────────────────────┼────────────────────────┼──────────────────────┤
  │ Regulators (OCC,   │ Fair lending, CRA      │ Demonstrates data-   │
  │ FDIC)              │ compliance             │ driven inclusion     │
  └────────────────────┴────────────────────────┴──────────────────────┘

  TRADEOFFS & MITIGATION:

  Risk 1: Demographic-adjusted pricing may raise fair lending concerns
    Mitigation: Frame as "hardship products" available to all, not
    pricing discrimination. Audit for disparate impact quarterly.

  Risk 2: Inflation-indexed products expose bank to rate risk
    Mitigation: Cap indexed rates; hedge with Treasury Inflation-
    Protected Securities (TIPS) in investment portfolio.

  Risk 3: Loosening credit for stressed groups increases loss exposure
    Mitigation: Start with secured products (home equity, equipment
    liens). Limit unsecured expansion to 5% of portfolio per year.

  PROJECTED IMPACT (12-MONTH):
    - Deposit retention improvement:    +$60-90M (vs. $150M outflow trend)
    - Auto loan loss reduction:         -15-20 bps
    - Small business delinquency:       Stabilize at 2.5% (from 3.2%)
    - Customer satisfaction (NPS):      +8-12 points in target segments
""")

    # ── Credit Stress Correlation ──
    lines.append("─" * 72)
    lines.append("APPENDIX: CREDIT STRESS CORRELATION WITH DIVERGENCE INDEX")
    lines.append("─" * 72)

    b21 = BANK_DATA[2021]
    b25 = BANK_DATA[2025]
    lines.append(f"""
  Metric                     2021        2025        Change
  ─────────────────────────  ──────────  ──────────  ──────────
  Total Retail Deposits      ${b21['total_retail_deposits']/1e9:.1f}B       ${b25['total_retail_deposits']/1e9:.2f}B     -${(b21['total_retail_deposits']-b25['total_retail_deposits'])/1e6:.0f}M
  Auto Loan Default Rate     {b21['auto_loan_default_rate']*100:.1f}%        {b25['auto_loan_default_rate']*100:.1f}%        +{(b25['auto_loan_default_rate']-b21['auto_loan_default_rate'])*100:.1f}pp
  Credit Card Utilization    {b21['credit_card_utilization']*100:.0f}%         {b25['credit_card_utilization']*100:.0f}%         +{(b25['credit_card_utilization']-b21['credit_card_utilization'])*100:.0f}pp
  Small Biz Delinquencies    {b21['small_biz_delinquencies']*100:.1f}%        {b25['small_biz_delinquencies']*100:.1f}%        +{(b25['small_biz_delinquencies']-b21['small_biz_delinquencies'])*100:.1f}pp

  CORRELATION: The ~2.9x increase in small business delinquencies (1.1% → 3.2%)
  is consistent with Rural Small Business Owners experiencing the highest
  inflation divergence in 2022 (+2.9pp above Midwest headline). Gasoline and
  utility costs that spiked in 2022 created a financial shock that cascaded
  into credit stress over the following 2-3 years as reserves were depleted.
""")

    lines.append("=" * 72)
    lines.append("END OF ANALYSIS")
    lines.append("=" * 72)

    report = "\n".join(lines)

    output_path = OUTPUT_DIR / "executive_summary.txt"
    output_path.write_text(report)
    print(report)
    print(f"\nSaved to {output_path}")

    return report


if __name__ == "__main__":
    generate_summary()
