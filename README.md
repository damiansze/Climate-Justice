# Climate Justice — Who Really Bears the Consequences of Climate Change?

> *"Wer trägt die Konsequenzen des Klimawandels wirklich?"*

A data-driven analysis examining the relationship between greenhouse gas emissions, economic development, and climate vulnerability across 180+ countries from 1995 to 2023.

**Team:** Alexis, Damian, Mila, Sandro  
**Context:** University module on Climate Justice & Data Analysis

---

## Research Questions

- Are the countries driving climate change most the same ones bearing the highest climate risk?
- Which countries are notable outliers?
- Is there a relationship between GDP and climate vulnerability (ND-GAIN)?
- Is there a relationship between GDP and GHG emissions?

---

## Project Structure

```
Climate-Justice/
├── 01_EDA_Preprocessing.ipynb          # Data cleaning & initial EDA
├── 02_EDA_ALL_Postprocessing.ipynb     # EDA on merged dataset
├── 03_Coupling.ipynb                   # GHG–Vulnerability coupling analysis
├── 04_Case_study_Paper3.ipynb          # Reproducing Grecequet et al. (2019)
├── 05_CGI.ipynb                        # Animated change visualizations
├── 06_Case_study_indicator.ipynb       # Deep-dive into individual indicators
├── 07_casestudy_quadrantgraph.ipynb    # Quadrant analysis by median
├── preprocess_and_merge.py             # Data cleaning & merging pipeline
├── data/
│   ├── merged_df.csv                   # Main dataset (182 countries, 1995–2023)
│   ├── EDGAR_GHG_per_capita.csv        # GHG emissions per capita (EDGAR)
│   ├── gain.csv                        # ND-GAIN country index
│   ├── vulnerability.csv               # Climate vulnerability scores
│   ├── gdp_input.csv                   # GDP per capita
│   └── vuln_indicators/                # 45+ detailed vulnerability indicators
├── Poster_Klimaverwundbarkeit.pdf      # Final A0 research poster
└── requirements.txt                    # Python dependencies
```

---

## Notebooks Overview

| Notebook | Description |
|---|---|
| `01_EDA_Preprocessing` | Data validation, missing value analysis, country harmonization across datasets |
| `02_EDA_ALL_Postprocessing` | Distributions, correlations, and temporal trends on the merged dataset |
| `03_Coupling` | Analyzes the (mis)match between who emits GHG and who is most vulnerable |
| `04_Case_study_Paper3` | Reproduces & extends Grecequet et al. (2019) — identifying countries reducing both emissions and vulnerability |
| `05_CGI` | Computes annual change vectors per country, produces an animated global visualization |
| `06_Case_study_indicator` | Examines specific vulnerability indicators (food, water, health, etc.) for outlier countries |
| `07_casestudy_quadrantgraph` | Quadrant plots placing countries by median GHG and vulnerability, tracking movement over time |

---

## Data Sources

| Dataset | Source | Coverage |
|---|---|---|
| GHG Emissions per capita | [EDGAR](https://edgar.jrc.ec.europa.eu/report_2025) | 210 countries, 1995–2023 |
| Climate Vulnerability & Readiness | [ND-GAIN Index](https://gain.nd.edu/our-work/country-index/download-data/) | 192 countries, 1995–2023 |
| GDP per capita | IMF / World Bank | 192 countries, 1995–2023 |
| Detailed Vulnerability Indicators | ND-GAIN sub-indicators | 45+ indicators across 9 categories |

The merged dataset (`data/merged_df.csv`) covers **182 countries** across **29 years** with columns: `ISO3`, `Country`, `Year`, `GHG_per_capita`, `ND_GAIN`, `Vulnerability`, `GDP_per_capita`.

---

## Methodology

1. **Preprocessing** — Harmonize country codes (ISO3), handle missing data, merge four datasets into one long-format table.
2. **Exploratory Data Analysis** — Distributions, correlations, and temporal trends across all variables.
3. **Coupling Analysis** — Quantify the mismatch between GHG emissions and climate vulnerability per country.
4. **Case Study (Grecequet et al.)** — Identify the ~48 countries simultaneously improving on both emissions and vulnerability.
5. **Change Animation** — Compute annual movement vectors to visualize global dynamics from 1995–2023.
6. **Indicator Deep-Dive** — Analyze food, water, health, infrastructure, and ecosystem indicators for outlier countries (Portugal, Vanuatu, Botswana, Somalia).
7. **Quadrant Analysis** — Classify countries into four archetypes by median GHG and vulnerability, and track shifts over time.

---

## Key Finding

Countries that cause the most greenhouse gas emissions are largely **not** the same ones that face the highest climate risks. This mismatch is the central injustice the project quantifies and visualizes.

Around **48 countries** managed to reduce both their GHG emissions per capita and their climate vulnerability between 1995 and 2023 — Grecequet et al. (2019) found ~42 up to 2015.

---

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd Climate-Justice

# Install dependencies
pip install -r requirements.txt

# Run preprocessing (generates data/merged_df.csv)
python preprocess_and_merge.py

# Open notebooks
jupyter lab
```

**Python version:** 3.10+

Key dependencies: `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `geopandas`, `scipy`, `itables`

---

## Outputs

- **Poster:** `Poster_Klimaverwundbarkeit.pdf` — A0 research poster presented at the module finale (06.02.2026)
- **Animation:** `anim_global_median_plus4_HD_zoom_like_screenshot_v3_label_below.mp4` — HD animation of country trajectories from 1995–2023

---

## References

- Grecequet, M. et al. (2019). *Select but diverse countries are reducing both climate vulnerability and CO₂ emissions.* Environmental Research Letters.
- Notre Dame Global Adaptation Initiative (ND-GAIN). Country Index. University of Notre Dame.
- Crippa, M. et al. EDGAR — Emissions Database for Global Atmospheric Research. European Commission, JRC.
- IPCC Assessment Reports on climate impacts and vulnerability.
