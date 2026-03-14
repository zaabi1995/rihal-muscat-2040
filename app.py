"""
Muscat 2040: Growth & Infrastructure Analysis
Interactive Streamlit dashboard for Rihal CODESTAKER 2026.

Uses official NCSI Population Projections Report (2020-2040).
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from analysis.population_model import (
    project_population,
    get_all_scenarios,
    get_national_scenarios,
    sensitivity_analysis,
    calculate_historical_cagr,
    SCENARIOS,
    NCSI_NATIONAL,
    MUSCAT_2020,
    MUSCAT_2040_NCSI,
    MUSCAT_OMANI_2020,
    MUSCAT_OMANI_2040,
    MUSCAT_EXPAT_INCREASE_2040,
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
NAVY = "#1A1A2E"
TEAL = "#009BC1"
GREEN = "#00DE51"
CORAL = "#F97316"
PURPLE = "#8B5CF6"
LIGHT_TEAL = "#00DE51"
SCENARIO_COLORS = {
    "Moderate Growth": TEAL,
    "High Growth": CORAL,
    "Low Growth": PURPLE,
}

# --- Chart template defaults ---
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,25,50,0.4)",
    font=dict(color="#E2E8F0", family="system-ui, -apple-system, sans-serif"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(color="#94A3B8"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(color="#94A3B8"),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0.3)",
        bordercolor="rgba(255,255,255,0.1)",
        borderwidth=1,
        font=dict(color="#E2E8F0"),
    ),
    hoverlabel=dict(
        bgcolor="#1E2D45",
        bordercolor="rgba(0,155,193,0.5)",
        font=dict(color="#E2E8F0", size=13),
    ),
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
/* ---- Base & Background ---- */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #0D1B2A 0%, #1A1A2E 40%, #0F2027 100%);
    min-height: 100vh;
}
[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stMain"] > div {
    padding-top: 0.5rem;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1B2A 0%, #1A2744 100%);
    border-right: 1px solid rgba(0, 155, 193, 0.2);
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] p {
    color: #CBD5E1 !important;
}
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #00DE51 !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: #009BC1;
}

/* ---- Typography ---- */
h1, h2, h3, h4 {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    font-weight: 700 !important;
}
.stMarkdown p {
    color: #CBD5E1;
    font-family: system-ui, -apple-system, sans-serif;
}

/* ---- Metric Cards ---- */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(0,155,193,0.08) 0%, rgba(26,26,46,0.6) 100%);
    border: 1px solid rgba(0,155,193,0.25);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 0 1px rgba(0,155,193,0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,155,193,0.2), 0 0 0 1px rgba(0,155,193,0.15);
}
[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] svg {
    display: none;
}

/* ---- Info / Alert boxes ---- */
.stAlert {
    background: rgba(0,155,193,0.08) !important;
    border: 1px solid rgba(0,155,193,0.3) !important;
    border-radius: 10px !important;
    color: #CBD5E1 !important;
}
.stAlert p {
    color: #CBD5E1 !important;
}

/* ---- Tabs ---- */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid rgba(0,155,193,0.2);
    gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    background: rgba(0,155,193,0.06);
    border: 1px solid rgba(0,155,193,0.15);
    border-radius: 8px 8px 0 0;
    color: #94A3B8 !important;
    font-weight: 500;
    padding: 0.4rem 1.2rem;
    transition: all 0.2s;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,155,193,0.3), rgba(0,222,81,0.1));
    border-color: rgba(0,155,193,0.5);
    color: #00DE51 !important;
    font-weight: 700;
}

/* ---- Dataframe ---- */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(0,155,193,0.2);
}
.dvn-scroller {
    background: rgba(13,27,42,0.6) !important;
}

/* ---- Expander ---- */
[data-testid="stExpander"] {
    background: rgba(0,155,193,0.05);
    border: 1px solid rgba(0,155,193,0.15);
    border-radius: 10px;
}
[data-testid="stExpander"] summary {
    color: #94A3B8 !important;
}

/* ---- Dividers ---- */
hr {
    border: none;
    border-top: 1px solid rgba(0,155,193,0.15);
    margin: 2rem 0;
}

/* ---- Section headers ---- */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1.5rem 0 1rem 0;
}
.section-badge {
    background: linear-gradient(135deg, #009BC1, #00DE51);
    color: #0D1B2A;
    font-weight: 800;
    font-size: 0.75rem;
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER BANNER
# ============================================================
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0D1B2A 0%, #1A1A2E 30%, #0F2744 60%, #003A4F 100%);
    border: 1px solid rgba(0,155,193,0.3);
    border-radius: 16px;
    padding: 2.5rem 2.5rem 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
">
    <!-- Decorative glow blobs -->
    <div style="
        position: absolute; top: -60px; right: -60px;
        width: 250px; height: 250px;
        background: radial-gradient(circle, rgba(0,222,81,0.12) 0%, transparent 70%);
        border-radius: 50%;
    "></div>
    <div style="
        position: absolute; bottom: -40px; left: 20%;
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(0,155,193,0.1) 0%, transparent 70%);
        border-radius: 50%;
    "></div>

    <div style="position: relative; z-index: 1;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.6rem;">
            <div style="
                background: linear-gradient(135deg, #009BC1, #00DE51);
                color: #0D1B2A; font-weight: 800; font-size: 0.7rem;
                padding: 3px 12px; border-radius: 20px; letter-spacing: 0.08em;
                text-transform: uppercase;
            ">Rihal CODESTACKER 2026</div>
            <div style="
                background: rgba(0,155,193,0.15); border: 1px solid rgba(0,155,193,0.3);
                color: #009BC1; font-size: 0.7rem; font-weight: 600;
                padding: 3px 12px; border-radius: 20px;
            ">Data Analytics Challenge</div>
        </div>

        <h1 style="
            font-size: 2.4rem; font-weight: 800; margin: 0 0 0.4rem 0;
            background: linear-gradient(135deg, #F8FAFC 30%, #009BC1 70%, #00DE51 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; line-height: 1.1;
        ">Muscat 2040</h1>
        <h2 style="
            font-size: 1.1rem; font-weight: 400; color: #94A3B8; margin: 0 0 1.2rem 0;
        ">Growth & Infrastructure Analysis</h2>

        <p style="color: #CBD5E1; font-size: 0.95rem; margin: 0; max-width: 700px; line-height: 1.6;">
            Interactive planning model built on <strong style="color:#00DE51;">official NCSI Population Projections
            (2020–2040)</strong> — analyzing Muscat Governorate's healthcare and education
            infrastructure needs through 2040.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# EXECUTIVE SUMMARY
# ============================================================
st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(0,222,81,0.06) 0%, rgba(0,155,193,0.06) 100%);
    border: 1px solid rgba(0,222,81,0.2);
    border-left: 4px solid #00DE51;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
">
    <div style="color: #00DE51; font-weight: 700; font-size: 0.75rem; text-transform: uppercase;
                letter-spacing: 0.08em; margin-bottom: 0.7rem;">Executive Summary</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
        <div>
            <div style="color: #94A3B8; font-size: 0.78rem; text-transform: uppercase;
                        letter-spacing: 0.05em; margin-bottom: 0.2rem;">Population Growth</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 0.9rem;">
                Muscat to grow from <strong style="color:#009BC1;">1.3M → 2.6M</strong> by 2040
                (+98% over 20 years)
            </div>
        </div>
        <div>
            <div style="color: #94A3B8; font-size: 0.78rem; text-transform: uppercase;
                        letter-spacing: 0.05em; margin-bottom: 0.2rem;">Healthcare Gap</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 0.9rem;">
                Need <strong style="color:#F97316;">5,000+ new beds</strong> by 2040 —
                equivalent to 10 major hospitals
            </div>
        </div>
        <div>
            <div style="color: #94A3B8; font-size: 0.78rem; text-transform: uppercase;
                        letter-spacing: 0.05em; margin-bottom: 0.2rem;">Education Gap</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 0.9rem;">
                Require <strong style="color:#8B5CF6;">700+ new schools</strong> —
                37 new schools per year until 2040
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <div style="font-size: 1.2rem; font-weight: 800; color: #F8FAFC;">⚙️ Assumptions</div>
    <div style="font-size: 0.75rem; color: #64748B; margin-top: 4px;">Adjust model parameters</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("#### Custom Growth Rates")
st.sidebar.markdown("_Override NCSI scenarios with your own rates:_")

use_custom = st.sidebar.checkbox("Use custom growth rates", value=False)

growth_rate = 0.0
migration_rate = 0.0

if use_custom:
    growth_rate = st.sidebar.slider(
        "Natural Growth Rate (%)",
        min_value=1.0, max_value=6.0, value=3.5, step=0.1,
    ) / 100

    migration_rate = st.sidebar.slider(
        "Net Migration Rate (%)",
        min_value=0.0, max_value=2.0, value=0.5, step=0.1,
    ) / 100

st.sidebar.markdown("---")
st.sidebar.subheader("Healthcare")

beds_benchmark = st.sidebar.slider(
    "Hospital Beds per 1,000 (target)",
    min_value=1.5, max_value=4.0, value=3.0, step=0.1,
    help="WHO recommends 3.0 beds per 1,000 population",
)

st.sidebar.markdown("---")
st.sidebar.subheader("Education")

school_age_pct = st.sidebar.slider(
    "School-Age Population (%)",
    min_value=15, max_value=22, value=18, step=1,
    help="Population aged 5-18 as percentage of total",
) / 100

avg_school_capacity = st.sidebar.slider(
    "Average School Capacity",
    min_value=300, max_value=800, value=615, step=5,
    help="Oman average: ~615 students per school (MOE 2023)",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Source:** NCSI Population Projections Report (2020-2040)  \n"
    "**Baseline:** 1.30M Muscat population (2020 Census)  \n"
    "**National 2040:** 8.3M (moderate scenario)  \n"
    "**Data:** NCSI, MOH, MOE, WHO, UNESCO"
)

# --- Get default scenario projection for infrastructure ---
default_muscat_df = project_population(scenario="Moderate Growth")
custom_df = project_population(growth_rate, migration_rate) if use_custom else default_muscat_df

# ============================================================
# SECTION 0: NCSI Key Facts
# ============================================================
st.markdown("""
<div class="section-header">
    <span class="section-badge">Official Data</span>
    <span style="font-size: 1.3rem; font-weight: 700; color: #F8FAFC;">
        NCSI Population Projections
    </span>
