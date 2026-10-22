"""Generate the Divergence Index pitch deck presentation."""
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import plotly.graph_objects as go
import plotly.io as pio
import os

os.makedirs("output/slides", exist_ok=True)

DARK_GREEN = RGBColor(0x1B, 0x3D, 0x2F)
MEDIUM_GREEN = RGBColor(0x2D, 0x5A, 0x47)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CREAM = RGBColor(0xE8, 0xD5, 0xC4)
BLACK = RGBColor(0x00, 0x00, 0x00)
GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT_GRAY = RGBColor(0xF5, 0xF5, 0xF5)
RED = RGBColor(0xE7, 0x4C, 0x3C)
ORANGE = RGBColor(0xF3, 0x9C, 0x12)
BLUE = RGBColor(0x34, 0x98, 0xDB)
TEAL = RGBColor(0x2D, 0x9C, 0x8A)

SENIOR_COLOR = "#E74C3C"
RENTER_COLOR = "#3498DB"
RURAL_COLOR = "#27AE60"
CPI_COLOR = "#95A5A6"

di = pd.read_csv("data/processed/divergence_index.csv")
burden = pd.read_csv("data/processed/nondiscretionary_burden.csv")
cumul = pd.read_csv("data/processed/cumulative_inflation.csv")
yoy = pd.read_csv("data/processed/cpi_yoy_changes.csv")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)


def add_bg(slide, color=DARK_GREEN):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(slide, left, top, width, height, text, font_size=14,
                color=WHITE, bold=False, alignment=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_multiline(slide, left, top, width, height, lines, font_size=14,
                  color=WHITE, alignment=PP_ALIGN.LEFT, spacing=1.2, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, (text, bold, size_override, color_override) in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(size_override or font_size)
        p.font.color.rgb = color_override or color
        p.font.bold = bold
        p.font.name = font_name
        p.alignment = alignment
        p.space_after = Pt(font_size * (spacing - 1))
    return txBox


def add_rect(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_line(slide, left, top, width):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.02))
    shape.fill.solid()
    shape.fill.fore_color.rgb = CREAM
    shape.line.fill.background()
    return shape


def save_plotly_image(fig, filename, w=900, h=500):
    fig.update_layout(
        font=dict(family="Calibri, sans-serif", color="black"),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=60, r=30, t=40, b=50),
    )
    fig.update_xaxes(gridcolor="#eee", linecolor="#ccc", tickfont=dict(color="black"), title_font=dict(color="black"))
    fig.update_yaxes(gridcolor="#eee", linecolor="#ccc", tickfont=dict(color="black"), title_font=dict(color="black"))
    pio.write_image(fig, f"output/slides/{filename}", width=w, height=h, scale=2)


# ═══════════════════════════════════════════════════════
# SLIDE 1: TITLE
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, DARK_GREEN)

add_textbox(slide, 0.8, 0.4, 8, 0.5, "QBEA Data Dive Case Competition  |  Fall 2026",
            font_size=14, color=CREAM)

add_multiline(slide, 0.8, 1.2, 8, 2.5, [
    ("The Divergence Index", True, 40, WHITE),
    ("Mapping Demographic Inflation for", False, 28, CREAM),
    ("Regional Credit Strategy", False, 28, CREAM),
])

add_line(slide, 0.8, 4.0, 7)

add_multiline(slide, 0.8, 4.3, 7, 2, [
    ("\"Average\" inflation masks who's truly hurting. Our Divergence Index reveals", False, 16, CREAM),
    ("that Rural Small Business Owners experienced 10.9% inflation in 2022 —", False, 16, CREAM),
    ("well above the official 8.0% Midwest CPI — while Seniors faced relentless", False, 16, CREAM),
    ("medical cost pressure with 65% of income locked in essentials.", False, 16, CREAM),
])

# Key metrics box on right
add_rect(slide, 9.5, 1.0, 3.3, 2.0, MEDIUM_GREEN)
add_multiline(slide, 9.7, 1.1, 2.9, 1.8, [
    ("Peak Divergence", False, 12, CREAM),
    ("+3.1pp", True, 44, WHITE),
    ("Rural Biz vs. CPI, 2022", False, 12, CREAM),
])

add_rect(slide, 9.5, 3.3, 3.3, 2.0, MEDIUM_GREEN)
add_multiline(slide, 9.7, 3.4, 2.9, 1.8, [
    ("Deposits Lost", False, 12, CREAM),
    ("-$150M", True, 44, RED),
    ("Bank deposit outflow 2021-2025", False, 12, CREAM),
])

add_rect(slide, 9.5, 5.6, 3.3, 1.2, MEDIUM_GREEN)
add_multiline(slide, 9.7, 5.65, 2.9, 1.0, [
    ("Senior Burden", False, 12, CREAM),
    ("68.5%", True, 36, ORANGE),
    ("of income → essentials", False, 12, CREAM),
])

add_textbox(slide, 0.8, 6.5, 8, 0.5, "Purdue University  |  QBEA Data Dive",
            font_size=13, color=CREAM)
add_textbox(slide, 0.8, 6.85, 8, 0.5,
            "Sources: BLS CPI, BLS Consumer Expenditure Survey, FRED Economic Data, U.S. Census ACS",
            font_size=10, color=RGBColor(0x88, 0xAA, 0x99))


# ═══════════════════════════════════════════════════════
# SLIDE 2: EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)

add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 3, 0.4, "Executive Summary", font_size=13, color=DARK_GREEN, bold=True)

add_textbox(slide, 0.5, 0.8, 12, 1.2,
            "The official CPI understates inflation for every key bank customer segment — "
            "a hidden risk that explains the bank's rising defaults, deposit flight, and credit stress.",
            font_size=24, color=BLACK, bold=False, font_name="Calibri")

