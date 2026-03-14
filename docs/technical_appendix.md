# Technical Appendix

## 1. Data Sources

| Source | Data Used | Reference |
|--------|-----------|-----------|
| National Centre for Statistics and Information (NCSI) | Population census 2003 (632,073), 2010 (775,878), 2020 (1,302,440) | [citypopulation.de/en/oman/admin/01__masqat/](https://www.citypopulation.de/en/oman/admin/01__masqat/) |
| NCSI Statistical Yearbook 2024 | 2023 population estimate (1,455,680: 575,171 Omani + 880,509 expat) | [gulfmigration.grc.net](https://gulfmigration.grc.net) |
| NCSI Population Projections | National 2040 projections: 7.0M-8.7M total; Muscat Omanis 543,293 to 783,891 | NCSI official projections report |
| Ministry of Housing | Muscat 2040 target: ~2.5M population, 2.3M workforce | Urban planning framework |
| NCSI via Oman News Agency | 2025 population estimate (~1.5M) | [omannews.gov.om](https://omannews.gov.om) |
| Ministry of Health (MOH) | National: 92 hospitals, 7,691 beds, 14.9 beds per 10,000 | MOH Annual Health Report 2023 ([omannews.gov.om](https://omannews.gov.om/topics/en/79/show/118135)) |
| Ministry of Education (MOE) | National: 1,268 government schools, 782,818 students, 60,618 teachers | MOE Statistical Yearbook 2023/2024 |
| WHO Global Health Observatory | Hospital bed benchmarks per 1,000 population (3.0 recommended) | [who.int/data/gho](https://www.who.int/data/gho) |
| WHO EMRO Region Report | GCC average healthcare capacity (~2.2 per 1,000) | WHO Eastern Mediterranean Region Health Report |
| UNESCO Institute for Statistics | Class size benchmarks | [uis.unesco.org](http://uis.unesco.org) |

## 2. Assumptions

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Baseline population (2023) | 1,455,680 | NCSI Statistical Yearbook 2024 (575,171 Omani + 880,509 expat) |
| Base case natural growth rate | 3.0% | Calibrated to reach ~2.6M by 2040, aligned with MOH/NCSI targets |
| Base case net migration rate | 0.5% | Conservative; Omanization policies moderate expat inflow |
| High growth natural rate | 4.0% | Vision 2040 mega-project acceleration, high expat inflow |
| High growth migration rate | 1.0% | Large-scale construction and industrial labor demand |
| Low growth natural rate | 2.0% | Economic slowdown scenario, fertility decline |
| Low growth migration rate | 0.0% | Net zero migration under aggressive Omanization |
| Current hospital beds (Muscat) | 2,692 | Estimated: 35% of national 7,691 beds (MOH 2023) |
| Current beds per 1,000 | ~1.8 | 2,692 / 1,456 = 1.85 - 40% below WHO benchmark |
| WHO bed benchmark | 3.0 per 1,000 | WHO recommendation for adequate coverage |
| Current schools (Muscat) | 317 | Estimated: 25% of national 1,268 schools (MOE 2023) |
| Average school capacity | 615 students | Oman actual: 782,818 students / 1,268 schools = 617 |
| School-age population share | 18% | NCSI demographic data, ages 5-18 |

### Notes on Muscat Share Estimates

Muscat Governorate-specific data for hospital beds and schools is not published separately in publicly available MOH/MOE reports. The estimates use:
- **Healthcare (35%):** Muscat hosts the largest share of Oman's healthcare infrastructure including the Royal Hospital, Sultan Qaboos University Hospital, and major private hospitals.
- **Education (25%):** Muscat has approximately one-quarter of Oman's school population, with a slightly lower share than population due to higher private school enrollment.

### Scenario Calibration Against Official Targets

The NCSI projects Muscat's Omani nationals growing from 543,293 (2020) to ~783,891 by 2040, an increase of ~241,000. Expatriates in Muscat are projected to grow by +1,040,863 from 2020 to 2040. Combined with the 2020 base of ~1.3M, this implies ~2.6-2.9M total by 2040.

The Ministry of Housing's Muscat 2040 target of ~2.5M provides the lower bound. Our base case (~2.6M) sits at the upper end of the official planning range, while the high growth scenario (~3.3M) represents a full Vision 2040 boom exceeding official assumptions.

## 3. Methodology

### 3.1 Population Projection Model

The model uses a **compound annual growth rate (CAGR)** formula with two additive components:

```
P(t) = P(0) x (1 + g + m)^t
```

Where:
- `P(0)` = baseline population (1,455,680 in 2023)
- `g` = annual natural growth rate
- `m` = annual net migration rate
- `t` = years from baseline

This approach was chosen over cohort-component models because:
1. Detailed age-sex-specific fertility and mortality data for Muscat Governorate is not publicly available at sufficient granularity.
2. For infrastructure planning over a 17-year horizon, aggregate growth rates provide actionable estimates without false precision.
3. The interactive model allows users to test different rate assumptions, effectively covering the range a more complex model would produce.

**Validation:** Historical CAGRs computed from NCSI census data:
- 2003-2010: 3.0% (pre-boom baseline)
- 2010-2020: 5.3% (infrastructure mega-projects, expatriate labor inflows)
- 2020-2023: 3.8% (post-COVID normalization)
- 2003-2023: 4.3% (full period)

The base case combined rate of 3.5% is deliberately conservative relative to the full-period average (4.3%), aligned with official planning targets. The high growth scenario at 5.0% approaches but does not exceed the observed 2010-2020 boom rate.

### 3.2 Healthcare Demand Model

```
Beds_needed(t) = P(t) / 1000 x benchmark_rate
```

- `benchmark_rate` defaults to WHO standard of 3.0 beds per 1,000
- Current capacity is treated as fixed (2,692 beds) to show the gap
- Current ratio: ~1.85 beds per 1,000 (40% below WHO benchmark)
- The breakpoint year is when `Beds_needed > Current_capacity`
- New hospitals estimated as: `gap / 500` (assuming 500-bed standard facility)

### 3.3 Education Demand Model

```
School_age_pop(t) = P(t) x school_age_pct
Schools_needed(t) = ceil(School_age_pop(t) / avg_capacity)
```

- `school_age_pct` = 0.18 (ages 5-18, NCSI demographic data)
- `avg_capacity` = 615 students per school (Oman actual average: 782,818 / 1,268)
- Breakpoint year is when `Schools_needed > Current_schools`
- Annual construction rate = `gap / years_remaining`

### 3.4 Sensitivity Analysis

Growth rate is varied from 1.0% to 6.0% in 0.5% increments while holding migration rate constant, producing a range of 2040 population estimates. This shows the model's sensitivity to the most uncertain parameter.

## 4. Limitations

1. **Linear growth rate assumption.** Real population growth is non-linear - it may accelerate with mega-projects (SOHAR FZ, Duqm spillover) or decelerate with economic cycles. The three scenarios partially address this.

2. **Fixed infrastructure baseline.** The model assumes current capacity remains unchanged. In reality, some expansion is already planned or underway. The gap figures should be interpreted as "additional beyond what exists today."

3. **No spatial distribution.** Muscat's wilayats (Seeb, Bawshar, Muttrah, Al Amerat, Muscat, Quriyat) have vastly different growth rates. A more granular model would project demand by wilayat to optimize facility placement.

4. **School-age ratio held constant.** In practice, demographic transition may shift the age pyramid. If fertility declines faster than expected, the 18% school-age share could drop to 15-16%.

5. **Muscat share estimates.** Hospital beds and school counts for Muscat are estimated shares of national totals, as governorate-level breakdowns are not separately published in publicly available reports.

6. **Expatriate share declining.** NCSI projects expatriates dropping from ~50% of Oman's population today to ~33% by 2040 under Omanization policies. This could moderate Muscat's growth more than our base case assumes.

## 5. How to Reproduce

```bash
# Clone the repository
git clone https://github.com/zaabi1995/rihal-muscat-2040.git
cd rihal-muscat-2040

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`. Use the sidebar sliders to adjust assumptions and explore scenarios interactively.

## 6. Project Structure

```
muscat-2040/
├── app.py                          # Streamlit dashboard
├── analysis/
│   ├── __init__.py
│   ├── population_model.py         # CAGR projection with 3 scenarios
│   ├── healthcare_analysis.py      # Bed demand vs capacity
│   └── education_analysis.py       # School demand vs capacity
├── data/
│   ├── population_baseline.csv     # Census data points
│   ├── healthcare_capacity.csv     # Current hospital beds
│   └── education_capacity.csv      # Current school capacity
├── docs/
│   ├── executive_summary.md        # 2-page decision-maker brief
│   └── technical_appendix.md       # This document
├── requirements.txt
├── README.md
└── .gitignore
```