</div>
""", unsafe_allow_html=True)

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.metric("Oman 2020 (Census)", "4.47M")
with col_b:
    st.metric("Oman 2040 (Moderate)", "8.3M", delta="+3.83M")
with col_c:
    st.metric("Muscat 2020 (Census)", f"{MUSCAT_2020:,}")
with col_d:
    st.metric("Muscat 2040 (NCSI)", f"{MUSCAT_2040_NCSI:,}", delta=f"+{MUSCAT_2040_NCSI - MUSCAT_2020:,}")

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# Population composition donut chart + Muscat breakdown side by side
col_donut, col_breakdown = st.columns([1, 1])

with col_donut:
    st.markdown("<div style='font-weight:600; color:#94A3B8; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;'>Muscat Population Composition</div>", unsafe_allow_html=True)

    omani_2020 = MUSCAT_OMANI_2020
    expat_2020 = MUSCAT_2020 - MUSCAT_OMANI_2020
    omani_2040 = MUSCAT_OMANI_2040
    expat_2040 = MUSCAT_2040_NCSI - MUSCAT_OMANI_2040

    fig_donut = go.Figure()

    fig_donut.add_trace(go.Pie(
        labels=["Omani (2020)", "Expat (2020)"],
        values=[omani_2020, expat_2020],
        hole=0.55,
        domain=dict(x=[0, 0.48]),
        marker=dict(colors=[TEAL, CORAL], line=dict(color="#0D1B2A", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#E2E8F0"),
        hovertemplate="%{label}<br><b>%{value:,}</b> people<extra></extra>",
        showlegend=False,
    ))

    fig_donut.add_trace(go.Pie(
        labels=["Omani (2040)", "Expat (2040)"],
        values=[omani_2040, expat_2040],
        hole=0.55,
        domain=dict(x=[0.52, 1.0]),
        marker=dict(colors=[TEAL, CORAL], line=dict(color="#0D1B2A", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#E2E8F0"),
        hovertemplate="%{label}<br><b>%{value:,}</b> people<extra></extra>",
        showlegend=False,
    ))

    fig_donut.add_annotation(x=0.22, y=0.5, text="2020<br><b>1.30M</b>",
                              showarrow=False, font=dict(size=13, color="#F8FAFC"), align="center")
    fig_donut.add_annotation(x=0.78, y=0.5, text="2040<br><b>2.58M</b>",
                              showarrow=False, font=dict(size=13, color="#F8FAFC"), align="center")

    fig_donut.update_layout(
        **CHART_LAYOUT,
        height=280,
        margin=dict(l=10, r=10, t=20, b=10),
        annotations=fig_donut.layout.annotations,
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_breakdown:
    st.markdown("<div style='font-weight:600; color:#94A3B8; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;'>Muscat Governorate Breakdown</div>", unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Omani 2020", f"{MUSCAT_OMANI_2020:,}")
        st.metric("Omani 2040", f"{MUSCAT_OMANI_2040:,}", delta=f"+{MUSCAT_OMANI_2040 - MUSCAT_OMANI_2020:,}")
    with col_m2:
        expat_2020_val = MUSCAT_2020 - MUSCAT_OMANI_2020
        st.metric("Expatriate 2020", f"{expat_2020_val:,}")
        st.metric("Expat Increase by 2040", f"+{MUSCAT_EXPAT_INCREASE_2040:,}")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.info(
        "NCSI projects Muscat absorbing the largest national share — "
        "primarily driven by **expatriate inflow** tied to economic development. "
        "Life expectancy rises from 76.2 → **79.8 years** by 2040."
    )

# NCSI National table
st.markdown("<div style='font-weight:600; color:#94A3B8; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; margin:1.2rem 0 0.5rem 0;'>National Population by Scenario (NCSI)</div>", unsafe_allow_html=True)
ncsi_table = []
for name, data in NCSI_NATIONAL.items():
    m = data["milestones"]
    ncsi_table.append({
        "Scenario": name,
        "Fertility Rate": f"{data['fertility']} children/woman",
        "2020": f"{m[2020]:,}",
        "2025": f"{m[2025]:,}",
        "2030": f"{m[2030]:,}",
        "2035": f"{m[2035]:,}",
        "2040": f"{m[2040]:,}",
    })
st.dataframe(pd.DataFrame(ncsi_table), use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================================
# SECTION 1: Population Projection Charts
# ============================================================
st.markdown("""
<div class="section-header">
    <span class="section-badge">Section 1</span>
    <span style="font-size: 1.3rem; font-weight: 700; color: #F8FAFC;">
        National & Muscat Population Projections (2020–2040)
    </span>
