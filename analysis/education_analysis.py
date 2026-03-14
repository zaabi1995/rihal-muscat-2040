"""
Education infrastructure demand model for Muscat Governorate.

Calculates school requirements based on population projections
and school-age demographic ratios.

Data sources:
- MOE Annual Statistics Book 2023/2024: 1,268 government schools nationally
  60,618 teachers (87.5% Omani), 782,818 students
  Source: main.moe.gov.om, omannews.gov.om
- Muscat estimated share: ~25% of national schools
- NCSI Demographic Data (age distribution)
- UNESCO Institute for Statistics (class size benchmarks)
"""

import pandas as pd


# Current capacity - Muscat Governorate estimated
# National: 1,268 government schools (MOE 2023/2024)
# Muscat has ~25% of national schools (est. based on student population share)
CURRENT_SCHOOLS = 317  # 1,268 * 0.25
AVG_SCHOOL_CAPACITY = 615  # Oman avg: 782,818 students / 1,268 schools ≈ 615
CURRENT_YEAR = 2023

# Demographics
SCHOOL_AGE_PCT = 0.18  # Ages 5-18 as % of total population
UNESCO_CLASS_SIZE = 25


def calculate_school_demand(
    population_df: pd.DataFrame,
    school_age_pct: float = SCHOOL_AGE_PCT,
    avg_capacity: int = AVG_SCHOOL_CAPACITY,
) -> pd.DataFrame:
    """
    Calculate school demand for each year in the projection.

    Args:
        population_df: DataFrame with 'year' and 'population' columns
        school_age_pct: Proportion of population aged 5-18
        avg_capacity: Average students per school

    Returns:
        DataFrame with year, population, school_age_pop, schools_needed,
        current_schools, surplus_deficit, capacity_sufficient
    """
    df = population_df.copy()
    df["school_age_pop"] = (df["population"] * school_age_pct).astype(int)
    df["schools_needed"] = (df["school_age_pop"] / avg_capacity).apply(
        lambda x: int(-(-x // 1))  # ceiling division
    )
    df["current_schools"] = CURRENT_SCHOOLS
    df["surplus_deficit"] = df["current_schools"] - df["schools_needed"]
    df["capacity_sufficient"] = df["surplus_deficit"] >= 0

    return df


def find_breakpoint_year(
    population_df: pd.DataFrame,
    school_age_pct: float = SCHOOL_AGE_PCT,
    avg_capacity: int = AVG_SCHOOL_CAPACITY,
) -> dict:
    """
    Find the year when school demand exceeds current capacity.

    Returns dict with breakpoint details.
    """
    df = calculate_school_demand(population_df, school_age_pct, avg_capacity)

    deficit_rows = df[~df["capacity_sufficient"]]

    if deficit_rows.empty:
        return {
            "breakpoint_year": None,
            "message": "Current school capacity sufficient through 2040",
            "gap_at_2040": 0,
        }

    breakpoint = deficit_rows.iloc[0]
    final = df.iloc[-1]

    return {
        "breakpoint_year": int(breakpoint["year"]),
        "school_age_pop_at_breakpoint": int(breakpoint["school_age_pop"]),
        "schools_needed_at_breakpoint": int(breakpoint["schools_needed"]),
        "gap_at_2040": int(abs(final["surplus_deficit"])),
        "schools_needed_2040": int(final["schools_needed"]),
        "school_age_pop_2040": int(final["school_age_pop"]),
    }


def get_capacity_summary(
    population_df: pd.DataFrame,
    school_age_pct: float = SCHOOL_AGE_PCT,
    avg_capacity: int = AVG_SCHOOL_CAPACITY,
) -> dict:
    """
    Get a summary of education capacity analysis.
    """
    breakpoint = find_breakpoint_year(population_df, school_age_pct, avg_capacity)
    final_year = population_df[population_df["year"] == population_df["year"].max()]
    pop_2040 = int(final_year["population"].iloc[0])
    school_age_2040 = int(pop_2040 * school_age_pct)
    schools_needed = int(-(-school_age_2040 // avg_capacity))

    return {
        "current_schools": CURRENT_SCHOOLS,
        "school_age_pct": school_age_pct,
        "avg_capacity": avg_capacity,
        "population_2040": pop_2040,
        "school_age_pop_2040": school_age_2040,
        "schools_needed_2040": schools_needed,
        "gap_2040": schools_needed - CURRENT_SCHOOLS,
        "breakpoint_year": breakpoint.get("breakpoint_year"),
        "new_schools_per_year": max(
            0,
            (schools_needed - CURRENT_SCHOOLS) // (2040 - CURRENT_YEAR),
        ),
    }
