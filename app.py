"""
Muscat 2040: Growth & Infrastructure Analysis
Interactive Streamlit dashboard for Rihal CODESTAKER 2026.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from analysis.population_model import (
    project_population,
    get_all_scenarios,
    sensitivity_analysis,
    calculate_historical_cagr,
    SCENARIOS,
    BASELINE_POPULATION,
)
from analysis.healthcare_analysis import (
    calculate_bed_demand,
    find_breakpoint_year as hc_breakpoint,
    get_capacity_summary as hc_summary,
    CURRENT_HOSPITAL_BEDS,
)
from analysis.education_analysis import (
    calculate_school_demand,
    find_breakpoint_year as edu_breakpoint,
    get_capacity_summary as edu_summary,
    CURRENT_SCHOOLS,
)

# --- Page Config ---
st.set_page_config(
    page_title="Muscat 2040 | Growth & Infrastructure",
    page_icon="🏗️",
    layout="wide",
)

# --- Colors ---
TEAL = "#0891B2"
CORAL = "#F97316"
PURPLE = "#8B5CF6"
SCENARIO_COLORS = {
    "Base Case": TEAL,
    "High Growth": CORAL,
    "Low Growth": PURPLE,
}

# --- Header ---
st.title("Muscat 2040: Growth & Infrastructure Analysis")
st.markdown(
    "Interactive planning model for Muscat Governorate's population, "
    "healthcare, and education infrastructure through 2040."
)
st.markdown("---")

# --- Sidebar ---
st.sidebar.header("Adjust Assumptions")
st.sidebar.markdown("Modify the parameters below to explore different scenarios.")

growth_rate = st.sidebar.slider(
    "Natural Growth Rate (%)",
    min_value=1.0,
    max_value=6.0,
    value=3.5,
    step=0.1,
    help="Annual natural population growth rate",
) / 100

migration_rate = st.sidebar.slider(
    "Net Migration Rate (%)",
    min_value=0.0,
    max_value=2.0,
    value=0.5,
    step=0.1,
    help="Annual net migration rate",
) / 100

st.sidebar.markdown("---")
st.sidebar.subheader("Healthcare")

beds_benchmark = st.sidebar.slider(
    "Hospital Beds per 1,000 (target)",
    min_value=1.5,
    max_value=4.0,
    value=3.0,
    step=0.1,
    help="WHO recommends 3.0 beds per 1,000 population",
)

st.sidebar.markdown("---")
st.sidebar.subheader("Education")

school_age_pct = st.sidebar.slider(
    "School-Age Population (%)",
    min_value=15,
    max_value=22,
    value=18,
    step=1,
    help="Population aged 5-18 as percentage of total",
) / 100

avg_school_capacity = st.sidebar.slider(
    "Average School Capacity",
    min_value=300,
    max_value=800,
    value=500,
    step=50,
    help="Average number of students per school",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data Sources:** NCSI, MOH, MOE, WHO, UNESCO  \n"
    "**Baseline:** 1.5M population (2023)"
)

# --- Custom projection from sidebar ---
custom_df = project_population(growth_rate, migration_rate)

# ============================================================
# SECTION 1: Population Projection
# ============================================================
st.header("1. Population Projection (2023-2040)")

scenarios = get_all_scenarios()

# Plot
fig_pop = go.Figure()

for name, df in scenarios.items():
    fig_pop.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["population"],
            name=name,
            mode="lines+markers",
            line=dict(color=SCENARIO_COLORS[name], width=3),
            marker=dict(size=4),
            hovertemplate="%{x}: %{y:,.0f}<extra>" + name + "</extra>",
        )
    )

# Add custom scenario if different from base
combined_custom = growth_rate + migration_rate
combined_base = SCENARIOS["Base Case"]["growth_rate"] + SCENARIOS["Base Case"]["migration_rate"]
if abs(combined_custom - combined_base) > 0.001:
    fig_pop.add_trace(
        go.Scatter(
            x=custom_df["year"],
            y=custom_df["population"],
            name="Your Scenario",
            mode="lines",
            line=dict(color="#10B981", width=3, dash="dash"),
            hovertemplate="%{x}: %{y:,.0f}<extra>Your Scenario</extra>",
        )
    )

fig_pop.update_layout(
    xaxis_title="Year",
    yaxis_title="Population",
    yaxis_tickformat=",",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=450,
    margin=dict(l=20, r=20, t=40, b=20),
)

st.plotly_chart(fig_pop, use_container_width=True)

# Metric cards
col1, col2, col3 = st.columns(3)

for col, (name, df) in zip([col1, col2, col3], scenarios.items()):
    pop_2040 = df[df["year"] == 2040]["population"].iloc[0]
    growth = pop_2040 - BASELINE_POPULATION
    with col:
        st.metric(
            label=f"{name} (2040)",
            value=f"{pop_2040:,.0f}",
            delta=f"+{growth:,.0f} from 2023",
        )

# Comparison table
st.subheader("Scenario Comparison")
comparison_data = []
for name, df in scenarios.items():
    pop_2040 = df[df["year"] == 2040]["population"].iloc[0]
    params = SCENARIOS[name]
    comparison_data.append(
        {
            "Scenario": name,
            "Growth Rate": f"{params['growth_rate']*100:.1f}%",
            "Migration Rate": f"{params['migration_rate']*100:.1f}%",
            "Combined Rate": f"{(params['growth_rate']+params['migration_rate'])*100:.1f}%",
            "2040 Population": f"{pop_2040:,}",
            "Growth from 2023": f"+{pop_2040 - BASELINE_POPULATION:,}",
            "Description": params["description"],
        }
    )

st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

# Historical validation
with st.expander("Historical Growth Rates (validation)"):
    cagrs = calculate_historical_cagr()
    cagr_df = pd.DataFrame(
        [{"Period": k, "CAGR": f"{v*100:.2f}%"} for k, v in cagrs.items()]
    )
    st.dataframe(cagr_df, use_container_width=True, hide_index=True)
    st.caption(
        "The 2010-2020 period saw 5.46% CAGR driven by infrastructure mega-projects "
        "and expatriate labor inflows. The base case of 4.0% combined rate is conservative "
        "relative to recent history."
    )

st.markdown("---")

# ============================================================
# SECTION 2: Healthcare Analysis
# ============================================================
st.header("2. Healthcare Infrastructure")

# Use custom rates for healthcare
hc_df = calculate_bed_demand(custom_df, beds_benchmark)
hc_bp = hc_breakpoint(custom_df, beds_benchmark)
hc_summ = hc_summary(custom_df, beds_benchmark)

col_hc1, col_hc2 = st.columns([2, 1])

with col_hc1:
    fig_hc = go.Figure()

    fig_hc.add_trace(
        go.Scatter(
            x=hc_df["year"],
            y=hc_df["beds_needed"],
            name="Beds Needed",
            mode="lines+markers",
            line=dict(color=CORAL, width=3),
            marker=dict(size=4),
            fill="tonexty" if False else None,
            hovertemplate="%{x}: %{y:,.0f} beds needed<extra></extra>",
        )
    )

    fig_hc.add_trace(
        go.Scatter(
            x=hc_df["year"],
            y=hc_df["current_capacity"],
            name="Current Capacity",
            mode="lines",
            line=dict(color=TEAL, width=3, dash="dash"),
            hovertemplate="%{x}: %{y:,.0f} beds available<extra></extra>",
        )
    )

    # Breakpoint annotation
    bp_year = hc_bp.get("breakpoint_year")
    if bp_year:
        bp_beds = hc_bp.get("beds_needed_at_breakpoint", CURRENT_HOSPITAL_BEDS)
        fig_hc.add_vline(x=bp_year, line_dash="dot", line_color="red", opacity=0.5)
        fig_hc.add_annotation(
            x=bp_year,
            y=bp_beds,
            text=f"Demand exceeds capacity ({bp_year})",
            showarrow=True,
            arrowhead=2,
            ax=60,
            ay=-40,
            font=dict(color="red"),
        )

    fig_hc.update_layout(
        xaxis_title="Year",
        yaxis_title="Hospital Beds",
        yaxis_tickformat=",",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig_hc, use_container_width=True)

with col_hc2:
    st.metric("Current Hospital Beds", f"{CURRENT_HOSPITAL_BEDS:,}")
    st.metric(
        "Beds Needed by 2040",
        f"{hc_summ['beds_needed_2040']:,}",
        delta=f"-{hc_summ['gap_2040']:,} shortfall",
        delta_color="inverse",
    )
    if bp_year:
        st.metric("Capacity Exceeded In", str(bp_year))
    st.metric(
        "New 500-Bed Hospitals Needed",
        str(hc_summ["new_hospitals_needed"]),
    )

    st.info(
        f"At {beds_benchmark:.1f} beds per 1,000, Muscat needs "
        f"**{hc_summ['beds_needed_2040']:,} beds** by 2040 — "
        f"a gap of **{hc_summ['gap_2040']:,}** from current capacity."
    )

st.markdown("---")

# ============================================================
# SECTION 3: Education Analysis
# ============================================================
st.header("3. Education Infrastructure")

edu_df = calculate_school_demand(custom_df, school_age_pct, avg_school_capacity)
edu_bp = edu_breakpoint(custom_df, school_age_pct, avg_school_capacity)
edu_summ = edu_summary(custom_df, school_age_pct, avg_school_capacity)

col_ed1, col_ed2 = st.columns([2, 1])

with col_ed1:
    fig_edu = go.Figure()

    fig_edu.add_trace(
        go.Scatter(
            x=edu_df["year"],
            y=edu_df["schools_needed"],
            name="Schools Needed",
            mode="lines+markers",
            line=dict(color=PURPLE, width=3),
            marker=dict(size=4),
            hovertemplate="%{x}: %{y:,.0f} schools needed<extra></extra>",
        )
    )

    fig_edu.add_trace(
        go.Scatter(
            x=edu_df["year"],
            y=edu_df["current_schools"],
            name="Current Schools",
            mode="lines",
            line=dict(color=TEAL, width=3, dash="dash"),
            hovertemplate="%{x}: %{y:,.0f} schools<extra></extra>",
        )
    )

    bp_year_edu = edu_bp.get("breakpoint_year")
    if bp_year_edu:
        bp_schools = edu_bp.get("schools_needed_at_breakpoint", CURRENT_SCHOOLS)
        fig_edu.add_vline(
            x=bp_year_edu, line_dash="dot", line_color="red", opacity=0.5
        )
        fig_edu.add_annotation(
            x=bp_year_edu,
            y=bp_schools,
            text=f"Demand exceeds capacity ({bp_year_edu})",
            showarrow=True,
            arrowhead=2,
            ax=60,
            ay=-40,
            font=dict(color="red"),
        )

    fig_edu.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Schools",
        yaxis_tickformat=",",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig_edu, use_container_width=True)

with col_ed2:
    st.metric("Current Schools", f"{CURRENT_SCHOOLS}")
    st.metric(
        "Schools Needed by 2040",
        f"{edu_summ['schools_needed_2040']:,}",
        delta=f"-{edu_summ['gap_2040']} shortfall",
        delta_color="inverse",
    )
    if bp_year_edu:
        st.metric("Capacity Exceeded In", str(bp_year_edu))
    st.metric(
        "New Schools per Year",
        str(edu_summ["new_schools_per_year"]),
    )

    st.info(
        f"With {school_age_pct*100:.0f}% school-age population, Muscat needs "
        f"**{edu_summ['schools_needed_2040']}** schools by 2040 — "
        f"**{edu_summ['gap_2040']}** more than today."
    )

st.markdown("---")

# ============================================================
# SECTION 4: Sensitivity Analysis
# ============================================================
st.header("4. Sensitivity Analysis")

st.markdown(
    "How does the 2040 population change as the growth rate varies? "
    "Migration rate held constant at the sidebar value."
)

sens_df = sensitivity_analysis(
    rate_range=(0.01, 0.06), steps=11, migration_rate=migration_rate
)

fig_sens = go.Figure()

fig_sens.add_trace(
    go.Bar(
        x=sens_df["growth_rate_pct"],
        y=sens_df["projected_2040_population"],
        marker_color=[
            PURPLE if r < 0.03 else (TEAL if r < 0.045 else CORAL)
            for r in sens_df["growth_rate"]
        ],
        hovertemplate="Growth: %{x}<br>Population: %{y:,.0f}<extra></extra>",
    )
)

fig_sens.update_layout(
    xaxis_title="Annual Growth Rate",
    yaxis_title="Projected 2040 Population",
    yaxis_tickformat=",",
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
)

st.plotly_chart(fig_sens, use_container_width=True)

# Table
st.dataframe(
    sens_df[["growth_rate_pct", "projected_2040_population"]].rename(
        columns={
            "growth_rate_pct": "Growth Rate",
            "projected_2040_population": "2040 Population",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# --- Footer ---
st.markdown(
    """
    <div style="text-align: center; color: #6B7280; font-size: 0.85rem; padding: 20px 0;">
        Built for <strong>Rihal CODESTAKER 2026</strong> — Data Analytics Challenge<br>
        Data: NCSI, MOH, MOE, WHO, UNESCO
    </div>
    """,
    unsafe_allow_html=True,
)
