"""
Population projection model for Muscat Governorate.

Uses compound annual growth rate (CAGR) with separate natural growth
and net migration components to project population from 2023 to 2040
under three scenarios.

Data sources:
- NCSI Census 2003: 632,073 (citypopulation.de)
- NCSI Census 2010: 775,878 (citypopulation.de)
- NCSI Census 2020: 1,302,440 (citypopulation.de)
- NCSI Yearbook 2024: 1,455,680 for 2023 (gulfmigration.grc.net)
- NCSI via ONA Feb 2025: ~1,500,000 (omannews.gov.om)
"""

import pandas as pd
import numpy as np


# Baseline — using 2023 NCSI yearbook figure (Omani 575,171 + Expat 880,509)
BASELINE_YEAR = 2023
BASELINE_POPULATION = 1_455_680
TARGET_YEAR = 2040

# Pre-defined scenarios
# Calibrated against NCSI population projections and Ministry of Housing
# Muscat 2040 target of ~2.5M. Base case aligns with official planning.
SCENARIOS = {
    "Base Case": {
        "growth_rate": 0.030,
        "migration_rate": 0.005,
        "description": "Aligned with NCSI/MOH 2.5M Muscat target",
    },
    "High Growth": {
        "growth_rate": 0.040,
        "migration_rate": 0.010,
        "description": "Vision 2040 boom, mega projects, high expat inflow",
    },
    "Low Growth": {
        "growth_rate": 0.020,
        "migration_rate": 0.000,
        "description": "Economic slowdown, aggressive Omanization",
    },
}


def project_population(
    growth_rate: float,
    migration_rate: float,
    baseline_pop: int = BASELINE_POPULATION,
    start_year: int = BASELINE_YEAR,
    end_year: int = TARGET_YEAR,
) -> pd.DataFrame:
    """
    Project population using compound growth model.

    Formula: P(t) = P(0) * (1 + g + m)^t
    where g = natural growth rate, m = net migration rate

    Args:
        growth_rate: Annual natural growth rate (e.g. 0.035 for 3.5%)
        migration_rate: Annual net migration rate (e.g. 0.005 for 0.5%)
        baseline_pop: Starting population
        start_year: First year of projection
        end_year: Last year of projection

    Returns:
        DataFrame with columns: year, population
    """
    combined_rate = growth_rate + migration_rate
    years = list(range(start_year, end_year + 1))
    populations = []

    for year in years:
        t = year - start_year
        pop = baseline_pop * ((1 + combined_rate) ** t)
        populations.append(int(round(pop)))

    return pd.DataFrame({"year": years, "population": populations})


def get_all_scenarios(
    baseline_pop: int = BASELINE_POPULATION,
    start_year: int = BASELINE_YEAR,
    end_year: int = TARGET_YEAR,
) -> dict[str, pd.DataFrame]:
    """Return projections for all three scenarios."""
    results = {}
    for name, params in SCENARIOS.items():
        df = project_population(
            growth_rate=params["growth_rate"],
            migration_rate=params["migration_rate"],
            baseline_pop=baseline_pop,
            start_year=start_year,
            end_year=end_year,
        )
        results[name] = df
    return results


def get_custom_projection(
    growth_rate: float,
    migration_rate: float,
    baseline_pop: int = BASELINE_POPULATION,
    start_year: int = BASELINE_YEAR,
    end_year: int = TARGET_YEAR,
) -> pd.DataFrame:
    """Return a single custom projection based on user-defined rates."""
    return project_population(
        growth_rate=growth_rate,
        migration_rate=migration_rate,
        baseline_pop=baseline_pop,
        start_year=start_year,
        end_year=end_year,
    )


def calculate_historical_cagr() -> dict:
    """
    Calculate historical CAGR between census data points
    to validate our assumptions.
    """
    data_points = [
        (2003, 632_073),   # NCSI Census 2003
        (2010, 775_878),   # NCSI Census 2010
        (2020, 1_302_440), # NCSI Census 2020
        (2023, 1_455_680), # NCSI Yearbook 2024 (575,171 Omani + 880,509 expat)
    ]

    cagrs = {}
    for i in range(len(data_points) - 1):
        y1, p1 = data_points[i]
        y2, p2 = data_points[i + 1]
        years = y2 - y1
        cagr = (p2 / p1) ** (1 / years) - 1
        cagrs[f"{y1}-{y2}"] = round(cagr, 4)

    # Overall
    y1, p1 = data_points[0]
    y2, p2 = data_points[-1]
    cagrs["2003-2023 (overall)"] = round((p2 / p1) ** (1 / (y2 - y1)) - 1, 4)

    return cagrs


def sensitivity_analysis(
    rate_range: tuple = (0.01, 0.06),
    steps: int = 11,
    migration_rate: float = 0.005,
) -> pd.DataFrame:
    """
    Show how 2040 population varies across growth rates.

    Returns DataFrame with growth_rate and projected_2040_population.
    """
    rates = np.linspace(rate_range[0], rate_range[1], steps)
    results = []

    for rate in rates:
        df = project_population(growth_rate=rate, migration_rate=migration_rate)
        pop_2040 = df[df["year"] == TARGET_YEAR]["population"].iloc[0]
        results.append(
            {
                "growth_rate": round(rate, 3),
                "growth_rate_pct": f"{rate*100:.1f}%",
                "migration_rate": migration_rate,
                "projected_2040_population": pop_2040,
            }
        )

    return pd.DataFrame(results)
