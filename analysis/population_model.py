"""
Population projection model for Muscat Governorate.

Uses official NCSI Population Projections Report (2020-2040) as the
primary source, aligned with Oman Vision 2040.

National projections (NCSI):
- Base year: 2020, 4.47 million total
- Low Growth: 2.8 fertility → 8.1M by 2040
- Moderate Growth: 3.3 fertility → 8.3M by 2040
- High Growth: 4.0 fertility → 8.7M by 2040

Muscat-specific projections (NCSI):
- Omani population: 543,293 (2020) → 783,891 (2040)
- Expatriate increase: ~1,040,000 (2020-2040)
- Total Muscat increase: ~1,281,000 (2020-2040)

Data sources:
- NCSI Population Projections Report (2020-2040)
- NCSI Census 2020: National 4,471,148; Muscat 1,302,440
- Ministry of Housing: Muscat 2040 target ~2.5M
"""

import pandas as pd
import numpy as np


# ============================================================
# OFFICIAL NCSI DATA POINTS
# ============================================================

# National population projections from NCSI (millions)
NCSI_NATIONAL = {
    "Low Growth": {
        "fertility": 2.8,
        "milestones": {2020: 4_471_148, 2025: 5_300_000, 2030: 6_100_000, 2035: 7_000_000, 2040: 8_100_000},
        "description": "Low fertility (2.8), conservative expat growth",
    },
    "Moderate Growth": {
        "fertility": 3.3,
        "milestones": {2020: 4_471_148, 2025: 5_300_000, 2030: 6_100_000, 2035: 7_100_000, 2040: 8_300_000},
        "description": "NCSI baseline - official planning scenario",
    },
    "High Growth": {
        "fertility": 4.0,
        "milestones": {2020: 4_471_148, 2025: 5_300_000, 2030: 6_200_000, 2035: 7_300_000, 2040: 8_700_000},
        "description": "High fertility + full Vision 2040 boom",
    },
}

# Muscat governorate specifics from NCSI
MUSCAT_2020 = 1_302_440  # NCSI Census 2020
MUSCAT_SHARE_2020 = MUSCAT_2020 / 4_471_148  # ~29.1%

# NCSI projects for Muscat specifically:
MUSCAT_OMANI_2020 = 543_293
MUSCAT_OMANI_2040 = 783_891
MUSCAT_EXPAT_INCREASE_2040 = 1_040_000
MUSCAT_2040_NCSI = MUSCAT_2020 + (MUSCAT_OMANI_2040 - MUSCAT_OMANI_2020) + MUSCAT_EXPAT_INCREASE_2040  # ~2.58M

# For backward compat
BASELINE_YEAR = 2020
BASELINE_POPULATION = MUSCAT_2020
TARGET_YEAR = 2040

# Muscat share evolves
MUSCAT_SHARE_2040 = {
    "Low Growth": MUSCAT_2040_NCSI / 8_100_000,
    "Moderate Growth": MUSCAT_2040_NCSI / 8_300_000,
    "High Growth": (MUSCAT_2040_NCSI + 200_000) / 8_700_000,
}

SCENARIOS = {
    "Moderate Growth": {
        "description": "NCSI official baseline (fertility 3.3) - 8.3M national by 2040",
    },
    "High Growth": {
        "description": "NCSI high fertility (4.0) + Vision 2040 boom - 8.7M national",
    },
    "Low Growth": {
        "description": "NCSI low fertility (2.8) + aggressive Omanization - 8.1M national",
    },
}


def _interpolate_milestones(milestones: dict, start_year: int = 2020, end_year: int = 2040) -> pd.DataFrame:
    """Interpolate between NCSI milestone years to get annual figures."""
    milestone_years = sorted(milestones.keys())
    years = list(range(start_year, end_year + 1))
    populations = []

    for year in years:
        if year in milestones:
            populations.append(milestones[year])
        else:
            lower = max(y for y in milestone_years if y <= year)
            upper = min(y for y in milestone_years if y >= year)
            if lower == upper:
                populations.append(milestones[lower])
            else:
                t = (year - lower) / (upper - lower)
                pop = milestones[lower] + t * (milestones[upper] - milestones[lower])
                populations.append(int(round(pop)))

    return pd.DataFrame({"year": years, "population": populations})


