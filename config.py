"""Configuration for the Divergence Index analysis pipeline."""

# ── BLS API ──
# Register for free at https://registrationdata.bls.gov/registrationForm.do
# Without a key, BLS limits to 25 requests/day (enough for our use)
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
BLS_API_KEY = ""  # Optional: add your key for higher rate limits

# ── FRED API ──
# Register at https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY = ""  # Optional

# ── Analysis Period ──
START_YEAR = 2021
END_YEAR = 2025

# ── BLS Series IDs (U.S. City Average) ──
# Format: CUSR0000SAx for US City Average (seasonally adjusted)
CPI_SERIES = {
    # Food
    "food_at_home":         "CUSR0000SAF11",   # Food at home
    "food_away":            "CUSR0000SEFV",    # Food away from home
    # Housing
    "rent":                 "CUSR0000SEHA",    # Rent of primary residence
    "owners_equiv_rent":    "CUSR0000SEHC",    # Owners' equivalent rent
    "household_energy":     "CUSR0000SAH21",   # Household energy
    # Transportation
    "gasoline":             "CUSR0000SETB01",  # Gasoline (all types)
    "new_vehicles":         "CUSR0000SETA01",  # New vehicles
    "used_vehicles":        "CUSR0000SETA02",  # Used cars and trucks
    "public_transit":       "CUSR0000SETG",    # Public transportation
    # Medical
    "medical_care":         "CUSR0000SAM",     # Medical care
    "medical_services":     "CUSR0000SAM2",    # Medical care services
    # Energy
    "energy":               "CUSR0000SA0E",    # Energy
    "electricity":          "CUSR0000SEHF01",  # Electricity
    "utility_gas":          "CUSR0000SEHF02",  # Utility (piped) gas service
    # Other
    "apparel":              "CUSR0000SAA",     # Apparel
    "recreation":           "CUSR0000SAR",     # Recreation
    "education_comm":       "CUSR0000SAE",     # Education and communication
    "all_items":            "CUSR0000SA0",     # All items (headline CPI)
}

# ── Expenditure Weights by Demographic Group ──
# Based on BLS Consumer Expenditure Survey patterns
# These represent the % of total spending each group allocates per category
# Source: BLS CEX Table 1300 (age), Table 3100 (housing tenure), regional adjustments

WEIGHTS = {
    # NOTE: We use only non-overlapping CPI sub-indices.
    # "household_energy" (CUSR0000SAH21) and "energy" (CUSR0000SA0E) are BLS
    # aggregates that overlap with gasoline, electricity, and utility_gas.
    # Using both the total and the pieces would double-count energy spending.
    # We use the granular series only: gasoline, electricity, utility_gas.
    "Fixed-Income Seniors": {
        "food_at_home":      0.16,    # Seniors cook more at home
        "food_away":         0.04,    # Less dining out
        "rent":              0.06,    # Many own homes, some rent
        "owners_equiv_rent": 0.13,    # Housing maintenance, property taxes
        "gasoline":          0.05,    # Less driving
        "medical_care":      0.20,    # Largest differentiator — Medicare gaps, prescriptions
        "medical_services":  0.08,    # Doctor visits, specialists
        "electricity":       0.07,    # Higher usage (home all day)
        "recreation":        0.05,    # Some leisure spending
        "apparel":           0.02,    # Minimal
        "education_comm":    0.03,    # Phone, internet
        "new_vehicles":      0.02,    # Rare purchases
        "used_vehicles":     0.01,
        "public_transit":    0.01,
        "utility_gas":       0.07,    # Heating (Indiana winters)
    },
    "Urban Renters": {
        "food_at_home":      0.08,
        "food_away":         0.08,    # Young professionals eat out more
        "rent":              0.28,    # Largest expense — rent-burdened
        "owners_equiv_rent": 0.00,    # Renters, not owners
        "gasoline":          0.07,    # Commuting
        "medical_care":      0.04,    # Young, fewer medical costs
        "medical_services":  0.02,
        "electricity":       0.05,    # Apartment electricity
        "recreation":        0.08,    # Entertainment, social
        "apparel":           0.04,    # Professional wardrobe
        "education_comm":    0.09,    # Student loans, phone, internet
        "new_vehicles":      0.04,    # Car payments
        "used_vehicles":     0.03,
        "public_transit":    0.04,    # Some use transit
        "utility_gas":       0.06,    # Heat in apartment
    },
    "Rural Small Business Owners": {
        "food_at_home":      0.12,
        "food_away":         0.06,
        "rent":              0.05,    # Most own property
        "owners_equiv_rent": 0.12,    # Property costs, maintenance
        "gasoline":          0.12,    # Heavy vehicle/equipment fuel usage
        "medical_care":      0.08,    # Self-insured, higher premiums
        "medical_services":  0.05,
        "electricity":       0.07,    # Business electricity costs
        "recreation":        0.04,
        "apparel":           0.02,
        "education_comm":    0.05,
        "new_vehicles":      0.08,    # Trucks, equipment
        "used_vehicles":     0.05,    # Used equipment
        "public_transit":    0.00,    # Rural — no transit
        "utility_gas":       0.09,    # Heating for business and home
    },
}

# ── Non-Discretionary Classification ──
NON_DISCRETIONARY = [
    "food_at_home", "rent", "owners_equiv_rent",
    "gasoline", "medical_care", "medical_services", "electricity",
    "utility_gas",
]

DISCRETIONARY = [
    "food_away", "recreation", "apparel", "education_comm",
    "new_vehicles", "used_vehicles", "public_transit",
]

# ── Hypothetical Bank Data (from case document) ──
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
MEDIAN_INCOMES = {
    "Fixed-Income Seniors": {2021: 32_000, 2022: 33_500, 2023: 35_200, 2024: 36_100, 2025: 37_000},
    "Urban Renters":        {2021: 42_000, 2022: 43_800, 2023: 45_200, 2024: 46_500, 2025: 48_000},
    "Rural Small Business Owners": {2021: 55_000, 2022: 56_500, 2023: 57_800, 2024: 59_000, 2025: 60_500},
}