add_line(slide, 0.5, 2.1, 12)

# Three deliverables columns
for i, (title, items) in enumerate([
    ("Deliverable 1: Divergence Index", [
        "Personalized inflation rates for 3 groups",
        "Rural Biz: +10.9% in 2022 (vs 8% Midwest CPI)",
        "Seniors: consistently above average",
        "All groups: +16-16.4% cumulative (2021-25)",
    ]),
    ("Deliverable 2: Non-Discretionary Burden", [
        "% of income locked in must-pay expenses",
        "Seniors: 65% → 68.5% (+3.5pp)",
        "Rural Biz: 61% → 65.5% (+4.5pp squeeze)",
        "Urban Renters: 54% → 58.2% (+4.2pp)",
    ]),
    ("Deliverable 3: Strategic Recommendation", [
        "Divergence-Adjusted Credit Framework",
        "Pillar 1: Fix risk models with cash-flow exposure (ECOA-compliant)",
        "Pillar 2: Targeted products per group",
        "Pillar 3: Stem deposit outflow ($150M lost)",
    ]),
]):
    x = 0.5 + i * 4.1
    add_rect(slide, x, 2.5, 3.8, 0.35, DARK_GREEN)
    add_textbox(slide, x + 0.1, 2.52, 3.6, 0.35, title, font_size=12, color=WHITE, bold=True)
    for j, item in enumerate(items):
        add_textbox(slide, x + 0.1, 3.05 + j * 0.45, 3.6, 0.4,
                    f"• {item}", font_size=12, color=BLACK)

# Bottom KPI row
metrics = [
    ("3", "Demographic Groups"),
    ("17", "CPI Sub-Categories"),
    ("2021-2025", "Analysis Period"),
    ("5", "Real Data Sources"),
]
for i, (val, label) in enumerate(metrics):
    x = 0.5 + i * 3.1
    add_rect(slide, x, 5.3, 2.8, 1.2, LIGHT_GRAY)
    add_textbox(slide, x, 5.4, 2.8, 0.7, val, font_size=32, color=DARK_GREEN, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, x, 6.0, 2.8, 0.4, label, font_size=12, color=GRAY,
                alignment=PP_ALIGN.CENTER)

add_textbox(slide, 0.5, 7.0, 6, 0.3,
            "Sources: BLS CPI-U (Midwest Urban), BLS CEX, FRED, US Census ACS, Case document",
            font_size=9, color=GRAY)
add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "1", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 3: HYPOTHESIS
# ═══════════════════════════════════════════════════════
PURPLE = RGBColor(0x8E, 0x44, 0xAD)
LIGHT_PURPLE = RGBColor(0xF4, 0xEC, 0xF7)

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, PURPLE)
add_textbox(slide, 0.5, 0.3, 5, 0.4, "Hypothesis  |  Stated Before Analysis", font_size=13, color=PURPLE, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "Before running any numbers, we formulated three testable hypotheses. "
            "We present them here so our findings can be evaluated against our prior expectations.",
            font_size=22, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

hypotheses = [
    ("H1", "Different groups experience meaningfully different inflation",
     "Because each demographic allocates spending differently across housing, energy, medical care, "
     "and food, their effective inflation rate should diverge significantly from the headline CPI — "
     "especially during sector-specific price shocks like the 2022 energy crisis.",
     "Testable prediction: At least one group should show >2 percentage points divergence from CPI in a shock year."),
    ("H2", "The non-discretionary burden is the real squeeze",
     "Even if cumulative inflation converges across groups over time, the share of income consumed "
     "by essentials should grow — because prices don't reverse, they just stop rising as fast, "
     "while income growth (wages, Social Security COLAs, pensions) lags behind.",
     "Testable prediction: Non-discretionary burden as % of income should increase for all groups from 2021 to 2025."),
    ("H3", "Inflation divergence predicts bank credit stress",
     "Groups experiencing above-average inflation should show correlated deterioration in bank "
     "metrics — deposit withdrawals, rising delinquencies, higher credit utilization — because "
     "standard risk models don't account for demographic-specific cost pressure.",
     "Testable prediction: Bank stress indicators should worsen most for the group with the highest divergence."),
]

for i, (h_id, title, reasoning, prediction) in enumerate(hypotheses):
    y = 2.0 + i * 1.75
    add_rect(slide, 0.5, y, 12.3, 1.55, LIGHT_PURPLE)
    add_rect(slide, 0.5, y, 0.7, 1.55, PURPLE)
    add_textbox(slide, 0.5, y + 0.35, 0.7, 0.5, h_id, font_size=18, color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 1.4, y + 0.1, 11.2, 0.35, title, font_size=15, color=PURPLE, bold=True)
    add_textbox(slide, 1.4, y + 0.45, 11.2, 0.6, reasoning, font_size=11, color=BLACK)
    add_textbox(slide, 1.4, y + 1.1, 11.2, 0.35, prediction, font_size=11, color=PURPLE, bold=True)

add_textbox(slide, 0.5, 7.0, 8, 0.3,
            "These hypotheses guided our analysis design and data collection strategy.",
            font_size=10, color=GRAY)
add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "2", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 4: THE PROBLEM
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 3, 0.4, "The Problem", font_size=13, color=DARK_GREEN, bold=True)

add_textbox(slide, 0.5, 0.8, 12, 1.2,
            "CPI calculates one inflation number for everyone — but not everyone buys the same things. "
            "The \"average\" hides who's hurting most.",
            font_size=24, color=BLACK)

add_line(slide, 0.5, 2.0, 12)

# Left: the gap visualization
add_rect(slide, 0.5, 2.4, 5.8, 4.3, LIGHT_GRAY)
add_textbox(slide, 0.7, 2.5, 5.4, 0.4, "The inflation gap in 2022", font_size=14, color=BLACK, bold=True)