</div>
""", unsafe_allow_html=True)

# Milestone years for annotations
MILESTONE_YEARS = [2025, 2030, 2035, 2040]

tab_national, tab_muscat = st.tabs(["National (Oman)", "Muscat Governorate"])

with tab_national:
    national_scenarios = get_national_scenarios()
    fig_nat = go.Figure()

    for name, df in national_scenarios.items():
        color = SCENARIO_COLORS[name]
        fig_nat.add_trace(go.Scatter(
            x=df["year"], y=df["population"],
            name=name, mode="lines",
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor=color.replace("#", "rgba(").rstrip(")") + ",0.04)" if color.startswith("#") else color,
            hovertemplate="<b>%{x}</b><br>Population: <b>%{y:,.0f}</b><extra>" + name + "</extra>",
        ))

    # Milestone annotations on moderate line
    mod_df = national_scenarios["Moderate Growth"]
    for yr in MILESTONE_YEARS:
        pop = mod_df[mod_df["year"] == yr]["population"].iloc[0]
        fig_nat.add_annotation(
            x=yr, y=pop,
            text=f"<b>{yr}</b><br>{pop/1e6:.1f}M",
            showarrow=True, arrowhead=2, arrowcolor=TEAL,
            ax=0, ay=-40,
            font=dict(size=11, color=TEAL),
            bgcolor="rgba(13,27,42,0.8)",
            bordercolor=TEAL, borderwidth=1, borderpad=4,
        )

    fig_nat.update_layout(
        **CHART_LAYOUT,
        xaxis_title="Year", yaxis_title="Population",
        yaxis_tickformat=",",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(0,155,193,0.2)", borderwidth=1),
        height=460, margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig_nat, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    for col, (name, data) in zip([col1, col2, col3], NCSI_NATIONAL.items()):
        with col:
            st.metric(
                label=f"{name} (2040)",
                value=f"{data['milestones'][2040]:,}",
                delta=f"+{data['milestones'][2040] - data['milestones'][2020]:,}",
            )

with tab_muscat:
    muscat_scenarios = get_all_scenarios()
    fig_mus = go.Figure()

    for name, df in muscat_scenarios.items():
        color = SCENARIO_COLORS[name]
        fig_mus.add_trace(go.Scatter(
            x=df["year"], y=df["population"],
            name=name, mode="lines",
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor=color.replace("#", "rgba(").rstrip(")") + ",0.04)" if color.startswith("#") else color,
            hovertemplate="<b>%{x}</b><br>Muscat Pop: <b>%{y:,.0f}</b><extra>" + name + "</extra>",
        ))

    if use_custom:
        fig_mus.add_trace(go.Scatter(
            x=custom_df["year"], y=custom_df["population"],
            name="Your Scenario", mode="lines",
            line=dict(color=GREEN, width=2.5, dash="dash"),
            hovertemplate="<b>%{x}</b><br>Muscat Pop: <b>%{y:,.0f}</b><extra>Your Scenario</extra>",
        ))

    # Milestone annotations on moderate line
    mod_mus = muscat_scenarios["Moderate Growth"]
    for yr in MILESTONE_YEARS:
        pop = mod_mus[mod_mus["year"] == yr]["population"].iloc[0]
        fig_mus.add_annotation(
            x=yr, y=pop,
            text=f"<b>{yr}</b><br>{pop/1e6:.2f}M",
            showarrow=True, arrowhead=2, arrowcolor=TEAL,
            ax=0, ay=-40,
            font=dict(size=11, color=TEAL),
            bgcolor="rgba(13,27,42,0.8)",
            bordercolor=TEAL, borderwidth=1, borderpad=4,
        )

    fig_mus.update_layout(
        **CHART_LAYOUT,
        xaxis_title="Year", yaxis_title="Muscat Population",
        yaxis_tickformat=",",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(0,155,193,0.2)", borderwidth=1),
        height=460, margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig_mus, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    for col, (name, df) in zip([col1, col2, col3], muscat_scenarios.items()):
        pop_2040 = df[df["year"] == 2040]["population"].iloc[0]
        with col:
            st.metric(
                label=f"{name} (2040)",
                value=f"{pop_2040:,}",
                delta=f"+{pop_2040 - MUSCAT_2020:,} from 2020",
            )

# Comparison bar chart: current vs projected
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.markdown("<div style='font-weight:600; color:#94A3B8; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;'>Current vs Projected — Scenario Comparison</div>", unsafe_allow_html=True)

col_bar, col_table = st.columns([1, 1])

with col_bar:
    comparison_data = []
    for name, df in muscat_scenarios.items():
        pop_2040 = df[df["year"] == 2040]["population"].iloc[0]
        comparison_data.append({
            "Scenario": name,
            "Fertility Rate": f"{NCSI_NATIONAL[name]['fertility']}",
            "National 2040": f"{NCSI_NATIONAL[name]['milestones'][2040]:,}",
            "Muscat 2040": f"{pop_2040:,}",
            "Muscat Growth": f"+{pop_2040 - MUSCAT_2020:,}",
            "pop_2040_raw": pop_2040,
            "Description": SCENARIOS[name]["description"],
        })

    scenario_names = [d["Scenario"] for d in comparison_data]
    pops_2040 = [d["pop_2040_raw"] for d in comparison_data]
    bar_colors = [SCENARIO_COLORS[n] for n in scenario_names]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="2020 Baseline",
        x=scenario_names,
        y=[MUSCAT_2020] * len(scenario_names),
        marker=dict(color="rgba(148,163,184,0.3)", line=dict(color="rgba(148,163,184,0.5)", width=1)),
        hovertemplate="<b>2020 Baseline</b><br>%{y:,.0f}<extra></extra>",
    ))
    fig_bar.add_trace(go.Bar(
        name="2040 Projected",
        x=scenario_names,
        y=pops_2040,
        marker=dict(color=bar_colors, line=dict(color="#0D1B2A", width=1)),
        hovertemplate="<b>2040 Projection</b><br>%{y:,.0f}<extra></extra>",
    ))

    fig_bar.update_layout(
        **CHART_LAYOUT,
        barmode="overlay",
        yaxis_tickformat=",",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(0,155,193,0.2)", borderwidth=1),
        height=320, margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_table:
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    display_data = [{k: v for k, v in d.items() if k != "pop_2040_raw"} for d in comparison_data]
    st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)

# Historical validation
with st.expander("Historical Growth Rates (Muscat Census Data)"):
    cagrs = calculate_historical_cagr()
    cagr_df = pd.DataFrame([{"Period": k, "CAGR": f"{v*100:.2f}%"} for k, v in cagrs.items()])
    st.dataframe(cagr_df, use_container_width=True, hide_index=True)
    st.caption(
        "The 2010-2020 period saw 5.3% CAGR driven by infrastructure mega-projects. "
        "NCSI official projections use fertility-based models rather than simple CAGR."
    )

st.markdown("---")

# ============================================================
# SECTION 2: Healthcare Analysis
# ============================================================
st.markdown("""
<div class="section-header">
    <span class="section-badge">Section 2</span>
    <span style="font-size: 1.3rem; font-weight: 700; color: #F8FAFC;">
        Healthcare Infrastructure
    </span>
