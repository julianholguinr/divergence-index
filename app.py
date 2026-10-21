"""Divergence Index — Interactive Dashboard.

Run:
    streamlit run app.py
"""

import sys
import io
import base64
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import WEIGHTS, BANK_DATA, MEDIAN_INCOMES, NON_DISCRETIONARY, DISCRETIONARY, CPI_SERIES

PROCESSED = Path(__file__).parent / "data" / "processed"
RAW = Path(__file__).parent / "data" / "raw"

COLORS = {
    "Fixed-Income Seniors": "#E74C3C",
    "Urban Renters": "#3498DB",
    "Rural Small Business Owners": "#27AE60",
    "headline": "#95A5A6",
}
SHORT = {
    "Fixed-Income Seniors": "Seniors",
    "Urban Renters": "Urban Renters",
    "Rural Small Business Owners": "Rural Biz",
}

NICE_CATEGORIES = {
    "food_at_home": "Groceries",
    "food_away": "Restaurants",
    "rent": "Rent",
    "owners_equiv_rent": "Home Ownership",
    "household_energy": "Home Energy",
    "gasoline": "Gasoline",
    "medical_care": "Medical Care",
    "medical_services": "Doctor Visits",
    "electricity": "Electricity",
    "utility_gas": "Natural Gas",
    "energy": "Energy (Total)",
    "recreation": "Entertainment",
    "apparel": "Clothing",
    "education_comm": "Education & Phone",
    "new_vehicles": "New Cars/Trucks",
    "used_vehicles": "Used Cars/Trucks",
    "public_transit": "Public Transit",
    "all_items": "All Items (Average)",
}

TIMELINE_EVENTS = {
    2022: [
        ("Feb 2022", "Russia invades Ukraine — global energy crisis begins"),
        ("Mar 2022", "Fed starts aggressive rate hikes (0% to 0.5%)"),
        ("Jun 2022", "Gas hits $5/gallon nationally — peak energy prices"),
    ],
    2023: [
        ("Jan 2023", "Fed rate reaches 4.5% — borrowing costs soar"),
        ("Mid 2023", "Energy prices cool down — Rural Biz gets relief"),
        ("Jul 2023", "Fed rate peaks at 5.25-5.50%"),
    ],
    2024: [
        ("Sep 2024", "Fed begins cutting rates (first cut in 4 years)"),
        ("2024", "Housing costs remain sticky — renters still squeezed"),
    ],
    2025: [
        ("2025", "Medical costs continue steady rise — seniors feel it most"),
        ("2025", "Small biz delinquencies hit 3.2% (tripled from 2021)"),
    ],
}

st.set_page_config(page_title="Divergence Index", layout="wide")