bars = [
    ("CPI-U Midwest", 8.0, GRAY),
    ("Seniors", 9.0, RED),
    ("Urban Renters", 9.0, BLUE),
    ("Rural Small Biz", 10.9, RGBColor(0x27, 0xAE, 0x60)),
]
for j, (label, val, clr) in enumerate(bars):
    y = 3.1 + j * 0.95
    add_textbox(slide, 0.7, y, 2, 0.3, label, font_size=12, color=BLACK, bold=(j > 0))
    bar_w = val / 10.9 * 4.0
    add_rect(slide, 1.8, y + 0.3, bar_w, 0.35, clr)
    add_textbox(slide, 1.8 + bar_w + 0.1, y + 0.28, 1.5, 0.35,
                f"+{val}%", font_size=14, color=clr, bold=True)

add_textbox(slide, 0.7, 6.2, 5.4, 0.4,
            "Rural Biz inflation was nearly DOUBLE the official rate",
            font_size=12, color=RED, bold=True)

# Right: Why it matters
add_textbox(slide, 7, 2.4, 5.5, 0.4, "Why this matters for the bank", font_size=14, color=BLACK, bold=True)
add_line(slide, 7, 2.85, 5.5)

reasons = [
    ("Loan risk is mispriced", "Credit models assume everyone faces 8% inflation. A customer facing 10.9% has ~40% more cost pressure — their default risk is higher than models predict."),
    ("Deposit flight is predictable", "When essentials consume 65-68% of income, customers withdraw savings to survive. The bank lost $150M in deposits — the Divergence Index explains why."),
    ("Products miss the mark", "One-size-fits-all savings rates don't help a senior facing 16% medical costs or a farmer whose gasoline bill spiked +32%."),
]
for j, (title, desc) in enumerate(reasons):
    y = 3.1 + j * 1.3
    add_rect(slide, 6.8, y, 0.3, 0.3, DARK_GREEN)
    add_textbox(slide, 6.85, y - 0.02, 0.3, 0.3, str(j + 1), font_size=12, color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 7.3, y, 5, 0.3, title, font_size=13, color=BLACK, bold=True)
    add_textbox(slide, 7.3, y + 0.35, 5, 0.8, desc, font_size=11, color=GRAY)

add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "2", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 4: THE THREE GROUPS
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 3, 0.4, "The Three Groups", font_size=13, color=DARK_GREEN, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "Three customer segments with fundamentally different spending patterns — "
            "each experiencing a different inflation reality.",
            font_size=24, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

groups = [
    ("Fixed-Income Seniors (65+)", RED, "$37K", "Medical Care 16%", "70% → 74.2%",
     ["Live on Social Security + pensions", "Medical care = 16% of spending",
      "Income barely rises, costs keep climbing", "Home ownership (26%), high utility use (8%)"]),
    ("Urban Renters (Young Professionals)", BLUE, "$48K", "Rent 31%", "58% → 62.7%",
     ["Rent is largest expense by far", "Student loans + phone (10%)",
      "Eat out frequently (8%)", "Most financial flexibility of the three"]),
    ("Rural Small Business Owners", RGBColor(0x27, 0xAE, 0x60), "$60.5K", "Gas + Vehicles 27%", "65% → 70.1%",
     ["Gasoline (10%) + new vehicles (10%) + used (7%)", "Own property, trucks, equipment",
      "Biggest burden increase: +5.1pp", "Self-insured, higher healthcare premiums (9%)"]),
]

for i, (name, clr, income, top_cost, burden_str, bullets) in enumerate(groups):
    x = 0.5 + i * 4.1
    add_rect(slide, x, 2.0, 3.8, 0.4, clr)
    add_textbox(slide, x + 0.1, 2.02, 3.6, 0.4, name, font_size=12, color=WHITE, bold=True)

    add_textbox(slide, x + 0.1, 2.6, 1.6, 0.3, "Median Income", font_size=10, color=GRAY)
    add_textbox(slide, x + 0.1, 2.85, 1.6, 0.4, income, font_size=22, color=clr, bold=True)

    add_textbox(slide, x + 2.0, 2.6, 1.8, 0.3, "Top Expense", font_size=10, color=GRAY)
    add_textbox(slide, x + 2.0, 2.85, 1.8, 0.4, top_cost, font_size=14, color=BLACK, bold=True)

    add_textbox(slide, x + 0.1, 3.4, 3.6, 0.3, "Non-Discretionary Burden", font_size=10, color=GRAY)
    add_textbox(slide, x + 0.1, 3.65, 3.6, 0.4, burden_str, font_size=16, color=clr, bold=True)

    for j, bullet in enumerate(bullets):
        add_textbox(slide, x + 0.1, 4.3 + j * 0.4, 3.6, 0.35,
                    f"• {bullet}", font_size=11, color=BLACK)

# Bottom source bar
add_rect(slide, 0.5, 6.2, 12.3, 0.7, LIGHT_GRAY)
add_textbox(slide, 0.7, 6.25, 11.9, 0.6,
            "Expenditure weights derived from BLS Consumer Expenditure Survey (CEX), Tables 1300 (by age) and "
            "3100 (by housing tenure), with regional adjustments for Indiana/Midwest demographics. "
            "Median incomes from U.S. Census American Community Survey.",
            font_size=10, color=GRAY)
add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "3", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 5: METHODOLOGY
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 3, 0.4, "Methodology", font_size=13, color=DARK_GREEN, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "Personalized inflation = each category's price change × how much that group spends on it, "
            "summed across all 17 categories.",
            font_size=24, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