</div>
""", unsafe_allow_html=True)

hc_df = calculate_bed_demand(custom_df, beds_benchmark)
hc_bp = hc_breakpoint(custom_df, beds_benchmark)
hc_summ = hc_summary(custom_df, beds_benchmark)

col_hc1, col_hc2 = st.columns([2, 1])

with col_hc1:
    fig_hc = go.Figure()

    # Fill between lines for gap visualization
    fig_hc.add_trace(go.Scatter(
        x=hc_df["year"], y=hc_df["beds_needed"],
        name="Beds Needed",
        mode="lines",
        line=dict(color=CORAL, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(249,115,22,0.08)",
        hovertemplate="<b>%{x}</b><br>Beds Needed: <b>%{y:,.0f}</b><extra></extra>",
    ))
    fig_hc.add_trace(go.Scatter(
        x=hc_df["year"], y=hc_df["current_capacity"],
        name="Current Capacity",
        mode="lines",
        line=dict(color=TEAL, width=2.5, dash="dash"),
        fill="tozeroy",
        fillcolor="rgba(0,155,193,0.08)",
        hovertemplate="<b>%{x}</b><br>Available: <b>%{y:,.0f}</b><extra></extra>",
    ))

    bp_year = hc_bp.get("breakpoint_year")
    if bp_year:
        bp_beds = hc_bp.get("beds_needed_at_breakpoint", CURRENT_HOSPITAL_BEDS)
        fig_hc.add_vline(x=bp_year, line_dash="dot", line_color="rgba(239,68,68,0.6)", line_width=2)
        fig_hc.add_annotation(
            x=bp_year, y=bp_beds,
            text=f"<b>Capacity Exceeded</b><br>{bp_year}",
            showarrow=True, arrowhead=2, arrowcolor="#EF4444",
            ax=60, ay=-40,
            font=dict(color="#EF4444", size=12),
            bgcolor="rgba(13,27,42,0.85)",
            bordercolor="#EF4444", borderwidth=1, borderpad=4,
        )

    # Add milestone markers
    for yr in MILESTONE_YEARS:
        row = hc_df[hc_df["year"] == yr]
        if not row.empty:
            needed = row["beds_needed"].iloc[0]
            fig_hc.add_annotation(
                x=yr, y=needed,
                text=f"{needed:,.0f}",
                showarrow=False,
                font=dict(size=10, color="#F8FAFC"),
                bgcolor="rgba(249,115,22,0.6)",
                borderpad=3,
                yshift=14,
            )

    fig_hc.update_layout(
        **CHART_LAYOUT,
        xaxis_title="Year", yaxis_title="Hospital Beds",
        yaxis_tickformat=",", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(0,155,193,0.2)", borderwidth=1),
        height=420, margin=dict(l=20, r=20, t=50, b=20),
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
    st.metric("New 500-Bed Hospitals Needed", str(hc_summ["new_hospitals_needed"]))
    st.info(
        f"At **{beds_benchmark:.1f} beds per 1,000**, Muscat needs "
        f"**{hc_summ['beds_needed_2040']:,} beds** by 2040 — "
        f"a gap of **{hc_summ['gap_2040']:,}** from current capacity."
    )

st.markdown("---")

# ============================================================
# SECTION 3: Education Analysis
# ============================================================
st.markdown("""
<div class="section-header">
    <span class="section-badge">Section 3</span>
    <span style="font-size: 1.3rem; font-weight: 700; color: #F8FAFC;">
        Education Infrastructure
    </span>