st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 1200px;}
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 10px; padding: 14px 18px;
        border: 1px solid #e9ecef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .kpi-row {display: flex; gap: 12px; margin: 12px 0 20px 0; flex-wrap: wrap;}
    .kpi-card {
        flex: 1; min-width: 180px; padding: 16px 20px; border-radius: 12px;
        border: 1px solid #e9ecef; background: #fff;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .kpi-card .label {font-size: 13px; font-weight: 600; color: #6c757d; margin-bottom: 4px;}
    .kpi-card .value {font-size: 28px; font-weight: 700; margin-bottom: 2px;}
    .kpi-card .delta {font-size: 13px; font-weight: 500;}
    .kpi-card .delta.pos {color: #E74C3C;}
    .kpi-card .delta.neg {color: #27AE60;}
    .kpi-card .delta.neutral {color: #95A5A6;}
    .stTabs [data-baseweb="tab-list"] {gap: 4px;}
    .stTabs [data-baseweb="tab"] {padding: 10px 24px; font-weight: 600; font-size: 14px;}
    h1 {font-size: 1.8rem !important;}
    .explanation {
        background: #1a1a2e; border-left: 4px solid #3498db;
        padding: 14px 18px; border-radius: 0 8px 8px 0;
        margin-bottom: 16px; font-size: 14px; line-height: 1.7;
        color: #e0e0e0; border: 1px solid #2a2a4a;
    }
    .explanation b {color: #5dade2;}
    .risk-card {
        padding: 20px; border-radius: 12px; text-align: center;
        border: 2px solid #e9ecef; background: #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .risk-card .risk-score {font-size: 48px; font-weight: 800; line-height: 1.1;}
    .risk-card .risk-label {font-size: 14px; font-weight: 600; color: #6c757d; margin-top: 4px;}
    .risk-card .risk-level {font-size: 13px; font-weight: 700; margin-top: 6px; text-transform: uppercase; letter-spacing: 1px;}
    .story-slide {
        background: #fff; border: 1px solid #e9ecef; border-radius: 12px;
        padding: 28px 32px; margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .story-slide h3 {margin-top: 0; color: #2C3E50;}
    .story-slide .slide-num {
        display: inline-block; background: #3498DB; color: white;
        border-radius: 50%; width: 28px; height: 28px; text-align: center;
        line-height: 28px; font-weight: 700; font-size: 14px; margin-right: 8px;
    }
    .data-source {
        background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px;
        padding: 10px 14px; font-size: 12px; color: #6c757d; margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    return {
        "di": pd.read_csv(PROCESSED / "divergence_index.csv"),
        "cum": pd.read_csv(PROCESSED / "cumulative_inflation.csv"),
        "burden": pd.read_csv(PROCESSED / "nondiscretionary_burden.csv"),
        "cpi_yoy": pd.read_csv(PROCESSED / "cpi_yoy_changes.csv", index_col=0),
        "cpi_raw": pd.read_csv(RAW / "cpi_annual_pivot.csv", index_col=0) if (RAW / "cpi_annual_pivot.csv").exists() else None,
    }


CHART_CONFIG = {
    "displayModeBar": True,
    "modeBarButtonsToAdd": ["resetScale2d"],
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "displaylogo": False,
    "scrollZoom": True,
    "toImageButtonOptions": {"format": "png", "width": 1200, "height": 600, "scale": 2},
}


def styled(fig, h=500):
    fig.update_layout(
        font=dict(family="Inter, sans-serif", size=13, color="black"),
        plot_bgcolor="rgba(250,250,252,1)", paper_bgcolor="white",
        height=h, margin=dict(l=55, r=20, t=30, b=50),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.95)", bordercolor="#E9ECEF", borderwidth=1,
            font=dict(size=12, color="black"),
        ),
        hovermode="x unified",
        dragmode="pan",
        modebar=dict(bgcolor="rgba(255,255,255,0.8)", color="#6c757d",
                     activecolor="#3498DB", orientation="h"),
    )
    fig.update_xaxes(gridcolor="#F0F0F0", linecolor="#CED4DA", dtick=1,
                     rangeslider=dict(visible=False), fixedrange=False,
                     tickfont=dict(color="black", size=12), title_font=dict(color="black"))
    fig.update_yaxes(gridcolor="#F0F0F0", linecolor="#CED4DA", fixedrange=False,
                     tickfont=dict(color="black", size=12), title_font=dict(color="black"))
    return fig


def add_timeline_annotations(fig, years):
    """(#5) Add key event annotations to a chart."""
    event_y_offsets = [0.95, 0.85, 0.75]
    for year in years:
        events = TIMELINE_EVENTS.get(year, [])
        for i, (label, desc) in enumerate(events[:1]):
            fig.add_vline(x=year, line_dash="dot", line_color="rgba(149,165,166,0.4)", line_width=1)
            fig.add_annotation(
                x=year, y=1.0, yref="paper", yshift=-(i * 18),
                text=f"<b>{label}</b>", showarrow=False,
                font=dict(size=9, color="#7F8C8D"),
                bgcolor="rgba(255,255,255,0.8)", borderpad=2,
            )
    return fig


def compute_risk_score(group, di_df, burden_df):
    """(#7) Compute a 1-10 credit risk score for a group."""
    scores = []
    latest = di_df[di_df["year"] == di_df["year"].max()]
    row = latest[latest["group"] == group]
    if not row.empty:
        div = abs(row.iloc[0]["divergence"])
        scores.append(min(10, div * 1.5))

    b = burden_df[(burden_df["group"] == group) & (burden_df["year"] == burden_df["year"].max())]
    if not b.empty:
        nd = b.iloc[0]["nondiscretionary_pct"]
        scores.append(min(10, (nd - 50) / 4))

    b21 = burden_df[(burden_df["group"] == group) & (burden_df["year"] == 2021)]
    if not b.empty and not b21.empty:
        shift = b.iloc[0]["nondiscretionary_pct"] - b21.iloc[0]["nondiscretionary_pct"]
        scores.append(min(10, shift * 1.2))

    cum = di_df[di_df["group"] == group]["group_inflation"]
    if len(cum) > 0:
        peak = cum.max()
        scores.append(min(10, peak / 2))

    return round(np.mean(scores), 1) if scores else 5.0


def generate_pdf_report(di_df, burden_df, cum_df):
    """(#9) Generate a text-based report for download."""
    lines = []
    lines.append("THE DIVERGENCE INDEX — Executive Report")
    lines.append(f"Generated: {datetime.now().strftime('%B %d, %Y')}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("DIVERGENCE INDEX (Year-over-Year)")
    lines.append(f"{'Year':<6} {'Group':<35} {'Inflation':>10} {'CPI':>8} {'Gap':>8}")
    lines.append("-" * 67)
    for _, r in di_df.iterrows():
        lines.append(f"{int(r['year']):<6} {r['group']:<35} {r['group_inflation']:>+9.1f}% {r['headline_cpi']:>+7.1f}% {r['divergence']:>+7.1f}pp")
    lines.append("")
    lines.append("CUMULATIVE INFLATION (since 2021)")
    for _, r in cum_df[cum_df["year"] == 2025].iterrows():
        lines.append(f"  {r['group']:<35} {r['cumulative_inflation']:>+.1f}%")
    lines.append("")
    lines.append("NON-DISCRETIONARY BURDEN")
    lines.append(f"{'Group':<35} {'2021':>8} {'2025':>8} {'Shift':>8}")
    lines.append("-" * 59)
    for group in WEIGHTS:
        g21 = burden_df[(burden_df["group"] == group) & (burden_df["year"] == 2021)]
        g25 = burden_df[(burden_df["group"] == group) & (burden_df["year"] == 2025)]
        if not g21.empty and not g25.empty:
            v21 = g21.iloc[0]["nondiscretionary_pct"]
            v25 = g25.iloc[0]["nondiscretionary_pct"]
            lines.append(f"  {group:<35} {v21:>7.1f}% {v25:>7.1f}% {v25-v21:>+7.1f}pp")
    lines.append("")
    lines.append("RISK SCORES")
    for group in WEIGHTS:
        score = compute_risk_score(group, di_df, burden_df)
        lines.append(f"  {group:<35} {score}/10")
    lines.append("")
    lines.append("BANK STRESS INDICATORS")
    b21, b25 = BANK_DATA[2021], BANK_DATA[2025]
    lines.append(f"  Deposits: ${b21['total_retail_deposits']/1e9:.1f}B -> ${b25['total_retail_deposits']/1e9:.2f}B (-${(b21['total_retail_deposits']-b25['total_retail_deposits'])/1e6:.0f}M)")
    lines.append(f"  Auto defaults: {b21['auto_loan_default_rate']*100:.1f}% -> {b25['auto_loan_default_rate']*100:.1f}%")
    lines.append(f"  Card utilization: {b21['credit_card_utilization']*100:.0f}% -> {b25['credit_card_utilization']*100:.0f}%")
    lines.append(f"  Biz delinquencies: {b21['small_biz_delinquencies']*100:.1f}% -> {b25['small_biz_delinquencies']*100:.1f}%")
    lines.append("")
    lines.append("Data sources: BLS CPI (CUSR0000SA*), FRED, BLS CEX, ACS")
    return "\n".join(lines)


# ── Load data ──
data = load_data()
di, cum, burden = data["di"], data["cum"], data["burden"]

# ── Sidebar ──
with st.sidebar:
    st.markdown("### Settings")

    st.markdown("**Which groups to show:**")
    show_seniors = st.toggle("Seniors (65+, fixed income)", value=True)
    show_renters = st.toggle("Urban Renters (young workers)", value=True)
    show_rural = st.toggle("Rural Small Business Owners", value=True)

    selected_groups = []
    if show_seniors:
        selected_groups.append("Fixed-Income Seniors")
    if show_renters:
        selected_groups.append("Urban Renters")
    if show_rural:
        selected_groups.append("Rural Small Business Owners")

    st.divider()
    st.markdown("**Time period:**")
    start_yr, end_yr = st.select_slider(
        "Years", options=[2021, 2022, 2023, 2024, 2025],
        value=(2021, 2025), label_visibility="collapsed",
    )

    st.divider()
    show_headline = st.toggle("Show average CPI line", value=True,
                              help="The gray dashed line = the government's 'average' inflation")
    show_explanations = st.toggle("Show explanations", value=True,
                                  help="Toggle the blue explanation boxes on/off")
    show_events = st.toggle("Show timeline events", value=True,
                            help="Annotate charts with key economic events")

    st.divider()
    # (#9) PDF Export
    st.markdown("**Export:**")
    report_text = generate_pdf_report(di, burden, cum)
    st.download_button(
        "Download Report (.txt)",
        data=report_text,
        file_name="divergence_index_report.txt",
        mime="text/plain",
    )

    st.divider()
    # (#10) Data freshness
    raw_file = RAW / "cpi_annual_pivot.csv"
    if raw_file.exists():
        mod_time = datetime.fromtimestamp(raw_file.stat().st_mtime)
        st.caption(f"Data last pulled: {mod_time.strftime('%b %d, %Y %I:%M %p')}")
    st.caption("Sources: BLS CPI (CUSR0000SA*), FRED, BLS CEX")
    st.caption("Period: 2021 - 2025 | US City Average")

if not selected_groups:
    st.warning("Turn on at least one group in the sidebar to see data.")
    st.stop()

# Filter
di_f = di[(di["group"].isin(selected_groups)) & (di["year"].between(start_yr, end_yr))]
cum_f = cum[(cum["group"].isin(selected_groups)) & (cum["year"].between(start_yr, end_yr))]
burden_f = burden[(burden["group"].isin(selected_groups)) & (burden["year"].between(start_yr, end_yr))]

# ── Header ──
st.markdown("# The Divergence Index")
st.markdown("*How inflation hits different people differently — and what a bank should do about it*")

# ── KPI cards ──
latest_yr = di_f["year"].max()
cards_html = '<div class="kpi-row">'
for group in selected_groups:
    row = di_f[(di_f["group"] == group) & (di_f["year"] == latest_yr)]
    if not row.empty:
        r = row.iloc[0]
        color = COLORS[group]
        div = r["divergence"]
        delta_class = "pos" if div > 0 else "neg" if div < 0 else "neutral"
        cards_html += f'''
        <div class="kpi-card" style="border-left: 4px solid {color};">
            <div class="label">{SHORT[group]}</div>
            <div class="value" style="color: {color};">{r["group_inflation"]:+.1f}%</div>
            <div class="delta {delta_class}">{div:+.1f}pp vs official CPI</div>
        </div>'''
hl_row = di_f[di_f["year"] == latest_yr].iloc[0] if not di_f.empty else None
if hl_row is not None:
    cards_html += f'''
    <div class="kpi-card" style="border-left: 4px solid #95A5A6;">
        <div class="label">Official CPI ({int(latest_yr)})</div>
        <div class="value" style="color: #95A5A6;">{hl_row["headline_cpi"]:+.1f}%</div>
        <div class="delta neutral">government average</div>
    </div>'''
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)

# ── Tabs ──
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Inflation by Group",
    "Who Pays More?",
    "Spending Weights",
    "Spending Squeeze",
    "What-If Simulator",
    "Risk Scores",
    "Bank Impact",
    "Story Mode",
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — INFLATION BY GROUP
# ════════════════════════════════════════════════════════════════
with tab1:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "The government measures inflation with one number (CPI) — but a retiree spending 26% on medical bills, "
            "a renter paying 28% on housing, and a farmer burning through diesel don't experience the same price increases. "
            "This dashboard calculates a <b>personalized inflation rate</b> for three demographic groups "
            "using real BLS price data, then connects the gap to <b>credit stress</b> at a regional Midwest bank. "
            "Each colored line below is a group's real inflation. The gray dashed line is the official average. "
            "Above the gray line = paying more than average."
            "</div>", unsafe_allow_html=True,
        )

    view = st.radio("View", ["Year by year", "Total since 2021"],
                    horizontal=True, label_visibility="collapsed")

    if view == "Year by year":
        fig = go.Figure()
        if show_headline and not di_f.empty:
            hl = di_f.drop_duplicates("year")[["year", "headline_cpi"]].dropna()
            fig.add_trace(go.Scatter(
                x=hl["year"], y=hl["headline_cpi"],
                mode="lines+markers", name="Official CPI (avg)",
                line=dict(color=COLORS["headline"], width=2, dash="dash"), marker=dict(size=6),
            ))
        for group in selected_groups:
            gdf = di_f[di_f["group"] == group]
            fig.add_trace(go.Scatter(
                x=gdf["year"], y=gdf["group_inflation"],
                mode="lines+markers+text", name=SHORT[group],
                line=dict(color=COLORS[group], width=3),
                marker=dict(size=10, symbol="diamond"),
                text=[f"{v:+.1f}%" for v in gdf["group_inflation"]],
                textposition="top center", textfont=dict(size=11, color=COLORS[group]),
                hovertemplate="%{y:+.1f}%<extra>" + SHORT[group] + "</extra>",
            ))
        if show_events:
            add_timeline_annotations(fig, range(start_yr, end_yr + 1))
        fig = styled(fig, h=480)
        fig.update_yaxes(title_text="Inflation rate (%)", ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    else:
        fig = go.Figure()
        for group in selected_groups:
            gdf = cum_f[cum_f["group"] == group]
            r, g, b = int(COLORS[group][1:3], 16), int(COLORS[group][3:5], 16), int(COLORS[group][5:7], 16)
            fig.add_trace(go.Scatter(
                x=gdf["year"], y=gdf["cumulative_inflation"],
                mode="lines+markers+text", name=SHORT[group],
                line=dict(color=COLORS[group], width=3), marker=dict(size=9),
                fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.07)",
                text=[f"{v:+.1f}%" if v != 0 else "" for v in gdf["cumulative_inflation"]],
                textposition="top center", textfont=dict(size=11),
                hovertemplate="%{y:+.1f}% total<extra>" + SHORT[group] + "</extra>",
            ))
        if show_events:
            add_timeline_annotations(fig, range(start_yr, end_yr + 1))
        fig = styled(fig, h=480)
        fig.update_yaxes(title_text="Total price increase since 2021 (%)", ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    # (#4) Dollar impact calculator
    st.divider()
    st.markdown("#### Dollar Impact Calculator")
    if show_explanations:
        st.caption("See exactly how many extra dollars each group needs to buy the same things as 2021.")
    dollar_html = '<div class="kpi-row">'
    for group in selected_groups:
        base_income = MEDIAN_INCOMES[group][2021]
        c_row = cum_f[(cum_f["group"] == group) & (cum_f["year"] == cum_f["year"].max())]
        if not c_row.empty:
            cum_inf = c_row.iloc[0]["cumulative_inflation"]
            cost_now = base_income * (1 + cum_inf / 100)
            extra = cost_now - base_income
            color = COLORS[group]
            dollar_html += f'''
            <div class="kpi-card" style="border-left: 4px solid {color};">
                <div class="label">{SHORT[group]}</div>
                <div class="value" style="color: {color}; font-size:22px;">${cost_now:,.0f}</div>
                <div class="delta neutral">needed in {int(cum_f["year"].max())} to buy what ${base_income:,} bought in 2021</div>
                <div class="delta pos" style="margin-top:4px;">+${extra:,.0f} extra per year</div>
            </div>'''
    dollar_html += '</div>'
    st.markdown(dollar_html, unsafe_allow_html=True)

    # (#10) Data source
    st.markdown('<div class="data-source">Source: BLS CPI-U, US City Average, Seasonally Adjusted (CUSR0000SA*) | 2021-2025 annual averages</div>', unsafe_allow_html=True)

    with st.expander("See the numbers in a table"):
        display_df = di_f[["year", "group", "group_inflation", "headline_cpi", "divergence"]].copy()
        display_df.columns = ["Year", "Group", "Their Inflation (%)", "Official CPI (%)", "Gap (pp)"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 — WHO PAYS MORE (+ #2 Heatmap)
# ════════════════════════════════════════════════════════════════
with tab2:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> The bars show how much MORE or LESS each group paid "
            "compared to the official CPI. A bar going UP = hit harder than average. "
            "The heatmap below reveals exactly WHICH categories drove the difference."
            "</div>", unsafe_allow_html=True,
        )

    fig = go.Figure()
    fig.add_hline(y=0, line_dash="solid", line_color="#CED4DA", line_width=1.5)
    for group in selected_groups:
        gdf = di_f[di_f["group"] == group]
        fig.add_trace(go.Bar(
            x=gdf["year"], y=gdf["divergence"],
            name=SHORT[group], marker_color=COLORS[group], opacity=0.9,
            text=[f"{v:+.1f}" for v in gdf["divergence"]],
            textposition="outside", textfont=dict(size=12),
            hovertemplate="<b>%{x}</b><br>%{y:+.1f}pp vs CPI<extra>" + SHORT[group] + "</extra>",
        ))
    fig.update_layout(barmode="group")
    if show_events:
        add_timeline_annotations(fig, range(start_yr, end_yr + 1))
    fig = styled(fig, h=450)
    fig.update_yaxes(title_text="Difference from official CPI (pp)", zeroline=True)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    # (#2) Heatmap — Weight x Price Change = Impact
    st.divider()
    st.markdown("#### Category Impact Heatmap")
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>How to read this:</b> Each cell = (how much the group spends on that category) x "
            "(how much that category's price changed). The number in each cell is how many "
            "percentage points that single category added to the group's inflation. "
            "<b>Darker red = bigger pain point. Green = prices fell, saving them money.</b>"
            "</div>", unsafe_allow_html=True,
        )
    heatmap_year = st.select_slider("Year", options=sorted(di_f["year"].unique()),
                                     value=int(di_f["year"].max()), key="hm_yr")
    cpi_yoy = data["cpi_yoy"]
    if heatmap_year in cpi_yoy.index:
        cats = [c for c in cpi_yoy.columns if c != "all_items"]
        groups_for_hm = selected_groups
        z_values = []
        hover_text = []
        annotation_text = []
        for group in groups_for_hm:
            row_vals = []
            row_hover = []
            row_annot = []
            for cat in cats:
                weight = WEIGHTS[group].get(cat, 0)
                price_chg = cpi_yoy.loc[heatmap_year, cat] if cat in cpi_yoy.columns else 0
                impact = weight * price_chg
                row_vals.append(round(impact, 2))
                nice = NICE_CATEGORIES.get(cat, cat)
                row_hover.append(f"<b>{nice}</b><br>Spend weight: {weight:.0%}<br>Price change: {price_chg:+.1f}%<br>Impact: {impact:+.2f}pp")
                if abs(impact) >= 0.15:
                    row_annot.append(f"{impact:+.1f}")
                elif abs(impact) >= 0.05:
                    row_annot.append(f"{impact:+.2f}")
                else:
                    row_annot.append("")
            z_values.append(row_vals)
            hover_text.append(row_hover)
            annotation_text.append(row_annot)

        x_labels = [NICE_CATEGORIES.get(c, c) for c in cats]
        y_labels = [SHORT[g] for g in groups_for_hm]

        fig_hm = go.Figure(data=go.Heatmap(
            z=z_values, x=x_labels, y=y_labels,
            hovertext=hover_text, hoverinfo="text",
            colorscale=[[0, "#2ECC71"], [0.35, "#FDFEFE"], [0.5, "#FEF9E7"], [0.75, "#F5B041"], [1, "#E74C3C"]],
            zmid=0, colorbar=dict(title="Impact (pp)", ticksuffix="pp"),
            showscale=True,
        ))

        for i, group in enumerate(groups_for_hm):
            for j, cat in enumerate(cats):
                txt = annotation_text[i][j]
                if txt:
                    val = z_values[i][j]
                    font_color = "white" if abs(val) > 1.0 else "#333"
                    fig_hm.add_annotation(
                        x=x_labels[j], y=y_labels[i], text=txt,
                        showarrow=False, font=dict(size=10, color=font_color, family="Inter, sans-serif"),
                    )

        fig_hm.update_layout(
            height=max(280, 160 + len(groups_for_hm) * 70),
            margin=dict(l=120, r=20, t=10, b=140),
            font=dict(size=12, family="Inter, sans-serif"), paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(tickangle=-45, side="bottom", tickfont=dict(size=13, color="black", family="Inter, sans-serif")),
            yaxis=dict(autorange="reversed", tickfont=dict(size=14, color="black", family="Inter, sans-serif")),
        )
        st.plotly_chart(fig_hm, use_container_width=True, config=CHART_CONFIG)

        # Find top 3 pain points for this year
        all_impacts = []
        for group in groups_for_hm:
            for cat in cats:
                weight = WEIGHTS[group].get(cat, 0)
                price_chg = cpi_yoy.loc[heatmap_year, cat] if cat in cpi_yoy.columns else 0
                impact = weight * price_chg
                all_impacts.append((SHORT[group], NICE_CATEGORIES.get(cat, cat), impact, weight * 100, price_chg))
        all_impacts.sort(key=lambda x: x[2], reverse=True)
        top3 = all_impacts[:3]
        st.markdown(f"**Top 3 pain points in {heatmap_year}:**")
        for rank, (grp, cat, imp, wt, pchg) in enumerate(top3, 1):
            st.markdown(f"{rank}. **{grp}** — {cat}: spends {wt:.0f}% of budget, price changed {pchg:+.1f}%, adding **{imp:+.2f}pp** to their inflation")

    st.markdown('<div class="data-source">Impact = (group spending weight) x (category price change). Each cell shows how many percentage points one category contributes to a group\'s total inflation.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 3 — SPENDING WEIGHTS (#6 Donut Charts)
# ════════════════════════════════════════════════════════════════
with tab3:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> These donuts show how each group spends their money. "
            "The bigger a slice, the more of their budget goes to that category. "
            "This is WHY different groups experience different inflation — they buy different things."
            "</div>", unsafe_allow_html=True,
        )

    donut_cols = st.columns(len(selected_groups))
    for i, group in enumerate(selected_groups):
        with donut_cols[i]:
            weights = WEIGHTS[group]
            cats = sorted(weights.keys(), key=lambda c: weights[c], reverse=True)
            vals = [weights[c] * 100 for c in cats]
            labels = [NICE_CATEGORIES.get(c, c) for c in cats]
            cat_colors = ["#E74C3C" if c in NON_DISCRETIONARY else "#F39C12" if c in DISCRETIONARY else "#BDC3C7" for c in cats]

            fig_d = go.Figure(data=[go.Pie(
                labels=labels, values=vals,
                hole=0.45, marker=dict(colors=cat_colors, line=dict(color="white", width=2)),
                textinfo="label+percent", textposition="auto",
                insidetextfont=dict(size=9, color="white"),
                outsidetextfont=dict(size=9, color="black"),
                hovertemplate="<b>%{label}</b><br>%{value:.1f}% of spending<extra></extra>",
                sort=False,
            )])
            fig_d.update_layout(
                height=420, margin=dict(l=40, r=40, t=40, b=40),
                title=dict(text=SHORT[group], font=dict(size=15, color=COLORS[group]), x=0.5),
                showlegend=False, paper_bgcolor="white",
                uniformtext=dict(minsize=8, mode="hide"),
                annotations=[dict(text=f"<b>{sum(v for c, v in zip(cats, vals) if c in NON_DISCRETIONARY):.0f}%</b><br>essentials",
                                  x=0.5, y=0.5, font=dict(size=13, color="#E74C3C"), showarrow=False)],
            )
            st.plotly_chart(fig_d, use_container_width=True, config=CHART_CONFIG)

    st.caption("Red = must-pay (non-discretionary) | Orange = optional (discretionary)")
    st.markdown('<div class="data-source">Weights based on BLS Consumer Expenditure Survey (CEX), Tables 1300 (age) and 3100 (housing tenure), with regional adjustments for Indiana/Midwest.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 — SPENDING SQUEEZE
# ════════════════════════════════════════════════════════════════
with tab4:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> This shows what percentage of each group's income goes to "
            "things they MUST pay for. The higher the line, the less money left for anything else. "
            "Above the red 80% line = serious financial stress."
            "</div>", unsafe_allow_html=True,
        )

    fig = go.Figure()
    for group in selected_groups:
        gdf = burden_f[burden_f["group"] == group]
        fig.add_trace(go.Scatter(
            x=gdf["year"], y=gdf["nondiscretionary_pct"],
            mode="lines+markers+text", name=SHORT[group],
            line=dict(color=COLORS[group], width=3), marker=dict(size=10),
            text=[f"{v:.0f}%" for v in gdf["nondiscretionary_pct"]],
            textposition="top center", textfont=dict(size=11, color=COLORS[group]),
            hovertemplate="%{y:.1f}% of income<extra>" + SHORT[group] + "</extra>",
        ))
    fig.add_hline(y=80, line_dash="dot", line_color="#E74C3C", line_width=2,
                  annotation_text="Danger zone (80%+)", annotation_position="bottom right",
                  annotation_font=dict(size=11, color="#E74C3C"))
    fig.add_hrect(y0=80, y1=95, fillcolor="rgba(231,76,60,0.04)", line_width=0)
    if show_events:
        add_timeline_annotations(fig, range(start_yr, end_yr + 1))
    fig = styled(fig, h=500)
    fig.update_yaxes(title_text="% of income spent on essentials", range=[50, 92], ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.divider()
    st.markdown("#### What's left after paying for essentials?")

    money_html = '<div class="kpi-row">'
    for group in selected_groups:
        g25 = burden_f[(burden_f["group"] == group) & (burden_f["year"] == burden_f["year"].max())]
        g21 = burden[(burden["group"] == group) & (burden["year"] == 2021)]
        if not g25.empty and not g21.empty:
            r25 = g25.iloc[0]
            r21 = g21.iloc[0]
            remaining_pct = 100 - r25["nondiscretionary_pct"]
            remaining_dollars = r25["income"] * remaining_pct / 100
            shift = r25["nondiscretionary_pct"] - r21["nondiscretionary_pct"]
            color = COLORS[group]
            money_html += f'''
            <div class="kpi-card" style="border-left: 4px solid {color};">
                <div class="label">{SHORT[group]}</div>
                <div class="value" style="color: {color};">${remaining_dollars:,.0f}/yr</div>
                <div class="delta neutral">{remaining_pct:.0f}% of income left after essentials</div>
                <div class="delta pos" style="margin-top:4px;">burden +{shift:.1f}pp since 2021</div>
            </div>'''
    money_html += '</div>'
    st.markdown(money_html, unsafe_allow_html=True)

    if show_explanations:
        st.divider()
        compare_yr = st.radio("Compare 2021 to:", [2025, 2024, 2023, 2022], horizontal=True)
        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=["2021 — Where each dollar went", f"{compare_yr} — Where each dollar goes now"],
                            shared_yaxes=True)
        names = [SHORT[g] for g in selected_groups]
        for col_idx, yr in enumerate([2021, compare_yr], 1):
            ydf = burden[burden["year"] == yr]
            nd = [ydf[ydf["group"] == g]["nondiscretionary_pct"].values[0] if len(ydf[ydf["group"] == g]) else 0 for g in selected_groups]
            d = [ydf[ydf["group"] == g]["discretionary_pct"].values[0] if len(ydf[ydf["group"] == g]) else 0 for g in selected_groups]
            rem = [max(0, 100 - n - dv) for n, dv in zip(nd, d)]
            fig.add_trace(go.Bar(x=names, y=nd, name="Must-pay" if col_idx == 1 else None,
                                 marker_color="#E74C3C", opacity=0.85, showlegend=(col_idx == 1), legendgroup="nd",
                                 text=[f"{v:.0f}%" for v in nd], textposition="inside", textfont=dict(color="white", size=12),
                                 ), row=1, col=col_idx)
            fig.add_trace(go.Bar(x=names, y=d, name="Optional" if col_idx == 1 else None,
                                 marker_color="#F39C12", opacity=0.85, showlegend=(col_idx == 1), legendgroup="d",
                                 text=[f"{v:.0f}%" for v in d], textposition="inside", textfont=dict(color="white", size=11),
                                 ), row=1, col=col_idx)
            fig.add_trace(go.Bar(x=names, y=rem, name="Savings" if col_idx == 1 else None,
                                 marker_color="#2ECC71", opacity=0.85, showlegend=(col_idx == 1), legendgroup="r",
                                 text=[f"{v:.0f}%" for v in rem], textposition="inside", textfont=dict(color="white", size=11),
                                 ), row=1, col=col_idx)
        fig.update_layout(barmode="stack")
        fig = styled(fig, h=460)
        fig.update_yaxes(title_text="% of income", ticksuffix="%", row=1, col=1)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown('<div class="data-source">Income: ACS estimates for Indiana | Burden: BLS CEX spending weights applied to CPI price changes</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 5 — WHAT-IF SIMULATOR (#3)
# ════════════════════════════════════════════════════════════════
with tab5:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> Drag the sliders to simulate different price scenarios. "
            "See how each group's inflation rate changes in real time based on which prices go up or down. "
            "This shows WHY the same price change affects groups differently."
            "</div>", unsafe_allow_html=True,
        )

    st.markdown("#### Adjust prices and see who gets hurt")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sim_gas = st.slider("Gasoline price change (%)", -20, 40, 10, key="sim_gas")
        sim_energy = st.slider("Energy price change (%)", -15, 30, 8, key="sim_energy")
    with sc2:
        sim_rent = st.slider("Rent price change (%)", -5, 20, 5, key="sim_rent")
        sim_food = st.slider("Grocery price change (%)", -5, 15, 3, key="sim_food")
    with sc3:
        sim_medical = st.slider("Medical care change (%)", -5, 20, 5, key="sim_med")
        sim_other = st.slider("All other categories (%)", -5, 10, 2, key="sim_other")

    sim_changes = {
        "gasoline": sim_gas, "energy": sim_energy, "rent": sim_rent,
        "food_at_home": sim_food, "medical_care": sim_medical, "medical_services": sim_medical,
        "owners_equiv_rent": sim_rent * 0.6, "household_energy": sim_energy * 0.8,
        "electricity": sim_energy * 0.7, "utility_gas": sim_energy * 0.9,
        "food_away": sim_food * 0.8, "recreation": sim_other, "apparel": sim_other,
        "education_comm": sim_other, "new_vehicles": sim_other, "used_vehicles": sim_other,
        "public_transit": sim_other,
    }

    sim_results = {}
    headline_sim = sum(sim_changes.get(cat, sim_other) * (1 / len(WEIGHTS[list(WEIGHTS.keys())[0]])) for cat in sim_changes) / len(sim_changes) * len(WEIGHTS[list(WEIGHTS.keys())[0]])

    for group in WEIGHTS:
        total = 0
        for cat, weight in WEIGHTS[group].items():
            chg = sim_changes.get(cat, sim_other)
            total += weight * chg
        sim_results[group] = round(total, 1)

    avg_sim = round(np.mean(list(sim_results.values())), 1)

    sim_html = '<div class="kpi-row">'
    for group in selected_groups:
        color = COLORS[group]
        val = sim_results[group]
        diff = val - avg_sim
        sim_html += f'''
        <div class="kpi-card" style="border-left: 4px solid {color};">
            <div class="label">{SHORT[group]}</div>
            <div class="value" style="color: {color};">{val:+.1f}%</div>
            <div class="delta {"pos" if diff > 0 else "neg" if diff < 0 else "neutral"}">{diff:+.1f}pp vs group average ({avg_sim:+.1f}%)</div>
        </div>'''
    sim_html += '</div>'
    st.markdown(sim_html, unsafe_allow_html=True)

    fig_sim = go.Figure()
    for group in selected_groups:
        fig_sim.add_trace(go.Bar(
            x=[SHORT[group]], y=[sim_results[group]],
            marker_color=COLORS[group], opacity=0.9, name=SHORT[group],
            text=[f"{sim_results[group]:+.1f}%"], textposition="outside", textfont=dict(size=14),
        ))
    fig_sim.add_hline(y=avg_sim, line_dash="dash", line_color="#95A5A6",
                      annotation_text=f"Average: {avg_sim:+.1f}%",
                      annotation_position="top right")
    fig_sim = styled(fig_sim, h=380)
    fig_sim.update_yaxes(title_text="Simulated inflation (%)", ticksuffix="%")
    fig_sim.update_layout(showlegend=False)
    st.plotly_chart(fig_sim, use_container_width=True, config=CHART_CONFIG)

    if show_explanations:
        st.info("Try cranking gasoline to +30% — watch how Rural Biz jumps way above the others. "
                "Or push medical to +15% and see Seniors get hit hardest. That's the Divergence Index in action.")

# ════════════════════════════════════════════════════════════════
# TAB 6 — RISK SCORES (#7)
# ════════════════════════════════════════════════════════════════
with tab6:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> A simple 1-10 credit risk score for each group, "
            "combining their inflation divergence, spending burden, burden shift, and peak inflation. "
            "Higher = more credit risk for the bank. This is what a loan officer could use at a glance."
            "</div>", unsafe_allow_html=True,
        )

    risk_cols = st.columns(len(selected_groups))
    for i, group in enumerate(selected_groups):
        score = compute_risk_score(group, di, burden)
        color = COLORS[group]
        if score >= 7:
            level, level_color = "HIGH RISK", "#E74C3C"
        elif score >= 4.5:
            level, level_color = "MODERATE", "#F39C12"
        else:
            level, level_color = "LOW RISK", "#27AE60"

        with risk_cols[i]:
            st.markdown(f'''
            <div class="risk-card" style="border-color: {color};">
                <div class="risk-score" style="color: {level_color};">{score}</div>
                <div class="risk-label">{SHORT[group]}</div>
                <div class="risk-level" style="color: {level_color};">{level}</div>
            </div>''', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### How the score is calculated")
    score_df_rows = []
    for group in selected_groups:
        latest = di[di["year"] == di["year"].max()]
        row = latest[latest["group"] == group]
        b_latest = burden[(burden["group"] == group) & (burden["year"] == burden["year"].max())]
        b21 = burden[(burden["group"] == group) & (burden["year"] == 2021)]

        divergence = abs(row.iloc[0]["divergence"]) if not row.empty else 0
        nd_pct = b_latest.iloc[0]["nondiscretionary_pct"] if not b_latest.empty else 0
        shift = (b_latest.iloc[0]["nondiscretionary_pct"] - b21.iloc[0]["nondiscretionary_pct"]) if (not b_latest.empty and not b21.empty) else 0
        peak = di[di["group"] == group]["group_inflation"].max()

        score_df_rows.append({
            "Group": SHORT[group],
            "Divergence (|gap|)": f"{divergence:.1f}pp",
            "Burden Level": f"{nd_pct:.1f}%",
            "Burden Shift": f"+{shift:.1f}pp",
            "Peak Inflation": f"{peak:+.1f}%",
            "Final Score": f"{compute_risk_score(group, di, burden)}/10",
        })
    st.dataframe(pd.DataFrame(score_df_rows), use_container_width=True, hide_index=True)

    st.markdown('<div class="data-source">Score = average of: divergence impact (x1.5), burden severity ((burden-50)/4), burden shift (x1.2), peak exposure (peak/2). Capped at 10.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 7 — BANK IMPACT
# ════════════════════════════════════════════════════════════════
with tab7:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> When people get squeezed by inflation, they pull savings, "
            "max out credit cards, and miss loan payments. This tab shows the bank's data proving that."
            "</div>", unsafe_allow_html=True,
        )

    b21, b25 = BANK_DATA[2021], BANK_DATA[2025]

    st.markdown("#### Bank Health: 2021 vs 2025")
    deposit_drop = (b21["total_retail_deposits"] - b25["total_retail_deposits"]) / 1e6
    bank_html = f'''
    <div class="kpi-row">
        <div class="kpi-card" style="border-left: 4px solid #E67E22;">
            <div class="label">Deposits Lost</div>
            <div class="value" style="color: #E67E22;">-${deposit_drop:.0f}M</div>
            <div class="delta neutral">customers withdrew savings</div>
        </div>
        <div class="kpi-card" style="border-left: 4px solid #E74C3C;">
            <div class="label">Auto Loan Defaults</div>
            <div class="value" style="color: #E74C3C;">{b21["auto_loan_default_rate"]*100:.1f}% &rarr; {b25["auto_loan_default_rate"]*100:.1f}%</div>
            <div class="delta pos">+{(b25["auto_loan_default_rate"]-b21["auto_loan_default_rate"])*100:.1f}pp increase</div>
        </div>
        <div class="kpi-card" style="border-left: 4px solid #3498DB;">
            <div class="label">Credit Card Usage</div>
            <div class="value" style="color: #3498DB;">{b21["credit_card_utilization"]*100:.0f}% &rarr; {b25["credit_card_utilization"]*100:.0f}%</div>
            <div class="delta pos">+{(b25["credit_card_utilization"]-b21["credit_card_utilization"])*100:.0f}pp — maxing out</div>
        </div>
        <div class="kpi-card" style="border-left: 4px solid #9B59B6;">
            <div class="label">Small Biz Late Payments</div>
            <div class="value" style="color: #9B59B6;">{b21["small_biz_delinquencies"]*100:.1f}% &rarr; {b25["small_biz_delinquencies"]*100:.1f}%</div>
            <div class="delta pos">tripled (3x increase)</div>
        </div>
    </div>'''
    st.markdown(bank_html, unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure()
        categories = ["Auto Loan\nDefault Rate", "Credit Card\nUtilization", "Small Biz\nDelinquencies"]
        vals_21 = [b21["auto_loan_default_rate"]*100, b21["credit_card_utilization"]*100, b21["small_biz_delinquencies"]*100]
        vals_25 = [b25["auto_loan_default_rate"]*100, b25["credit_card_utilization"]*100, b25["small_biz_delinquencies"]*100]
        fig.add_trace(go.Bar(x=categories, y=vals_21, name="2021", marker_color="#3498DB", opacity=0.8,
                             text=[f"{v:.1f}%" for v in vals_21], textposition="outside", textfont=dict(size=13)))
        fig.add_trace(go.Bar(x=categories, y=vals_25, name="2025", marker_color="#E74C3C", opacity=0.8,
                             text=[f"{v:.1f}%" for v in vals_25], textposition="outside", textfont=dict(size=13)))
        fig.update_layout(barmode="group")
        fig = styled(fig, h=420)
        fig.update_yaxes(title_text="Rate (%)", ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with c2:
        st.markdown("#### The Connection")
        st.markdown("""
        **Inflation squeeze** --> **Credit stress**

        1. Energy prices spiked in 2022
        2. Rural businesses burned through cash
        3. Small biz delinquencies **tripled**
        4. Customers pulled **$150M** from deposits
        5. Card utilization: 29% to 41%

        The bank needs a **demographic-aware strategy**.
        """)

    if show_explanations:
        st.divider()
        with st.expander("What should the bank do? (Strategic Recommendation)"):
            st.markdown("""
            ### Divergence-Adjusted Credit Framework (DACF)

            **Pillar 1 — Fix the risk models**
            - Add demographic inflation exposure to credit scoring
            - Flag portfolios concentrated in high-stress groups

            **Pillar 2 — Create products that match real needs**

            | Group | Their Problem | Product Solution |
            |-------|--------------|-----------------|
            | **Seniors** | Medical = 26% of spending | Inflation-indexed CDs; prescription financing |
            | **Renters** | Rent = 28% of spending | Rent-smoothing accounts; homebuyer programs |
            | **Rural Biz** | Energy costs doubled | Energy hedging; seasonal payment schedules |

            **Pillar 3 — Stop the deposit bleeding ($150M lost)**
            - Seniors: guaranteed-rate CDs
            - Rural Biz: fee-waiver operating accounts
            - Renters: high-yield savings with autopay bonuses

            **Projected 12-month impact:**
            - Recover $60-90M in deposits
            - Cut auto loan losses by 15-20 bps
            - Stabilize biz delinquencies at 2.5%
            """)

    st.markdown(f'<div class="data-source">Bank data from case document (hypothetical). Credit stress metrics: 2021 vs 2025.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 8 — STORY MODE (#1)
# ════════════════════════════════════════════════════════════════
with tab8:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>Presentation mode.</b> Walk through the analysis step by step. "
            "Use the slider below to advance through each slide."
            "</div>", unsafe_allow_html=True,
        )

    slide = st.slider("Slide", 1, 7, 1, key="story_slide")

    if slide == 1:
        st.markdown('''
        <div class="story-slide">
            <span class="slide-num">1</span> <b style="font-size:18px;">The Problem: One Number Can't Describe Everyone</b>
            <hr style="margin:12px 0;">
            <p style="font-size:16px; line-height:1.7;">
            The government says inflation was <b>+8.0% in 2022</b>. But that's an <i>average</i>
            across all Americans. A 70-year-old retiree spending 26% of their income on medical care
            experiences a completely different inflation rate than a 25-year-old renter spending 28% on rent.
            </p>
            <p style="font-size:16px; line-height:1.7;">
            <b>The Divergence Index</b> calculates a personalized inflation rate for each demographic group,
            revealing who the "average" is hiding.
            </p>
        </div>''', unsafe_allow_html=True)

    elif slide == 2:
        st.markdown('''
        <div class="story-slide">
            <span class="slide-num">2</span> <b style="font-size:18px;">Three Groups, Three Realities</b>
            <hr style="margin:12px 0;">
        </div>''', unsafe_allow_html=True)
        g_cols = st.columns(3)
        for i, (group, details) in enumerate([
            ("Fixed-Income Seniors", "Median income: $37K | Top expense: Medical care (26%) | Home all day = high energy bills"),
            ("Urban Renters", "Median income: $48K | Top expense: Rent (28%) | Young professionals, student loans"),
            ("Rural Small Business Owners", "Median income: $60.5K | Top expenses: Gas (12%) + Energy (12%) | Equipment, trucks, diesel"),
        ]):
            with g_cols[i]:
                st.markdown(f'<div class="kpi-card" style="border-left:4px solid {COLORS[group]};"><div class="label" style="color:{COLORS[group]}; font-size:15px;">{SHORT[group]}</div><p style="margin-top:8px; font-size:13px; line-height:1.6;">{details}</p></div>', unsafe_allow_html=True)

    elif slide == 3:
        st.markdown('''
        <div class="story-slide">
            <span class="slide-num">3</span> <b style="font-size:18px;">2022: The Year Everything Diverged</b>
            <hr style="margin:12px 0;">
            <p style="font-size:16px;">Russia invaded Ukraine. Gas hit $5/gallon. Energy prices exploded.</p>
        </div>''', unsafe_allow_html=True)
        fig = go.Figure()
        hl = di.drop_duplicates("year")[["year", "headline_cpi"]].dropna()
        fig.add_trace(go.Scatter(x=hl["year"], y=hl["headline_cpi"], mode="lines+markers",
                                 name="Official CPI", line=dict(color="#95A5A6", width=2, dash="dash"), marker=dict(size=6)))
        for group in WEIGHTS:
            gdf = di[di["group"] == group]
            fig.add_trace(go.Scatter(x=gdf["year"], y=gdf["group_inflation"], mode="lines+markers+text",
                                     name=SHORT[group], line=dict(color=COLORS[group], width=3),
                                     marker=dict(size=10, symbol="diamond"),
                                     text=[f"{v:+.1f}%" for v in gdf["group_inflation"]],
                                     textposition="top center", textfont=dict(size=11, color=COLORS[group])))
        fig.add_annotation(x=2022, y=14.4, text="Rural Biz: +14.4%<br>(energy crisis)",
                          showarrow=True, arrowhead=2, ax=-80, ay=-30,
                          bgcolor="rgba(39,174,96,0.1)", bordercolor="#27AE60", font=dict(size=11, color="#27AE60"))
        fig = styled(fig, h=450)
        fig.update_yaxes(title_text="Inflation (%)", ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    elif slide == 4:
        st.markdown('''
        <div class="story-slide">
            <span class="slide-num">4</span> <b style="font-size:18px;">The Spending Squeeze</b>
            <hr style="margin:12px 0;">
            <p style="font-size:16px;">When essentials eat more of your income, you have nothing left.</p>
        </div>''', unsafe_allow_html=True)
        squeeze_html = '<div class="kpi-row">'
        for group in WEIGHTS:
            g21 = burden[(burden["group"] == group) & (burden["year"] == 2021)]
            g25 = burden[(burden["group"] == group) & (burden["year"] == 2025)]
            if not g21.empty and not g25.empty:
                v21 = g21.iloc[0]["nondiscretionary_pct"]
                v25 = g25.iloc[0]["nondiscretionary_pct"]
                shift = v25 - v21
                income = MEDIAN_INCOMES[group][2025]
                left = income * (100 - v25) / 100
                color = COLORS[group]
                squeeze_html += f'''
                <div class="kpi-card" style="border-left:4px solid {color};">
                    <div class="label">{SHORT[group]}</div>
                    <div class="value" style="color:{color}; font-size:22px;">{v21:.0f}% &rarr; {v25:.0f}%</div>
                    <div class="delta pos">+{shift:.1f}pp more of income to essentials</div>
                    <div class="delta neutral" style="margin-top:6px;">Only ${left:,.0f}/yr left for everything else</div>
                </div>'''
        squeeze_html += '</div>'
        st.markdown(squeeze_html, unsafe_allow_html=True)

    elif slide == 5:
        st.markdown('''
        <div class="story-slide">
            <span class="slide-num">5</span> <b style="font-size:18px;">The Bank Feels It Too</b>
            <hr style="margin:12px 0;">
            <p style="font-size:16px;">When customers get squeezed, the bank's numbers go red.</p>
        </div>''', unsafe_allow_html=True)
        b21, b25 = BANK_DATA[2021], BANK_DATA[2025]
        stress_data = {
            "Metric": ["Deposits", "Auto Defaults", "Card Utilization", "Biz Delinquencies"],
            "2021": [f"${b21['total_retail_deposits']/1e9:.1f}B", f"{b21['auto_loan_default_rate']*100:.1f}%",
                     f"{b21['credit_card_utilization']*100:.0f}%", f"{b21['small_biz_delinquencies']*100:.1f}%"],
            "2025": [f"${b25['total_retail_deposits']/1e9:.2f}B", f"{b25['auto_loan_default_rate']*100:.1f}%",
                     f"{b25['credit_card_utilization']*100:.0f}%", f"{b25['small_biz_delinquencies']*100:.1f}%"],
            "Change": ["-$150M", "+1.2pp", "+12pp", "TRIPLED"],
        }
        st.dataframe(pd.DataFrame(stress_data), use_container_width=True, hide_index=True)

    elif slide == 6:
        st.markdown('''
        <div class="story-slide">
            <span class="slide-num">6</span> <b style="font-size:18px;">Risk Scores at a Glance</b>
            <hr style="margin:12px 0;">
            <p style="font-size:16px;">A single number a loan officer can use.</p>
        </div>''', unsafe_allow_html=True)
        r_cols = st.columns(3)
        for i, group in enumerate(WEIGHTS):
            score = compute_risk_score(group, di, burden)
            color = COLORS[group]
            level_color = "#E74C3C" if score >= 7 else "#F39C12" if score >= 4.5 else "#27AE60"
            level = "HIGH" if score >= 7 else "MODERATE" if score >= 4.5 else "LOW"
            with r_cols[i]:
                st.markdown(f'''
                <div class="risk-card" style="border-color:{color};">
                    <div class="risk-score" style="color:{level_color};">{score}</div>
                    <div class="risk-label">{SHORT[group]}</div>
                    <div class="risk-level" style="color:{level_color};">{level} RISK</div>
                </div>''', unsafe_allow_html=True)

    elif slide == 7:
        st.markdown('''
        <div class="story-slide">
            <span class="slide-num">7</span> <b style="font-size:18px;">The Recommendation: Divergence-Adjusted Credit Framework</b>
            <hr style="margin:12px 0;">
        </div>''', unsafe_allow_html=True)
        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown('''
            <div class="kpi-card" style="border-left:4px solid #E74C3C;">
                <div class="label" style="color:#E74C3C; font-size:15px;">Pillar 1: Fix Risk Models</div>
                <p style="font-size:13px; margin-top:8px; line-height:1.6;">
                Add demographic inflation exposure to credit scoring. Flag portfolios in high-stress groups.
                Increase loss reserves where real purchasing power declined most.
                </p>
            </div>''', unsafe_allow_html=True)
        with p2:
            st.markdown('''
            <div class="kpi-card" style="border-left:4px solid #3498DB;">
                <div class="label" style="color:#3498DB; font-size:15px;">Pillar 2: Targeted Products</div>
                <p style="font-size:13px; margin-top:8px; line-height:1.6;">
                Seniors: inflation-indexed CDs, Rx financing.<br>
                Renters: rent-smoothing, homebuyer programs.<br>
                Rural Biz: energy hedging, seasonal payments.
                </p>
            </div>''', unsafe_allow_html=True)
        with p3:
            st.markdown('''
            <div class="kpi-card" style="border-left:4px solid #27AE60;">
                <div class="label" style="color:#27AE60; font-size:15px;">Pillar 3: Retain Deposits</div>
                <p style="font-size:13px; margin-top:8px; line-height:1.6;">
                Recover $60-90M of the $150M outflow.<br>
                Seniors: guaranteed-rate CDs.<br>
                Rural Biz: fee-waiver bundles.<br>
                Renters: high-yield autopay savings.
                </p>
            </div>''', unsafe_allow_html=True)
        st.markdown("")
        st.success("**Projected 12-month impact:** Recover $60-90M deposits | Auto losses -15-20bps | Biz delinquencies stabilize at 2.5%")