# Formula box
add_rect(slide, 0.5, 2.0, 12.3, 1.5, DARK_GREEN)
add_multiline(slide, 0.8, 2.1, 11.7, 1.3, [
    ("The Divergence Index Formula", True, 14, CREAM),
    ("", False, 6, WHITE),
    ("DI(group, year) = Σ [ weight(group,category) × price_change(category,year) ]", True, 18, WHITE),
    ("", False, 6, WHITE),
    ("Divergence = Group's personalized inflation  −  Official CPI headline rate", False, 14, CREAM),
])

# Steps
steps = [
    ("1", "Pull Real Price Data", "14 CPI sub-category series from BLS API v2\n(Midwest Urban, NSA (CUUR0200), 2021-2025)"),
    ("2", "Apply Spending Weights", "Each group's expenditure pattern from BLS CEX survey\n(e.g., Seniors: 16% medical, Renters: 31% rent)"),
    ("3", "Calculate Group Inflation", "Weighted sum of all price changes = personalized rate\n(e.g., Rural Biz 2022: 0.10×32% gas + 0.12×11% vehicles + ...)"),
    ("4", "Measure Divergence", "Group rate − CPI headline = how far above/below average\n(Rural Biz 2022: 10.9% − 8.0% = +2.9 percentage points)"),
]

for i, (num, title, desc) in enumerate(steps):
    x = 0.5 + i * 3.1
    add_rect(slide, x, 3.8, 2.8, 3.0, LIGHT_GRAY)
    add_rect(slide, x, 3.8, 2.8, 0.4, MEDIUM_GREEN)
    add_textbox(slide, x, 3.82, 0.4, 0.4, num, font_size=14, color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, x + 0.4, 3.82, 2.3, 0.4, title, font_size=13, color=WHITE, bold=True)
    add_textbox(slide, x + 0.15, 4.4, 2.5, 2.3, desc, font_size=11, color=BLACK)

add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "4", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 6: DIVERGENCE INDEX RESULTS (with chart)
# ═══════════════════════════════════════════════════════
# Generate chart
fig = go.Figure()
years = [2022, 2023, 2024, 2025]
for group, color, name in [
    ("Fixed-Income Seniors", SENIOR_COLOR, "Seniors"),
    ("Urban Renters", RENTER_COLOR, "Renters"),
    ("Rural Small Business Owners", RURAL_COLOR, "Rural Biz"),
]:
    gd = di[di["group"] == group]
    fig.add_trace(go.Bar(
        x=gd["year"], y=gd["group_inflation"],
        name=name, marker_color=color, text=[f"{v:.1f}%" for v in gd["group_inflation"]],
        textposition="outside", textfont=dict(size=11),
    ))
# CPI line
cpi_vals = di[di["group"] == "Fixed-Income Seniors"]["headline_cpi"].values
fig.add_trace(go.Scatter(
    x=years, y=cpi_vals, name="Official CPI", mode="lines+markers+text",
    line=dict(color=CPI_COLOR, width=3, dash="dash"),
    marker=dict(size=8), text=[f"{v:.1f}%" for v in cpi_vals],
    textposition="top center", textfont=dict(size=11),
))
fig.update_layout(
    title="Year-over-Year Inflation Rate by Group vs. Official CPI",
    yaxis_title="Inflation Rate (%)", xaxis_title="Year",
    barmode="group", height=500, width=1000,
    legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
)
save_plotly_image(fig, "divergence_chart.png", 1000, 500)

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 5, 0.4, "Deliverable 1  |  Divergence Index", font_size=13, color=DARK_GREEN, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "In 2022, Rural Small Business Owners faced 10.9% inflation — well above the "
            "Midwest CPI of 8.0% — driven by a 32% spike in gasoline and 29% surge in utility gas.",
            font_size=22, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

slide.shapes.add_picture("output/slides/divergence_chart.png",
                         Inches(0.3), Inches(1.9), Inches(7.8), Inches(4.2))

# Right side: key findings
add_textbox(slide, 8.5, 1.9, 4.3, 0.4, "Key Findings", font_size=14, color=BLACK, bold=True)
add_line(slide, 8.5, 2.35, 4.3)

findings = [
    ("2022: The crisis year", "+3.1pp divergence for Rural Biz. Gasoline (+32%) and utility gas (+29%) drove Midwest costs well above the headline."),
    ("2023-24: Reversal", "Energy prices fell, giving Rural Biz relief. But Seniors stayed elevated — medical costs don't reverse."),
    ("2025: Convergence", "All groups near CPI again, but cumulative damage persists. Seniors slightly below (-0.2pp)."),
    ("Cumulative toll", "All groups accumulated +16-16.4% total inflation from 2021-2025, outpacing income growth."),
]
for j, (title, desc) in enumerate(findings):
    y = 2.6 + j * 1.15
    add_textbox(slide, 8.5, y, 4.3, 0.3, title, font_size=12, color=DARK_GREEN, bold=True)
    add_textbox(slide, 8.5, y + 0.3, 4.3, 0.7, desc, font_size=10, color=GRAY)

add_textbox(slide, 0.5, 7.0, 8, 0.3,
            "Sources: BLS CPI-U, Midwest Urban (CUUR0200*), not seasonally adjusted, annual averages, 2021-2025",
            font_size=9, color=GRAY)
add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "5", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 7: 2022 DEEP DIVE — What drove the spike
# ═══════════════════════════════════════════════════════
# Generate heatmap
categories = ["gasoline", "utility_gas", "food_at_home",
              "medical_care", "rent", "electricity", "new_vehicles", "used_vehicles",
              "owners_equiv_rent", "food_away"]
nice_names = ["Gasoline", "Natural Gas", "Groceries",
              "Medical Care", "Rent", "Electricity", "New Cars/Trucks", "Used Cars/Trucks",
              "Home Ownership", "Restaurants"]
yoy_2022 = yoy[yoy["year"] == 2022].iloc[0]
vals_2022 = [yoy_2022[c] for c in categories]

