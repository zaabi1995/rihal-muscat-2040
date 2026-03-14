"""
Healthcare infrastructure demand model for Muscat Governorate.

Calculates hospital bed requirements based on population projections
and WHO/GCC benchmarks.

Data sources:
- MOH Annual Health Report 2023: 92 hospitals nationally, 7,691 beds total
  (50 MOH hospitals with 5,024 beds + private/other)
  Source: moh.gov.om, omannews.gov.om/topics/en/79/show/118135
- National bed ratio: 14.9 per 10,000 (1.49 per 1,000) as of 2023
- Muscat estimated share: ~35% of national capacity (largest governorate)
- WHO Global Health Observatory (benchmarks)
- WHO EMRO Region Report (GCC averages)
"""

import pandas as pd


# Current capacity - Muscat Governorate estimated
# National: 7,691 beds across 92 hospitals (MOH Annual Report 2023)
# Muscat has ~35% of national capacity (est. based on population share + concentration)
CURRENT_HOSPITAL_BEDS = 2_692  # 7,691 * 0.35
CURRENT_YEAR = 2023

# Benchmarks (beds per 1,000 population)
WHO_BENCHMARK = 3.0
GCC_AVERAGE = 2.2
OMAN_CURRENT_PER_1000 = 1.49  # 14.9 per 10,000 (MOH 2023)


def calculate_bed_demand(
    population_df: pd.DataFrame,
    beds_per_1000: float = WHO_BENCHMARK,
) -> pd.DataFrame:
    """
    Calculate hospital bed demand for each year in the projection.

    Args:
        population_df: DataFrame with 'year' and 'population' columns
        beds_per_1000: Target beds per 1,000 population

    Returns:
        DataFrame with year, population, beds_needed, current_capacity,
        surplus_deficit, and capacity_sufficient columns
    """
    df = population_df.copy()
    df["beds_needed"] = (df["population"] / 1000 * beds_per_1000).astype(int)
    df["current_capacity"] = CURRENT_HOSPITAL_BEDS
    df["surplus_deficit"] = df["current_capacity"] - df["beds_needed"]
    df["capacity_sufficient"] = df["surplus_deficit"] >= 0

    return df


def find_breakpoint_year(
    population_df: pd.DataFrame,
    beds_per_1000: float = WHO_BENCHMARK,
) -> dict:
    """
    Find the year when hospital bed demand exceeds current capacity.

    Returns dict with breakpoint_year, population_at_breakpoint,
    beds_needed_at_breakpoint, and gap_at_2040.
    """
    df = calculate_bed_demand(population_df, beds_per_1000)

    # Find first year where capacity is insufficient
    deficit_rows = df[~df["capacity_sufficient"]]

    if deficit_rows.empty:
        return {
            "breakpoint_year": None,
            "message": "Current capacity sufficient through 2040",
            "gap_at_2040": 0,
        }

    breakpoint = deficit_rows.iloc[0]
    final = df.iloc[-1]

    return {
        "breakpoint_year": int(breakpoint["year"]),
        "population_at_breakpoint": int(breakpoint["population"]),
        "beds_needed_at_breakpoint": int(breakpoint["beds_needed"]),
        "gap_at_2040": int(abs(final["surplus_deficit"])),
        "beds_needed_2040": int(final["beds_needed"]),
        "population_2040": int(final["population"]),
    }


def get_capacity_summary(
    population_df: pd.DataFrame,
    beds_per_1000: float = WHO_BENCHMARK,
) -> dict:
    """
    Get a summary of healthcare capacity analysis.
    """
    breakpoint = find_breakpoint_year(population_df, beds_per_1000)
    final_year = population_df[population_df["year"] == population_df["year"].max()]
    pop_2040 = int(final_year["population"].iloc[0])
    beds_needed_2040 = int(pop_2040 / 1000 * beds_per_1000)

    return {
        "current_beds": CURRENT_HOSPITAL_BEDS,
        "benchmark_used": beds_per_1000,
        "population_2040": pop_2040,
        "beds_needed_2040": beds_needed_2040,
        "gap_2040": beds_needed_2040 - CURRENT_HOSPITAL_BEDS,
        "breakpoint_year": breakpoint.get("breakpoint_year"),
        "new_hospitals_needed": max(
            0, (beds_needed_2040 - CURRENT_HOSPITAL_BEDS) // 500
        ),
    }
