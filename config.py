"""Configuration for the Divergence Index analysis pipeline."""

# ── BLS API ──
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
BLS_API_KEY = ""  # Optional: add your key for higher rate limits

# ── Analysis Period ──
START_YEAR = 2021
END_YEAR = 2025

# ── BLS Series IDs ──
# Midwest Urban CPI (CUUR0200, NOT seasonally adjusted — BLS does not
# publish SA data at the regional level). Used for group calculations.
# The national CPI-U (CUSR0000SA0) is kept as a comparison benchmark.
CPI_SERIES = {
    # Food — Midwest
    "food_at_home":         "CUUR0200SAF11",   # Food at home, Midwest
    "food_away":            "CUUR0200SEFV",    # Food away from home, Midwest
    # Housing — Midwest
    "rent":                 "CUUR0200SEHA",    # Rent of primary residence, Midwest
    "owners_equiv_rent":    "CUUR0200SEHC",    # Owners' equivalent rent, Midwest
    # Transportation — Midwest
    "gasoline":             "CUUR0200SETB01",  # Gasoline (all types), Midwest
    "new_vehicles":         "CUUR0200SETA01",  # New vehicles, Midwest
    "used_vehicles":        "CUUR0200SETA02",  # Used cars and trucks, Midwest
    "public_transit":       "CUSR0000SETG",    # Public transit — national (Midwest N/A)
    # Medical — Midwest (aggregate only; medical_services is a subset)
    "medical_care":         "CUUR0200SAM",     # Medical care (all), Midwest
    # Utilities — Midwest, granular, non-overlapping
    "electricity":          "CUUR0200SEHF01",  # Electricity, Midwest
    "utility_gas":          "CUUR0200SEHF02",  # Utility (piped) gas, Midwest
    # Other — Midwest
    "apparel":              "CUUR0200SAA",     # Apparel, Midwest
    "recreation":           "CUUR0200SAR",     # Recreation, Midwest
    "education_comm":       "CUUR0200SAE",     # Education and communication, Midwest
    # Headline — Midwest for group benchmark; national kept separately
    "all_items":            "CUUR0200SA0",     # All items, Midwest Urban
}

# National CPI-U for comparison line (different from group calculations)
NATIONAL_CPI_SERIES = "CUSR0000SA0"

# ── Expenditure Weights by Demographic Group ──
#
# Derived from BLS Consumer Expenditure Survey (CEX) 2021:
#   - Table 1300 (by age of reference person)
#   - Table 3100 (by housing tenure)
#
# IMPORTANT: Only non-overlapping CPI sub-indices are used.
#   - medical_care is the aggregate; medical_services is excluded (it's a subset)
#   - electricity and utility_gas are granular; household_energy and energy are excluded
#   - Weights are renormalized to sum to 1.00 across tracked categories only
#   - Not all CEX categories have matching CPI sub-indices (e.g., vehicle insurance,
#     household furnishings). Those are omitted and the remaining weights are scaled up.
#
# The renormalization means these weights overstate tracked categories relative to
# true total spending. This is a known limitation noted in the dashboard.