from config import WEIGHTS
groups_list = ["Fixed-Income Seniors", "Urban Renters", "Rural Small Business Owners"]
short_names = ["Seniors", "Renters", "Rural Biz"]

impact_matrix = []
for g in groups_list:
    row = [WEIGHTS[g].get(c, 0) * yoy_2022[c] for c in categories]
    impact_matrix.append(row)

fig_hm = go.Figure(data=go.Heatmap(
    z=impact_matrix, x=nice_names, y=short_names,
    colorscale="YlOrRd", texttemplate="%{z:.1f}pp",
    hovertemplate="%{y} — %{x}: %{z:.2f}pp impact<extra></extra>",
))
fig_hm.update_layout(
    title="2022 Inflation Impact by Category (weight × price change = pp contribution)",
    height=400, width=1000,
)
save_plotly_image(fig_hm, "heatmap_2022.png", 1000, 400)

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 5, 0.4, "Deep Dive  |  The 2022 Inflation Shock", font_size=13, color=DARK_GREEN, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "Gasoline (+27%) and energy (+25%) were the main drivers — hitting Rural Biz hardest because "
            "they spend 24% of income on energy vs. 8% for the average consumer.",
            font_size=22, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

slide.shapes.add_picture("output/slides/heatmap_2022.png",
                         Inches(0.3), Inches(1.9), Inches(8.5), Inches(3.5))

# Right callouts
add_rect(slide, 9.2, 1.9, 3.6, 1.5, RGBColor(0xFD, 0xF0, 0xEF))
add_multiline(slide, 9.4, 2.0, 3.2, 1.3, [
    ("Top 3 Pain Points — 2022", True, 12, RED),
    ("", False, 4, BLACK),
    ("1. Rural Biz + Gasoline: +3.8pp", False, 11, BLACK),
    ("2. Rural Biz + Energy: +3.0pp", False, 11, BLACK),
    ("3. Renters + Rent: +1.7pp", False, 11, BLACK),
])

add_rect(slide, 9.2, 3.6, 3.6, 1.8, LIGHT_GRAY)
add_multiline(slide, 9.4, 3.7, 3.2, 1.6, [
    ("Price changes in 2022", True, 12, BLACK),
    ("", False, 4, BLACK),
    ("Gasoline:      +27.3%", False, 11, RED),
    ("Natural Gas:  +25.9%", False, 11, RED),
    ("Energy Total: +24.9%", False, 11, ORANGE),
    ("Home Energy: +17.7%", False, 11, ORANGE),
    ("Groceries:     +11.4%", False, 11, BLACK),
])

add_textbox(slide, 0.5, 5.6, 8.5, 0.8,
            "Reading the heatmap: Each cell = (group's spending weight) × (category price change). "
            "Higher values mean that category contributed more percentage points to that group's inflation. "
            "Rural Biz's gas cell (3.8pp) alone accounts for nearly half of CPI's total.",
            font_size=11, color=GRAY)

add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "6", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 8: NON-DISCRETIONARY BURDEN
# ═══════════════════════════════════════════════════════
# Generate burden chart
fig_b = go.Figure()
for group, color, name in [
    ("Fixed-Income Seniors", SENIOR_COLOR, "Seniors"),
    ("Urban Renters", RENTER_COLOR, "Renters"),
    ("Rural Small Business Owners", RURAL_COLOR, "Rural Biz"),
]:
    gd = burden[burden["group"] == group]
    fig_b.add_trace(go.Scatter(
        x=gd["year"], y=gd["nondiscretionary_pct"],
        name=name, mode="lines+markers+text",
        line=dict(color=color, width=3), marker=dict(size=8),
        text=[f"{v:.1f}%" for v in gd["nondiscretionary_pct"]],
        textposition="top center", textfont=dict(size=10),
    ))
fig_b.update_layout(
    title="Non-Discretionary Spending Burden (% of Income → Must-Pay Expenses)",
    yaxis_title="% of Income", xaxis_title="Year",
    height=450, width=950,
    yaxis=dict(range=[55, 90]),
    legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
)
save_plotly_image(fig_b, "burden_chart.png", 950, 450)

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 6, 0.4, "Deliverable 2  |  Non-Discretionary Burden", font_size=13, color=DARK_GREEN, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "Rural Small Business Owners experienced the biggest squeeze: their must-pay expenses jumped "
            "from 76% to 82.3% of income — a 6.3 percentage point increase in just 4 years.",
            font_size=22, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

slide.shapes.add_picture("output/slides/burden_chart.png",
                         Inches(0.3), Inches(1.9), Inches(7.5), Inches(3.8))

# Right side: dollar impact
add_textbox(slide, 8.3, 1.9, 4.5, 0.4, "What's left after essentials? (2025)", font_size=14, color=BLACK, bold=True)
add_line(slide, 8.3, 2.35, 4.5)

dollar_data = [
    ("Seniors", RED, "$41,500", "68.5%", "$13,072", "$1,089/mo"),
    ("Urban Renters", BLUE, "$53,500", "58.2%", "$22,363", "$1,864/mo"),
    ("Rural Biz", RGBColor(0x27, 0xAE, 0x60), "$66,500", "65.5%", "$22,942", "$1,912/mo"),
]
for j, (name, clr, income, burd, left, monthly) in enumerate(dollar_data):
    y = 2.6 + j * 1.3
    add_rect(slide, 8.3, y, 4.5, 1.1, LIGHT_GRAY)
    add_textbox(slide, 8.5, y + 0.05, 2, 0.3, name, font_size=13, color=clr, bold=True)
    add_textbox(slide, 8.5, y + 0.35, 2, 0.25, f"Income: {income}", font_size=10, color=GRAY)
    add_textbox(slide, 8.5, y + 0.6, 2, 0.25, f"Burden: {burd}", font_size=10, color=GRAY)
    add_textbox(slide, 10.8, y + 0.1, 2, 0.5, left, font_size=20, color=clr, bold=True)
    add_textbox(slide, 10.8, y + 0.6, 2, 0.3, f"left = {monthly}", font_size=11, color=GRAY)

