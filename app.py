"""Divergence Index — Interactive Dashboard.

Run:
    streamlit run app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import WEIGHTS, BANK_DATA, MEDIAN_INCOMES, NON_DISCRETIONARY, DISCRETIONARY

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
    "owners_equiv_rent": "Home Ownership Costs",
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
        background: #f0f7ff; border-left: 4px solid #3498db;
        padding: 12px 16px; border-radius: 0 8px 8px 0;
        margin-bottom: 16px; font-size: 14px; line-height: 1.6;
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
        font=dict(family="Inter, sans-serif", size=13, color="#34495E"),
        plot_bgcolor="rgba(250,250,252,1)", paper_bgcolor="white",
        height=h, margin=dict(l=55, r=20, t=30, b=50),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.95)", bordercolor="#E9ECEF", borderwidth=1,
            font=dict(size=12),
        ),
        hovermode="x unified",
        dragmode="pan",
        modebar=dict(
            bgcolor="rgba(255,255,255,0.8)",
            color="#6c757d",
            activecolor="#3498DB",
            orientation="h",
        ),
    )
    fig.update_xaxes(gridcolor="#F0F0F0", linecolor="#CED4DA", dtick=1,
                     rangeslider=dict(visible=False), fixedrange=False)
    fig.update_yaxes(gridcolor="#F0F0F0", linecolor="#CED4DA", fixedrange=False)
    return fig


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
    show_headline = st.toggle("Show average CPI line", value=True, help="The gray dashed line = what the government says the 'average' inflation is")
    show_explanations = st.toggle("Show explanations", value=True, help="Toggle the blue explanation boxes on/off")

    st.divider()
    st.caption("Data sources: Bureau of Labor Statistics (CPI), Federal Reserve (FRED)")
    st.caption("Period: 2021 - 2025")

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
        arrow = "^" if div > 0 else "v" if div < 0 else ""
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
tab1, tab2, tab3, tab4 = st.tabs([
    "Inflation by Group",
    "Who Pays More?",
    "Spending Squeeze",
    "Bank Impact",
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — INFLATION BY GROUP
# ════════════════════════════════════════════════════════════════
with tab1:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> Each line shows the real inflation rate a specific "
            "group of people experienced each year. The gray dashed line is the official "
            "government average (CPI). When a colored line is ABOVE the gray line, that group "
            "is paying more than the average person. When it's below, they're paying less."
            "</div>",
            unsafe_allow_html=True,
        )

    view = st.radio(
        "View", ["Year by year", "Total since 2021"],
        horizontal=True, label_visibility="collapsed",
    )

    if view == "Year by year":
        fig = go.Figure()
        if show_headline and not di_f.empty:
            hl = di_f.drop_duplicates("year")[["year", "headline_cpi"]].dropna()
            fig.add_trace(go.Scatter(
                x=hl["year"], y=hl["headline_cpi"],
                mode="lines+markers", name="Official CPI (avg)",
                line=dict(color=COLORS["headline"], width=2, dash="dash"),
                marker=dict(size=6),
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
                line=dict(color=COLORS[group], width=3),
                marker=dict(size=9),
                fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.07)",
                text=[f"{v:+.1f}%" if v != 0 else "" for v in gdf["cumulative_inflation"]],
                textposition="top center", textfont=dict(size=11),
                hovertemplate="%{y:+.1f}% total<extra>" + SHORT[group] + "</extra>",
            ))
        fig = styled(fig, h=480)
        fig.update_yaxes(title_text="Total price increase since 2021 (%)", ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    if show_explanations:
        st.info(
            "**Key takeaway:** In 2022, Rural Small Business Owners experienced +14.4% inflation "
            "while the government said the average was +8.0%. That means a rural business owner's "
            "costs nearly doubled the 'official' rate, mostly because of gasoline and energy prices."
        )

    with st.expander("See the numbers in a table"):
        display_df = di_f[["year", "group", "group_inflation", "headline_cpi", "divergence"]].copy()
        display_df.columns = ["Year", "Group", "Their Inflation (%)", "Official CPI (%)", "Gap (pp)"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 — WHO PAYS MORE
# ════════════════════════════════════════════════════════════════
with tab2:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> These bars show how much MORE or LESS each group "
            "paid compared to the official average inflation (CPI). A bar going UP means that group "
            "got hit harder than average. A bar going DOWN means they got some relief that year."
            "</div>",
            unsafe_allow_html=True,
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
            hovertemplate="<b>%{x}</b><br>%{y:+.1f} percentage points vs CPI<extra>" + SHORT[group] + "</extra>",
        ))
    fig.update_layout(barmode="group")
    fig = styled(fig, h=480)
    fig.update_yaxes(title_text="Difference from official CPI (percentage points)", zeroline=True)
    fig.add_annotation(
        x=2022, y=6.5, text="Rural Biz: +6.5pp above CPI",
        showarrow=True, arrowhead=2, ax=0, ay=-40,
        bgcolor="rgba(39,174,96,0.1)", bordercolor="#27AE60", borderpad=4,
        font=dict(size=11, color="#27AE60"),
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with st.expander("What drove the differences? (price changes by category)"):
        year_pick = st.select_slider(
            "Pick a year to explore",
            options=sorted(di_f["year"].unique()),
            value=int(di_f["year"].max()),
            key="cat_year",
        )
        cpi_yoy = data["cpi_yoy"]
        if year_pick in cpi_yoy.index:
            row = cpi_yoy.loc[year_pick].dropna().sort_values(ascending=False)
            cat_df = pd.DataFrame({
                "Category": [NICE_CATEGORIES.get(c, c) for c in row.index],
                "Price Change (%)": [round(v, 1) for v in row.values],
            })
            cat_df = cat_df[cat_df["Category"] != "All Items (Average)"]

            fig2 = go.Figure()
            colors = ["#E74C3C" if v > 0 else "#27AE60" for v in cat_df["Price Change (%)"]]
            fig2.add_trace(go.Bar(
                y=cat_df["Category"], x=cat_df["Price Change (%)"],
                orientation="h", marker_color=colors,
                text=[f"{v:+.1f}%" for v in cat_df["Price Change (%)"]],
                textposition="outside",
            ))
            fig2.update_layout(
                height=450, margin=dict(l=140, r=40, t=10, b=30),
                plot_bgcolor="rgba(250,250,252,1)", paper_bgcolor="white",
                font=dict(size=12),
                xaxis_title=f"Price change in {year_pick} (%)",
            )
            fig2.update_xaxes(gridcolor="#F0F0F0")
            fig2.update_yaxes(gridcolor="#F0F0F0")
            st.plotly_chart(fig2, use_container_width=True, config=CHART_CONFIG)

            if show_explanations:
                st.caption(
                    "Red bars = prices went up. Green bars = prices went down. "
                    "The categories at the top rose the most that year."
                )

# ════════════════════════════════════════════════════════════════
# TAB 3 — SPENDING SQUEEZE
# ════════════════════════════════════════════════════════════════
with tab3:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> This shows what percentage of each group's income goes to "
            "things they MUST pay for — rent, food, medical bills, gas, electricity. "
            "The higher the line, the less money they have left for anything else. "
            "When a group crosses the 80% red line, they're in serious financial stress."
            "</div>",
            unsafe_allow_html=True,
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
    fig.add_hline(
        y=80, line_dash="dot", line_color="#E74C3C", line_width=2,
        annotation_text="Danger zone (80%+)",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color="#E74C3C"),
    )
    fig.add_hrect(y0=80, y1=95, fillcolor="rgba(231,76,60,0.04)", line_width=0)
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

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=[f"2021 — Where each dollar went", f"{compare_yr} — Where each dollar goes now"],
            shared_yaxes=True,
        )
        names = [SHORT[g] for g in selected_groups]
        for col_idx, yr in enumerate([2021, compare_yr], 1):
            ydf = burden[burden["year"] == yr]
            nd = [ydf[ydf["group"] == g]["nondiscretionary_pct"].values[0] if len(ydf[ydf["group"] == g]) else 0 for g in selected_groups]
            d = [ydf[ydf["group"] == g]["discretionary_pct"].values[0] if len(ydf[ydf["group"] == g]) else 0 for g in selected_groups]
            rem = [max(0, 100 - n - dv) for n, dv in zip(nd, d)]
            fig.add_trace(go.Bar(
                x=names, y=nd,
                name="Must-pay (rent, food, medical...)" if col_idx == 1 else None,
                marker_color="#E74C3C", opacity=0.85,
                showlegend=(col_idx == 1), legendgroup="nd",
                text=[f"{v:.0f}%" for v in nd], textposition="inside", textfont=dict(color="white", size=12),
            ), row=1, col=col_idx)
            fig.add_trace(go.Bar(
                x=names, y=d,
                name="Optional (eating out, clothes...)" if col_idx == 1 else None,
                marker_color="#F39C12", opacity=0.85,
                showlegend=(col_idx == 1), legendgroup="d",
                text=[f"{v:.0f}%" for v in d], textposition="inside", textfont=dict(color="white", size=11),
            ), row=1, col=col_idx)
            fig.add_trace(go.Bar(
                x=names, y=rem,
                name="Savings / extra" if col_idx == 1 else None,
                marker_color="#2ECC71", opacity=0.85,
                showlegend=(col_idx == 1), legendgroup="r",
                text=[f"{v:.0f}%" for v in rem], textposition="inside", textfont=dict(color="white", size=11),
            ), row=1, col=col_idx)
        fig.update_layout(barmode="stack")
        fig = styled(fig, h=460)
        fig.update_yaxes(title_text="% of income", ticksuffix="%", row=1, col=1)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

# ════════════════════════════════════════════════════════════════
# TAB 4 — BANK IMPACT
# ════════════════════════════════════════════════════════════════
with tab4:
    if show_explanations:
        st.markdown(
            '<div class="explanation">'
            "<b>What am I looking at?</b> This is the bank's data. When people get squeezed by inflation, "
            "they pull money out of their savings (deposits go down), max out credit cards (utilization goes up), "
            "and start missing loan payments (defaults and delinquencies go up). This tab shows all of that happening."
            "</div>",
            unsafe_allow_html=True,
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
            <div class="delta pos">+{(b25["credit_card_utilization"]-b21["credit_card_utilization"])*100:.0f}pp — maxing out cards</div>
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
        fig.add_trace(go.Bar(
            x=categories, y=vals_21, name="2021", marker_color="#3498DB", opacity=0.8,
            text=[f"{v:.1f}%" for v in vals_21], textposition="outside", textfont=dict(size=13),
        ))
        fig.add_trace(go.Bar(
            x=categories, y=vals_25, name="2025", marker_color="#E74C3C", opacity=0.8,
            text=[f"{v:.1f}%" for v in vals_25], textposition="outside", textfont=dict(size=13),
        ))
        fig.update_layout(barmode="group")
        fig = styled(fig, h=420)
        fig.update_yaxes(title_text="Rate (%)", ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with c2:
        st.markdown("#### The Connection")
        st.markdown("""
        **Inflation squeeze** --> **Credit stress**

        1. Energy prices spiked in 2022
        2. Rural businesses burned through cash reserves
        3. By 2025, small biz delinquencies **tripled** (1.1% to 3.2%)
        4. Customers pulled $150M from deposits
        5. Credit card maxing-out jumped from 29% to 41%

        This is why the bank needs a **demographic-aware strategy** --
        the "average" inflation number hides who is actually hurting.
        """)

    if show_explanations:
        st.divider()
        with st.expander("What should the bank do? (Strategic Recommendation)"):
            st.markdown("""
            ### Divergence-Adjusted Credit Framework (DACF)

            **Pillar 1 — Fix the risk models**
            - Current models use "average" inflation. That misses who's actually struggling.
            - Add demographic inflation exposure to credit scoring.
            - Flag portfolios concentrated in high-stress groups.

            **Pillar 2 — Create products that match real needs**

            | Group | Their Problem | Product Solution |
            |-------|--------------|-----------------|
            | **Seniors** | Medical costs eating 26% of income | Inflation-indexed CDs that track medical CPI; prescription financing |
            | **Urban Renters** | Rent is 28% of spending | Rent-smoothing accounts; first-time homebuyer programs |
            | **Rural Biz** | Energy costs doubled | Energy cost hedging; seasonal payment schedules |

            **Pillar 3 — Stop the deposit bleeding**
            - $150M left the bank. Target retention by group:
            - Seniors: guaranteed-rate CDs (they want safety)
            - Rural Biz: fee-waiver bundles for operating accounts
            - Renters: high-yield savings with autopay bonuses

            **Projected impact (12 months):**
            - Recover $60-90M in deposits
            - Cut auto loan losses by 15-20 basis points
            - Stabilize small biz delinquencies at 2.5%
            """)
