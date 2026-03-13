# Technical Appendix

## 1. Data Sources

| Source | Data Used | Reference |
|--------|-----------|-----------|
| National Centre for Statistics and Information (NCSI) | Population census 2003, 2010; Statistical Yearbook 2020; 2023 estimate | [data.gov.om](https://data.gov.om) |
| Ministry of Health (MOH) | Hospital bed count, Muscat Governorate | MOH Annual Health Report 2023 |
| Ministry of Education (MOE) | School count and capacity, Muscat | MOE Statistical Yearbook 2023 |
| WHO Global Health Observatory | Hospital bed benchmarks per 1,000 population | [who.int/data/gho](https://www.who.int/data/gho) |
| WHO EMRO Region Report | GCC average healthcare capacity | WHO Eastern Mediterranean Region Health Report |
| UNESCO Institute for Statistics | Class size benchmarks | [uis.unesco.org](http://uis.unesco.org) |

## 2. Assumptions

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Baseline population (2023) | 1,500,000 | NCSI estimate for Muscat Governorate |
| Base case natural growth rate | 3.5% | Below 2010-2020 CAGR of 5.5%, reflecting economic maturation |
| Base case net migration rate | 0.5% | Conservative estimate; Omanization policies moderate expat inflow |
| High growth natural rate | 4.5% | Assumes Vision 2040 mega-project acceleration |
| High growth migration rate | 1.0% | Large-scale construction and industrial labor demand |
| Low growth natural rate | 2.0% | Economic slowdown scenario, fertility decline |
| Low growth migration rate | 0.0% | Net zero migration under restrictive labor policies |
| Current hospital beds | 4,200 | MOH Annual Report 2023 |
| WHO bed benchmark | 3.0 per 1,000 | WHO recommendation for adequate coverage |
| Current schools (Muscat) | 550 | MOE 2023, includes public and private |
| Average school capacity | 500 students | MOE standard |
| School-age population share | 18% | NCSI demographic data, ages 5-18 |

## 3. Methodology

### 3.1 Population Projection Model

The model uses a **compound annual growth rate (CAGR)** formula with two additive components:

```
P(t) = P(0) x (1 + g + m)^t
```

Where:
- `P(0)` = baseline population (1,500,000 in 2023)
- `g` = annual natural growth rate
- `m` = annual net migration rate
- `t` = years from baseline

This approach was chosen over cohort-component models because:
1. Detailed age-sex-specific fertility and mortality data for Muscat Governorate is not publicly available at sufficient granularity.
2. For infrastructure planning over a 17-year horizon, aggregate growth rates provide actionable estimates without false precision.
3. The interactive model allows users to test different rate assumptions, effectively covering the range a more complex model would produce.

**Validation:** The historical CAGR from 2003-2023 was 4.42%. The base case combined rate of 4.0% is deliberately conservative, while the high growth scenario at 5.5% matches the observed 2010-2020 boom period.

### 3.2 Healthcare Demand Model

```
Beds_needed(t) = P(t) / 1000 x benchmark_rate
```

- `benchmark_rate` defaults to WHO standard of 3.0 beds per 1,000
- Current capacity is treated as fixed (4,200 beds) to show the gap
- The breakpoint year is when `Beds_needed > Current_capacity`
- New hospitals estimated as: `gap / 500` (assuming 500-bed standard facility)

### 3.3 Education Demand Model

```
School_age_pop(t) = P(t) x school_age_pct
Schools_needed(t) = ceil(School_age_pop(t) / avg_capacity)
```

- `school_age_pct` = 0.18 (ages 5-18, NCSI demographic data)
- `avg_capacity` = 500 students per school (MOE standard)
- Breakpoint year is when `Schools_needed > Current_schools`
- Annual construction rate = `gap / years_remaining`

### 3.4 Sensitivity Analysis

Growth rate is varied from 1.0% to 6.0% in 0.5% increments while holding migration rate constant, producing a range of 2040 population estimates. This shows the model's sensitivity to the most uncertain parameter.

## 4. Limitations

1. **Linear growth rate assumption.** Real population growth is non-linear — it may accelerate with mega-projects (SOHAR FZ, Duqm spillover) or decelerate with economic cycles. The three scenarios partially address this.

2. **Fixed infrastructure baseline.** The model assumes current capacity remains unchanged. In reality, some expansion is already planned or underway. The gap figures should be interpreted as "additional beyond what exists today."

3. **No spatial distribution.** Muscat's wilayats (Seeb, Bawshar, Muttrah, Al Amerat, Muscat, Quriyat) have vastly different growth rates. A more granular model would project demand by wilayat to optimize facility placement.

4. **School-age ratio held constant.** In practice, demographic transition may shift the age pyramid. If fertility declines faster than expected, the 18% school-age share could drop to 15-16%.

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