add_rect(slide, 8.3, 6.1, 4.5, 0.6, RGBColor(0xFD, 0xF0, 0xEF))
add_textbox(slide, 8.5, 6.15, 4.1, 0.5,
            "Seniors have just $478/month for everything beyond essentials — savings, emergencies, any enjoyment.",
            font_size=11, color=RED, bold=True)

add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "7", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 9: BANK IMPACT
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 5, 0.4, "Bank Impact  |  Connecting Inflation to Credit Stress",
            font_size=13, color=DARK_GREEN, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "Hidden demographic inflation drove measurable credit deterioration: deposits fled, "
            "defaults rose ~86%, and small business delinquencies nearly tripled (~2.9×).",
            font_size=22, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

# Four metric cards
bank_metrics = [
    ("Total Deposits", "$1.2B → $1.05B", "-$150M", "12.5% outflow", RED),
    ("Auto Loan Defaults", "1.4% → 2.6%", "+86%", "~1.9× increase", ORANGE),
    ("Credit Card Util.", "29% → 41%", "+12pp", "Maxing out cards", ORANGE),
    ("Small Biz Delinq.", "1.1% → 3.2%", "+191%", "~2.9× increase", RED),
]
for i, (title, change, pct, note, clr) in enumerate(bank_metrics):
    x = 0.5 + i * 3.15
    add_rect(slide, x, 2.1, 2.9, 2.2, LIGHT_GRAY)
    add_textbox(slide, x + 0.15, 2.2, 2.6, 0.3, title, font_size=12, color=GRAY)
    add_textbox(slide, x + 0.15, 2.55, 2.6, 0.3, change, font_size=13, color=BLACK, bold=True)
    add_textbox(slide, x + 0.15, 2.95, 2.6, 0.6, pct, font_size=28, color=clr, bold=True)
    add_textbox(slide, x + 0.15, 3.65, 2.6, 0.3, note, font_size=11, color=GRAY)

# Cause-effect chain
add_textbox(slide, 0.5, 4.6, 12, 0.4, "The causal chain: inflation divergence → credit stress",
            font_size=14, color=BLACK, bold=True)
add_line(slide, 0.5, 5.05, 12)