WEIGHTS = {
    "Fixed-Income Seniors": {
        "food_at_home":      0.11,    # CEX 65+: ~$4,500 / $46K ≈ 9.8%, scaled
        "food_away":         0.06,    # CEX 65+: ~$2,200 ≈ 4.8%, scaled
        "rent":              0.04,    # Mostly homeowners, small renter fraction
        "owners_equiv_rent": 0.26,    # CPI OER weight ~24% Midwest; seniors own outright but
                                      # OER captures rental-equivalent value, not mortgage cost
        "gasoline":          0.05,    # CEX 65+: gas portion of transport
        "medical_care":      0.16,    # CEX 65+: ~$7,000 = 15.3% — single aggregate, no overlap
        "electricity":       0.05,    # CEX 65+: utilities ~$4,000 total; elec ~55%
        "utility_gas":       0.03,    # CEX 65+: natural gas ~35% of utilities
        "recreation":        0.04,    # CEX 65+: ~$2,600, trimmed for shelter rebalance
        "apparel":           0.03,    # CEX 65+: ~$1,000, scaled
        "education_comm":    0.04,    # CEX 65+: phone + internet
        "new_vehicles":      0.05,    # CEX 65+: vehicles, trimmed for shelter rebalance
        "used_vehicles":     0.05,    # Remainder of vehicle spending
        "public_transit":    0.03,    # Small but tracked
    },
    "Urban Renters": {
        "food_at_home":      0.09,    # CEX renters <35, scaled
        "food_away":         0.08,    # Young professionals eat out more
        "rent":              0.31,    # CEX renters <35: shelter ~33%; rent is primary cost
        "owners_equiv_rent": 0.00,    # Renters, not owners
        "gasoline":          0.06,    # Commuting
        "medical_care":      0.06,    # CEX <35: ~$2,500 = ~5%, scaled
        "electricity":       0.04,    # CEX renters: utilities ~6.5%, elec ~55%
        "utility_gas":       0.02,    # Apartment gas heating, lower
        "recreation":        0.07,    # Entertainment, social
        "apparel":           0.03,    # Professional wardrobe
        "education_comm":    0.10,    # Student loans + phone + internet
        "new_vehicles":      0.06,    # Car payments
        "used_vehicles":     0.04,    # Used car portion, trimmed for shelter rebalance
        "public_transit":    0.04,    # Urban transit
    },
    "Rural Small Business Owners": {
        "food_at_home":      0.11,    # CEX Midwest homeowners, scaled
        "food_away":         0.06,    # Less dining out in rural areas
        "rent":              0.02,    # Most own property
        "owners_equiv_rent": 0.24,    # CPI OER weight ~24% Midwest; rural lower housing value
        "gasoline":          0.10,    # Heavy vehicle/equipment fuel — biggest differentiator
        "medical_care":      0.09,    # Self-insured, higher premiums
        "electricity":       0.05,    # Business + home electricity
        "utility_gas":       0.04,    # Heating for business and home
        "recreation":        0.04,    # Some leisure, trimmed for shelter rebalance
        "apparel":           0.03,    # Minimal, scaled
        "education_comm":    0.04,    # Phone, internet, some training
        "new_vehicles":      0.10,    # Trucks, equipment — biggest differentiator
        "used_vehicles":     0.07,    # Used equipment, vehicles
        "public_transit":    0.01,    # Rural — near zero
    },
}

# Verify totals
for _g, _w in WEIGHTS.items():
    _total = sum(_w.values())
    assert abs(_total - 1.0) < 0.011, f"{_g} weights sum to {_total}, expected 1.00"

# ── Non-Discretionary Classification ──
NON_DISCRETIONARY = [
    "food_at_home", "rent", "owners_equiv_rent",
    "gasoline", "medical_care", "electricity", "utility_gas",
]

DISCRETIONARY = [
    "food_away", "recreation", "apparel", "education_comm",
    "new_vehicles", "used_vehicles", "public_transit",
]

# ── Hypothetical Bank Data (from case document — Crossroads Regional Bank) ──
BANK_DATA = {
    2021: {
        "total_retail_deposits": 1_200_000_000,
        "auto_loan_default_rate": 0.014,
        "credit_card_utilization": 0.29,
        "small_biz_delinquencies": 0.011,
    },
    2025: {
        "total_retail_deposits": 1_050_000_000,
        "auto_loan_default_rate": 0.026,
        "credit_card_utilization": 0.41,
        "small_biz_delinquencies": 0.032,
    },
}

# ── Estimated Median Incomes (Indiana, from ACS data) ──
# These must be used consistently everywhere (Dollar Impact uses 2021 base,
# Spending Squeeze uses the year-specific values).
MEDIAN_INCOMES = {
    "Fixed-Income Seniors": {2021: 37_000, 2022: 38_500, 2023: 39_800, 2024: 40_500, 2025: 41_500},
    "Urban Renters":        {2021: 48_000, 2022: 49_500, 2023: 50_800, 2024: 52_000, 2025: 53_500},
    "Rural Small Business Owners": {2021: 60_500, 2022: 62_000, 2023: 63_500, 2024: 64_800, 2025: 66_500},
}