</div>
""", unsafe_allow_html=True)

edu_df = calculate_school_demand(custom_df, school_age_pct, avg_school_capacity)
edu_bp = edu_breakpoint(custom_df, school_age_pct, avg_school_capacity)
edu_summ = edu_summary(custom_df, school_age_pct, avg_school_capacity)

col_ed1, col_ed2 = st.columns([2, 1])

with col_ed1:
    fig_edu = go.Figure()
    fig_edu.add_trace(go.Scatter(
        x=edu_df["year"], y=edu_df["schools_needed"],
        name="Schools Needed",
        mode="lines",
        line=dict(color=PURPLE, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(139,92,246,0.08)",
        hovertemplate="<b>%{x}</b><br>Schools Needed: <b>%{y:,.0f}</b><extra></extra>",
    ))
    fig_edu.add_trace(go.Scatter(
        x=edu_df["year"], y=edu_df["current_schools"],
        name="Current Schools",
        mode="lines",
        line=dict(color=TEAL, width=2.5, dash="dash"),
        fill="tozeroy",
        fillcolor="rgba(0,155,193,0.08)",
        hovertemplate="<b>%{x}</b><br>Current: <b>%{y:,.0f}</b><extra></extra>",
    ))

    bp_year_edu = edu_bp.get("breakpoint_year")
    if bp_year_edu:
        bp_schools = edu_bp.get("schools_needed_at_breakpoint", CURRENT_SCHOOLS)
        fig_edu.add_vline(x=bp_year_edu, line_dash="dot", line_color="rgba(239,68,68,0.6)", line_width=2)
        fig_edu.add_annotation(
            x=bp_year_edu, y=bp_schools,
            text=f"<b>Capacity Exceeded</b><br>{bp_year_edu}",
            showarrow=True, arrowhead=2, arrowcolor="#EF4444",
            ax=60, ay=-40,
            font=dict(color="#EF4444", size=12),
            bgcolor="rgba(13,27,42,0.85)",
            bordercolor="#EF4444", borderwidth=1, borderpad=4,
        )

    # Add milestone markers
    for yr in MILESTONE_YEARS:
        row = edu_df[edu_df["year"] == yr]
        if not row.empty:
            needed = row["schools_needed"].iloc[0]
            fig_edu.add_annotation(
                x=yr, y=needed,
                text=f"{needed:,.0f}",
                showarrow=False,
                font=dict(size=10, color="#F8FAFC"),
                bgcolor="rgba(139,92,246,0.6)",
                borderpad=3,
                yshift=14,
            )

    fig_edu.update_layout(
        **CHART_LAYOUT,
        xaxis_title="Year", yaxis_title="Number of Schools",
        yaxis_tickformat=",", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(0,155,193,0.2)", borderwidth=1),
        height=420, margin=dict(l=20, r=20, t=50, b=20),
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
    st.metric("New Schools per Year", str(edu_summ["new_schools_per_year"]))
    st.info(
        f"With **{school_age_pct*100:.0f}% school-age population**, Muscat needs "
        f"**{edu_summ['schools_needed_2040']}** schools by 2040 — "
        f"**{edu_summ['gap_2040']}** more than today."
    )

st.markdown("---")

# ============================================================
# SECTION 4: Sensitivity Analysis
# ============================================================
st.markdown("""
<div class="section-header">
    <span class="section-badge">Section 4</span>
    <span style="font-size: 1.3rem; font-weight: 700; color: #F8FAFC;">
        Sensitivity Analysis — Custom Growth Rates
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<p style='color:#94A3B8; margin-bottom:1rem;'>How does the 2040 Muscat population change with different annual growth rates? "
    "This supplements the NCSI official projections above.</p>",
    unsafe_allow_html=True,
)