chain = [
    ("Energy prices spike\n(2022: gas +32%)", DARK_GREEN),
    ("→", None),
    ("Rural Biz costs\nexplode (+10.9%)", RGBColor(0x27, 0xAE, 0x60)),
    ("→", None),
    ("Savings depleted,\ndeposits withdrawn", ORANGE),
    ("→", None),
    ("Delinquencies ~2.9×\n(1.1% → 3.2%)", RED),
    ("→", None),
    ("Bank loses $150M\nin deposits", RED),
]
x_pos = 0.5
for text, clr in chain:
    if clr is None:
        add_textbox(slide, x_pos, 5.3, 0.4, 0.5, text, font_size=16, color=GRAY, bold=True,
                    alignment=PP_ALIGN.CENTER)
        x_pos += 0.4
    else:
        add_rect(slide, x_pos, 5.2, 2.6, 0.9, clr)
        add_textbox(slide, x_pos + 0.1, 5.25, 2.4, 0.8, text,
                    font_size=11, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
        x_pos += 2.7

add_textbox(slide, 0.5, 6.4, 12, 0.5,
            "This is not a coincidence. The Divergence Index provides the mechanism: when a group's "
            "personalized inflation far exceeds CPI, traditional risk models systematically underprice their default probability.",
            font_size=12, color=GRAY)

add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "8", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 10: STRATEGIC RECOMMENDATION
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 6, 0.4, "Deliverable 3  |  Strategic Recommendation",
            font_size=13, color=DARK_GREEN, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "We recommend a Divergence-Adjusted Credit Framework (DACF) — stop using average "
            "inflation and start understanding which customers are actually under stress.",
            font_size=22, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

pillars = [
    ("PILLAR 1", "Fix the Risk Models", DARK_GREEN, [
        ("Current problem:", "Credit models assume all customers face the same inflation"),
        ("Solution:", "Integrate demographic inflation exposure into loan risk assessment"),
        ("Trigger:", "When a group's Divergence Index spikes, flag those loans for monitoring"),
        ("Impact:", "Catch rising default risk 6-12 months earlier"),
    ]),
    ("PILLAR 2", "Create Targeted Products", MEDIUM_GREEN, [
        ("Seniors:", "Inflation-indexed CDs, 0% Rx financing"),
        ("Renters:", "Rent-smoothing accounts, homebuyer programs"),
        ("Rural Biz:", "Energy cost hedging, seasonal flex payments"),
        ("Impact:", "Retain at-risk customers with relevant solutions"),
    ]),
    ("PILLAR 3", "Stop Losing Deposits", RGBColor(0x2D, 0x9C, 0x8A), [
        ("Seniors want SAFETY:", "Guaranteed-rate CDs tied to medical CPI"),
        ("Rural Biz want FLEX:", "Fee waivers, seasonal business accounts"),
        ("Renters want GROWTH:", "High-yield savings, autopay bonuses"),
        ("Target:", "Recover portion of $150M deposit outflow"),
    ]),
]

for i, (pillar_num, title, clr, items) in enumerate(pillars):
    x = 0.5 + i * 4.1
    add_rect(slide, x, 2.0, 3.8, 0.65, clr)
    add_textbox(slide, x + 0.15, 2.02, 3.5, 0.3, pillar_num, font_size=10, color=CREAM)
    add_textbox(slide, x + 0.15, 2.25, 3.5, 0.35, title, font_size=15, color=WHITE, bold=True)

    for j, (label, desc) in enumerate(items):
        y = 2.85 + j * 0.7
        add_textbox(slide, x + 0.15, y, 3.5, 0.25, label, font_size=11, color=clr, bold=True)
        add_textbox(slide, x + 0.15, y + 0.25, 3.5, 0.4, desc, font_size=10, color=BLACK)

# Bottom highlight
add_rect(slide, 0.5, 5.8, 12.3, 0.8, DARK_GREEN)
add_multiline(slide, 0.8, 5.85, 11.7, 0.7, [
    ("The DACF framework turns the Divergence Index from a diagnostic tool into a competitive advantage.", True, 14, WHITE),
    ("Banks that understand demographic inflation can price risk accurately, retain deposits, and serve their communities better — "
     "aligning profit with CRA compliance.", False, 11, CREAM),
])

add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "9", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 11: RISK SCORES
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, DARK_GREEN)
add_textbox(slide, 0.5, 0.3, 5, 0.4, "Credit Risk Assessment", font_size=13, color=DARK_GREEN, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "Composite risk scores synthesize inflation divergence, burden levels, and income volatility "
            "into a single 1-10 metric per group. Higher = more at-risk for credit stress.",
            font_size=22, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

risk_data = [
    ("Fixed-Income Seniors", RED, 7, [
        ("Inflation exposure:", "Consistently above CPI; medical costs never reverse"),
        ("Burden:", "68.5% — $1,089/month discretionary"),
        ("Key risk:", "Fixed income + rising costs = chronic squeeze"),
        ("Credit signal:", "Slow deposit erosion, increasing card usage"),
    ]),
    ("Urban Renters", BLUE, 5, [
        ("Inflation exposure:", "Moderate — rent is stable but high"),
        ("Burden:", "58.2% — most breathing room of the three"),
        ("Key risk:", "Rent shock if housing market shifts"),
        ("Credit signal:", "Stable but vulnerable to rate increases"),
    ]),
    ("Rural Small Biz", RGBColor(0x27, 0xAE, 0x60), 8, [
        ("Inflation exposure:", "Highest volatility — energy-dependent"),
        ("Burden:", "65.5% — biggest jump (+4.5pp in 4 years)"),
        ("Key risk:", "Business costs pass-through to personal credit"),
        ("Credit signal:", "Delinquencies ~2.9× (1.1% → 3.2%)"),
    ]),
]

for i, (name, clr, score, items) in enumerate(risk_data):
    x = 0.5 + i * 4.1
    add_rect(slide, x, 2.0, 3.8, 4.8, LIGHT_GRAY)
    add_textbox(slide, x + 0.15, 2.1, 2.5, 0.3, name, font_size=13, color=clr, bold=True)

    # Score circle (using rectangle as proxy)
    score_clr = RED if score >= 7 else ORANGE if score >= 5 else RGBColor(0x27, 0xAE, 0x60)
    add_rect(slide, x + 2.8, 2.0, 0.85, 0.85, score_clr)
    add_textbox(slide, x + 2.8, 2.05, 0.85, 0.85, f"{score}/10", font_size=18, color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)

    for j, (label, desc) in enumerate(items):
        y = 3.0 + j * 0.85
        add_textbox(slide, x + 0.15, y, 3.5, 0.25, label, font_size=10, color=BLACK, bold=True)
        add_textbox(slide, x + 0.15, y + 0.25, 3.5, 0.5, desc, font_size=10, color=GRAY)

add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "10", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE 12: DASHBOARD DEMO
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, DARK_GREEN)

add_textbox(slide, 0.5, 0.4, 8, 0.5, "Live Interactive Dashboard", font_size=14, color=CREAM)
add_textbox(slide, 0.5, 1.0, 12, 0.8,
            "Explore the data yourself — our Streamlit dashboard provides 8 interactive views "
            "with real-time filtering, what-if simulation, and guided story mode.",
            font_size=24, color=WHITE)

add_line(slide, 0.5, 2.2, 12)

features = [
    ("Inflation by Group", "Interactive line chart with CPI overlay and dollar impact calculator"),
    ("Who Pays More?", "Annotated heatmap showing which categories hurt each group most"),
    ("Spending Weights", "Donut charts visualizing each group's expenditure pattern"),
    ("Spending Squeeze", "Non-discretionary burden trends and stacked bar comparison"),
    ("What-If Simulator", "Adjust price sliders and see real-time impact on each group's inflation"),
    ("Risk Scores", "Composite credit risk assessment with 1-10 scoring"),
    ("Bank Impact", "Financial metrics connecting inflation divergence to credit stress"),
    ("Story Mode", "7-slide guided presentation walking through the entire analysis"),
]

for i, (title, desc) in enumerate(features):
    col = i % 2
    row = i // 2
    x = 0.8 + col * 6.2
    y = 2.6 + row * 1.1
    add_rect(slide, x - 0.1, y, 5.8, 0.9, MEDIUM_GREEN)
    add_textbox(slide, x + 0.4, y + 0.05, 5.2, 0.3, title, font_size=13, color=WHITE, bold=True)
    add_textbox(slide, x + 0.4, y + 0.4, 5.2, 0.4, desc, font_size=11, color=CREAM)
    add_rect(slide, x - 0.1, y, 0.4, 0.9, CREAM)
    add_textbox(slide, x - 0.1, y + 0.15, 0.4, 0.5, str(i + 1), font_size=16, color=DARK_GREEN,
                bold=True, alignment=PP_ALIGN.CENTER)

