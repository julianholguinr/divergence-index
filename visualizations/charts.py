"""Professional visualizations for Divergence Index case competition.

Generates presentation-ready charts using Plotly and Matplotlib.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WEIGHTS, MEDIAN_INCOMES, BANK_DATA

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

COLORS = {
    "Fixed-Income Seniors": "#E74C3C",
    "Urban Renters": "#3498DB",
    "Rural Small Business Owners": "#27AE60",
    "headline": "#7F8C8D",
}

FILL_COLORS = {
    "Fixed-Income Seniors": "rgba(231,76,60,0.08)",
    "Urban Renters": "rgba(52,152,219,0.08)",
    "Rural Small Business Owners": "rgba(39,174,96,0.08)",
}

GROUP_SHORT = {
    "Fixed-Income Seniors": "Seniors",
    "Urban Renters": "Urban Renters",
    "Rural Small Business Owners": "Rural Biz",
}


def _style_figure(fig, title: str, height: int = 500) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color="#2C3E50"), x=0.5),
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#34495E"),
        plot_bgcolor="rgba(248,249,250,1)",
        paper_bgcolor="white",
        height=height,
        margin=dict(l=60, r=30, t=80, b=60),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.8)", bordercolor="#DEE2E6", borderwidth=1,
        ),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="#DEE2E6", linecolor="#ADB5BD")
    fig.update_yaxes(gridcolor="#DEE2E6", linecolor="#ADB5BD")
    return fig


def chart_divergence_index() -> go.Figure:
    """Chart 1: Divergence Index by group over time."""
    df = pd.read_csv(PROCESSED_DIR / "divergence_index.csv")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[df["group"] == list(WEIGHTS.keys())[0]]["year"],
        y=df[df["group"] == list(WEIGHTS.keys())[0]]["headline_cpi"],
        mode="lines+markers",
        name="Headline CPI",
        line=dict(color=COLORS["headline"], width=3, dash="dash"),
        marker=dict(size=8),
    ))

    for group in WEIGHTS:
        gdf = df[df["group"] == group]
        fig.add_trace(go.Scatter(
            x=gdf["year"],
            y=gdf["group_inflation"],
            mode="lines+markers",
            name=GROUP_SHORT[group],
            line=dict(color=COLORS[group], width=3),
            marker=dict(size=10, symbol="diamond"),
            hovertemplate="%{y:+.1f}%<extra>" + GROUP_SHORT[group] + "</extra>",
        ))

    fig = _style_figure(fig, "The Divergence Index: Experienced Inflation by Group", height=520)
    fig.update_yaxes(title_text="Year-over-Year Inflation (%)", ticksuffix="%")
    fig.update_xaxes(title_text="Year", dtick=1)

    fig.add_annotation(
        x=2022, y=14.4,
        text="Rural Biz: +14.4%<br>(Energy spike)",
        showarrow=True, arrowhead=2, ax=-80, ay=-40,
        bgcolor="rgba(39,174,96,0.1)", bordercolor="#27AE60",
        font=dict(size=11, color="#27AE60"),
    )

    return fig


def chart_divergence_gap() -> go.Figure:
    """Chart 2: Divergence gap (group inflation - headline CPI)."""
    df = pd.read_csv(PROCESSED_DIR / "divergence_index.csv")

    fig = go.Figure()

    fig.add_hline(y=0, line_dash="dash", line_color="#ADB5BD", line_width=1)

    for group in WEIGHTS:
        gdf = df[df["group"] == group]
        fig.add_trace(go.Bar(
            x=gdf["year"],
            y=gdf["divergence"],
            name=GROUP_SHORT[group],
            marker_color=COLORS[group],
            opacity=0.85,
            hovertemplate="%{y:+.1f}pp<extra>" + GROUP_SHORT[group] + "</extra>",
        ))

    fig = _style_figure(fig, "Inflation Gap: Group Rate vs. Headline CPI", height=480)
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Divergence (percentage points)", zeroline=True)
    fig.update_xaxes(title_text="Year", dtick=1)

    return fig


def chart_cumulative_inflation() -> go.Figure:
    """Chart 3: Cumulative inflation since 2021 base year."""
    df = pd.read_csv(PROCESSED_DIR / "cumulative_inflation.csv")

    fig = go.Figure()

    for group in WEIGHTS:
        gdf = df[df["group"] == group]
        fig.add_trace(go.Scatter(
            x=gdf["year"],
            y=gdf["cumulative_inflation"],
            mode="lines+markers",
            name=GROUP_SHORT[group],
            line=dict(color=COLORS[group], width=3),
            marker=dict(size=9),
            fill="tozeroy",
            fillcolor=FILL_COLORS[group],
            hovertemplate="%{y:+.1f}%<extra>" + GROUP_SHORT[group] + "</extra>",
        ))

    fig = _style_figure(fig, "Cumulative Price Increase Since 2021", height=500)
    fig.update_yaxes(title_text="Cumulative Inflation (%)", ticksuffix="%")
    fig.update_xaxes(title_text="Year", dtick=1)

    return fig


def chart_nondiscretionary_burden() -> go.Figure:
    """Chart 4: Non-discretionary spending as % of income."""
    df = pd.read_csv(PROCESSED_DIR / "nondiscretionary_burden.csv")

    fig = go.Figure()

    for group in WEIGHTS:
        gdf = df[df["group"] == group]
        fig.add_trace(go.Scatter(
            x=gdf["year"],
            y=gdf["nondiscretionary_pct"],
            mode="lines+markers",
            name=GROUP_SHORT[group],
            line=dict(color=COLORS[group], width=3),
            marker=dict(size=10),
            hovertemplate="%{y:.1f}%<extra>" + GROUP_SHORT[group] + "</extra>",
        ))

    fig.add_hline(
        y=80, line_dash="dot", line_color="#E74C3C", line_width=1.5,
        annotation_text="Critical Burden Threshold (80%)",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#E74C3C"),
    )

    fig = _style_figure(fig, "Non-Discretionary Spending Burden (% of Income)", height=520)
    fig.update_yaxes(title_text="% of Median Income", range=[50, 95], ticksuffix="%")
    fig.update_xaxes(title_text="Year", dtick=1)

    return fig


def chart_burden_breakdown() -> go.Figure:
    """Chart 5: Stacked bar showing burden composition for 2021 vs 2025."""
    df = pd.read_csv(PROCESSED_DIR / "nondiscretionary_burden.csv")

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["2021 (Pre-Inflation)", "2025 (Post-Inflation)"],
        shared_yaxes=True,
    )

    groups = list(WEIGHTS.keys())
    short_names = [GROUP_SHORT[g] for g in groups]

    for col_idx, year in enumerate([2021, 2025], 1):
        ydf = df[df["year"] == year]
        nd_vals = [ydf[ydf["group"] == g]["nondiscretionary_pct"].values[0] for g in groups]
        d_vals = [ydf[ydf["group"] == g]["discretionary_pct"].values[0] for g in groups]
        disp_vals = [ydf[ydf["group"] == g]["disposable_pct"].values[0] for g in groups]

        fig.add_trace(go.Bar(
            x=short_names, y=nd_vals,
            name="Non-Discretionary" if col_idx == 1 else None,
            marker_color="#E74C3C", opacity=0.85,
            showlegend=(col_idx == 1),
            legendgroup="nd",
            hovertemplate="%{y:.1f}%<extra>Non-Discretionary</extra>",
        ), row=1, col=col_idx)

        fig.add_trace(go.Bar(
            x=short_names, y=d_vals,
            name="Discretionary" if col_idx == 1 else None,
            marker_color="#F39C12", opacity=0.85,
            showlegend=(col_idx == 1),
            legendgroup="d",
            hovertemplate="%{y:.1f}%<extra>Discretionary</extra>",
        ), row=1, col=col_idx)

        fig.add_trace(go.Bar(
            x=short_names, y=disp_vals,
            name="Disposable" if col_idx == 1 else None,
            marker_color="#2ECC71", opacity=0.85,
            showlegend=(col_idx == 1),
            legendgroup="disp",
            hovertemplate="%{y:.1f}%<extra>Disposable</extra>",
        ), row=1, col=col_idx)

    fig.update_layout(barmode="stack")
    fig = _style_figure(fig, "Income Allocation: 2021 vs 2025", height=520)
    fig.update_yaxes(title_text="% of Income", ticksuffix="%", row=1, col=1)

    return fig


def chart_bank_credit_stress() -> go.Figure:
    """Chart 6: Bank credit stress indicators (from case data)."""
    years = list(BANK_DATA.keys())
    metrics = {
        "Auto Loan Default Rate": [BANK_DATA[y]["auto_loan_default_rate"] * 100 for y in years],
        "Credit Card Utilization": [BANK_DATA[y]["credit_card_utilization"] * 100 for y in years],
        "Small Biz Delinquencies": [BANK_DATA[y]["small_biz_delinquencies"] * 100 for y in years],
    }
    metric_colors = ["#E74C3C", "#3498DB", "#27AE60"]

    fig = go.Figure()
    for (name, values), color in zip(metrics.items(), metric_colors):
        fig.add_trace(go.Bar(
            x=[str(y) for y in years],
            y=values,
            name=name,
            marker_color=color,
            opacity=0.85,
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
        ))

    fig = _style_figure(fig, "Credit Stress Indicators: 2021 vs 2025", height=480)
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Rate (%)", ticksuffix="%")

    return fig


def generate_all_charts():
    """Generate and save all charts."""
    charts = {
        "01_divergence_index": chart_divergence_index,
        "02_divergence_gap": chart_divergence_gap,
        "03_cumulative_inflation": chart_cumulative_inflation,
        "04_nondiscretionary_burden": chart_nondiscretionary_burden,
        "05_burden_breakdown": chart_burden_breakdown,
        "06_credit_stress": chart_bank_credit_stress,
    }

    print("Generating presentation charts...")
    for name, chart_fn in charts.items():
        fig = chart_fn()
        html_path = OUTPUT_DIR / f"{name}.html"
        png_path = OUTPUT_DIR / f"{name}.png"

        pio.write_html(fig, str(html_path), include_plotlyjs="cdn")
        print(f"  Saved {html_path.name}")

        try:
            pio.write_image(fig, str(png_path), width=1200, height=600, scale=2)
            print(f"  Saved {png_path.name}")
        except Exception:
            print(f"  (PNG export requires kaleido — HTML saved)")

    print(f"\nAll charts saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    generate_all_charts()