sens_df = sensitivity_analysis(rate_range=(0.01, 0.06), steps=11, migration_rate=0.005)

col_sens1, col_sens2 = st.columns([2, 1])

with col_sens1:
    # Color scale from purple (low) → teal (mid) → coral (high)
    n = len(sens_df)
    bar_colors_sens = []
    for i, r in enumerate(sens_df["growth_rate"]):
        if r < 0.03:
            bar_colors_sens.append(PURPLE)
        elif r < 0.045:
            bar_colors_sens.append(TEAL)
        else:
            bar_colors_sens.append(CORAL)

    fig_sens = go.Figure()
    fig_sens.add_trace(go.Bar(
        x=sens_df["growth_rate_pct"],
        y=sens_df["projected_2040_population"],
        marker=dict(
            color=bar_colors_sens,
            line=dict(color="#0D1B2A", width=1),
        ),
        text=[f"{p/1e6:.2f}M" for p in sens_df["projected_2040_population"]],
        textposition="outside",
        textfont=dict(color="#CBD5E1", size=10),
        hovertemplate="<b>Growth Rate: %{x}</b><br>2040 Population: <b>%{y:,.0f}</b><extra></extra>",
    ))

    # NCSI moderate reference line
    mod_2040 = muscat_scenarios["Moderate Growth"][muscat_scenarios["Moderate Growth"]["year"] == 2040]["population"].iloc[0]
    fig_sens.add_hline(
        y=mod_2040,
        line_dash="dot", line_color=GREEN, line_width=2,
        annotation_text=f"NCSI Moderate: {mod_2040:,}",
        annotation_position="top right",
        annotation_font=dict(color=GREEN, size=11),
    )

    fig_sens.update_layout(
        **CHART_LAYOUT,
        xaxis_title="Annual Growth Rate",
        yaxis_title="Projected 2040 Muscat Population",
        yaxis_tickformat=",",
        height=380, margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig_sens, use_container_width=True)