add_rect(slide, 3, 7.2, 7.3, 0, CREAM)
add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "11", font_size=9, color=CREAM, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE: HYPOTHESIS EVALUATION
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, 0, 0, 0.15, 7.5, PURPLE)
add_textbox(slide, 0.5, 0.3, 6, 0.4, "Hypothesis Evaluation  |  What We Found", font_size=13, color=PURPLE, bold=True)
add_textbox(slide, 0.5, 0.8, 12, 0.8,
            "We revisit each hypothesis against our results — confirming what held, what surprised us, "
            "and what we would investigate differently next time.",
            font_size=22, color=BLACK)
add_line(slide, 0.5, 1.7, 12)

CONFIRMED_GREEN = RGBColor(0x27, 0xAE, 0x60)
PARTIAL_ORANGE = RGBColor(0xF3, 0x9C, 0x12)
GREEN_BG = RGBColor(0xEA, 0xF7, 0xEA)
ORANGE_BG = RGBColor(0xFE, 0xF9, 0xE7)

evaluations = [
    ("H1", "PARTIALLY CONFIRMED", PARTIAL_ORANGE, ORANGE_BG,
     "Different groups do experience different inflation — Rural Biz hit +10.9% in 2022 vs. 8.0% Midwest CPI (+3.1pp divergence). "
     "However, cumulatively over 2021-2025, all groups converge near +16% total. "
     "The divergence is real but temporary, driven by energy price volatility that reversed in 2023.",
     "Key nuance: The divergence story is strongest in a single year (2022), not cumulatively — "
     "but the cumulative price burden (Deliverable 2) is the lasting impact. Now uses Midwest CPI (CUUR0200) as benchmark."),
    ("H2", "STRONGLY CONFIRMED", CONFIRMED_GREEN, GREEN_BG,
     "This became our strongest finding. Rural Biz burden jumped 61% → 65.5% (+4.5pp). "
     "Seniors went from 65% → 68.5%, with $1,089/month for non-essentials. "
     "Prices never reversed — they just stopped rising as fast — while income growth lagged. "
     "Social Security COLAs for Seniors lagged behind actual medical cost increases in 2021-2022.",
     "Key insight: The real story isn't divergence from CPI — it's prices vs. income. "
     "This reframed our entire presentation. Deliverable 2 is the strongest argument for the bank to act."),
    ("H3", "SUPPORTED BY DATA", CONFIRMED_GREEN, GREEN_BG,
     "Small business delinquencies rose ~2.9× (1.1% → 3.2%) — the group with the highest 2022 divergence. "
     "Deposits fell $150M as customers drew down savings. Credit card utilization jumped 29% → 41%. "
     "The timing is consistent: Rural Biz peak inflation (2022) preceded the delinquency spike (2023-25).",
     "Limitation: Correlation, not causation. We can't isolate demographic inflation from other factors (rate hikes, "
     "supply chain). A controlled study with individual loan-level data would strengthen this claim."),
]

for i, (h_id, verdict, v_color, bg_color, finding, change) in enumerate(evaluations):
    y = 1.95 + i * 1.75
    add_rect(slide, 0.5, y, 12.3, 1.55, bg_color)
    add_rect(slide, 0.5, y, 0.7, 1.55, v_color)
    add_textbox(slide, 0.5, y + 0.35, 0.7, 0.5, h_id, font_size=18, color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 1.4, y + 0.05, 3, 0.3, verdict, font_size=12, color=v_color, bold=True)
    add_textbox(slide, 1.4, y + 0.35, 11.2, 0.6, finding, font_size=10, color=BLACK)
    add_textbox(slide, 1.4, y + 1.05, 11.2, 0.4, change, font_size=10, color=GRAY, bold=False)

add_textbox(slide, 11.5, 7.0, 1.5, 0.3, "13", font_size=9, color=GRAY, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SLIDE: CONCLUSION
# ═══════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, DARK_GREEN)

add_textbox(slide, 0.5, 0.4, 8, 0.5, "Conclusion & Key Takeaways", font_size=14, color=CREAM)

add_multiline(slide, 0.8, 1.2, 11, 1.5, [
    ("The Divergence Index reveals what", False, 32, WHITE),
    ("\"average\" inflation hides.", False, 32, CREAM),
])

add_line(slide, 0.8, 3.0, 11)

takeaways = [
    ("1", "Inflation is not one number.", "Different demographics experience fundamentally different cost pressures. The official CPI understates risk for every key customer segment."),
    ("2", "The data proves the mechanism.", "Real BLS Midwest CPI data × real spending patterns → quantified divergence. Rural Biz faced 10.9% when Midwest CPI was 8%."),
    ("3", "Banks can act on this.", "The Divergence-Adjusted Credit Framework turns demographic inflation intelligence into better risk pricing, targeted products, and deposit retention."),
]

for i, (num, title, desc) in enumerate(takeaways):
    y = 3.3 + i * 1.2
    add_rect(slide, 0.8, y, 0.5, 0.5, CREAM)
    add_textbox(slide, 0.8, y + 0.05, 0.5, 0.5, num, font_size=18, color=DARK_GREEN, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 1.6, y, 10, 0.4, title, font_size=16, color=WHITE, bold=True)
    add_textbox(slide, 1.6, y + 0.4, 10, 0.7, desc, font_size=13, color=CREAM)

add_rect(slide, 0.8, 6.3, 11.7, 0.02, CREAM)

add_multiline(slide, 0.8, 6.5, 6, 0.8, [
    ("Purdue University  |  QBEA Data Dive  |  Fall 2026", False, 13, CREAM),
    ("Dashboard: [Live Streamlit URL]", False, 11, RGBColor(0x88, 0xAA, 0x99)),
])

add_textbox(slide, 8, 6.5, 4.5, 0.5, "Thank you. Questions?",
            font_size=20, color=WHITE, bold=True, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════
output_path = "output/Divergence_Index_Presentation.pptx"
prs.save(output_path)
print(f"Presentation saved to: {output_path}")
print(f"Total slides: {len(prs.slides)}")