def _muscat_from_national(national_df: pd.DataFrame, scenario_name: str) -> pd.DataFrame:
    """Derive Muscat population from national projection using evolving share."""
    share_2020 = MUSCAT_SHARE_2020
    share_2040 = MUSCAT_SHARE_2040.get(scenario_name, 0.31)

    df = national_df.copy()
    muscat_pops = []

    for _, row in df.iterrows():
        year = row["year"]
        t = (year - 2020) / (2040 - 2020)
        share = share_2020 + t * (share_2040 - share_2020)
        muscat_pop = int(round(row["population"] * share))
        muscat_pops.append(muscat_pop)

    df["national_population"] = df["population"]
    df["population"] = muscat_pops
    return df


def project_population(
    growth_rate: float = 0.0,
    migration_rate: float = 0.0,
    baseline_pop: int = MUSCAT_2020,
    start_year: int = 2020,
    end_year: int = 2040,
    scenario: str = "Moderate Growth",
) -> pd.DataFrame:
    """
    Project Muscat population.

    If growth/migration rates are 0, uses official NCSI data.
    Otherwise, applies custom CAGR for user-adjustable scenarios.
    """
    if growth_rate == 0 and migration_rate == 0:
        ncsi = NCSI_NATIONAL.get(scenario, NCSI_NATIONAL["Moderate Growth"])
        national_df = _interpolate_milestones(ncsi["milestones"], start_year, end_year)
        return _muscat_from_national(national_df, scenario)
    else:
        combined_rate = growth_rate + migration_rate
        years = list(range(start_year, end_year + 1))
        populations = []
        for year in years:
            t = year - start_year
            pop = baseline_pop * ((1 + combined_rate) ** t)
            populations.append(int(round(pop)))
        return pd.DataFrame({"year": years, "population": populations})


def get_all_scenarios(
    baseline_pop: int = MUSCAT_2020,
    start_year: int = 2020,
    end_year: int = 2040,
) -> dict[str, pd.DataFrame]:
    """Return NCSI-based projections for all three scenarios (Muscat-derived)."""
    results = {}
    for name in SCENARIOS:
        ncsi = NCSI_NATIONAL[name]
        national_df = _interpolate_milestones(ncsi["milestones"], start_year, end_year)
        muscat_df = _muscat_from_national(national_df, name)
        results[name] = muscat_df
    return results


def get_national_scenarios(
    start_year: int = 2020,
    end_year: int = 2040,
) -> dict[str, pd.DataFrame]:
    """Return NCSI national projections for all scenarios."""
    results = {}
    for name, data in NCSI_NATIONAL.items():
        results[name] = _interpolate_milestones(data["milestones"], start_year, end_year)
    return results


def get_custom_projection(
    growth_rate: float,
    migration_rate: float,
    baseline_pop: int = MUSCAT_2020,
    start_year: int = 2020,
    end_year: int = 2040,
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
    """Calculate historical CAGR between Muscat census data points."""
    data_points = [
        (2003, 632_073),
        (2010, 775_878),
        (2020, 1_302_440),
    ]

    cagrs = {}
    for i in range(len(data_points) - 1):
        y1, p1 = data_points[i]
        y2, p2 = data_points[i + 1]
        years = y2 - y1
        cagr = (p2 / p1) ** (1 / years) - 1
        cagrs[f"{y1}-{y2}"] = round(cagr, 4)

    y1, p1 = data_points[0]
    y2, p2 = data_points[-1]
    cagrs["2003-2020 (overall)"] = round((p2 / p1) ** (1 / (y2 - y1)) - 1, 4)

    return cagrs


def sensitivity_analysis(
    rate_range: tuple = (0.01, 0.06),
    steps: int = 11,
    migration_rate: float = 0.005,
) -> pd.DataFrame:
    """Show how 2040 Muscat population varies across custom growth rates."""
    rates = np.linspace(rate_range[0], rate_range[1], steps)
    results = []

    for rate in rates:
        df = project_population(
            growth_rate=rate,
            migration_rate=migration_rate,
            baseline_pop=MUSCAT_2020,
        )
        pop_2040 = df[df["year"] == TARGET_YEAR]["population"].iloc[0]
        results.append({
            "growth_rate": round(rate, 3),
            "growth_rate_pct": f"{rate*100:.1f}%",
            "migration_rate": migration_rate,
            "projected_2040_population": pop_2040,
        })

    return pd.DataFrame(results)