with col_sens2:
    st.markdown("<div style='font-weight:600; color:#94A3B8; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;'>Rate → Population Table</div>", unsafe_allow_html=True)
    st.dataframe(
        sens_df[["growth_rate_pct", "projected_2040_population"]].rename(columns={
            "growth_rate_pct": "Growth Rate",
            "projected_2040_population": "2040 Population",
        }).assign(**{"2040 Population": sens_df["projected_2040_population"].apply(lambda x: f"{x:,}")}),
        use_container_width=True, hide_index=True, height=340,
    )

st.markdown("---")

# --- Footer ---
st.markdown(
    """
    <div style="
        text-align: center;
        padding: 2rem 0 1.5rem 0;
        background: linear-gradient(135deg, rgba(0,155,193,0.04) 0%, rgba(0,222,81,0.04) 100%);
        border-radius: 12px;
        border: 1px solid rgba(0,155,193,0.1);
        margin-top: 0.5rem;
    ">
        <div style="font-size: 1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.4rem;">
            Muscat 2040 — Growth &amp; Infrastructure Analysis
        </div>
        <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.3rem;">
            Built for <strong style="color:#009BC1;">Rihal CODESTACKER 2026</strong> — Data Analytics Challenge
        </div>
        <div style="font-size: 0.75rem; color: #475569;">
            Data Sources: NCSI Population Projections (2020-2040) &bull; Ministry of Health &bull;
            Ministry of Education &bull; WHO &bull; UNESCO
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
