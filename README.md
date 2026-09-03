# Employee Exit Survey Analysis (DETE vs. TAFE)
## Technical portfolio presentation

**Duration:** 10 minutes review
**Audience:** Technical Recruiters and Hiring Managers
**Date:** 2026-09-03

---

## Agenda

1. Business problem and executive summary (2 min)
2. Survey data dictionary and schema harmonization (2 min)
3. Tech stack (1 min)
4. System architecture and pipeline flow (2 min)
5. Core analytical findings and takeaways (2 min)
6. Installation and reproduction commands (1 min)

---

## 1. Business problem and executive summary

Public education bodies face substantial costs and operational disruptions when experienced personnel depart unexpectedly. In Queensland, Australia, exit surveys were administered by two separate entities:
- **DETE:** Department of Education, Training and Employment (primary & secondary schooling)
- **TAFE:** Technical and Further Education institute (vocational education)

Because the surveys were operated independently, their question schemas, missing value representations, and tenure metrics were incompatible.

### Key project outcomes
- Unified over 6,600 raw survey records and filtered 3,868 voluntary resignations into a standardized columnar table.
- Mapped diverse dissatisfaction indicators into a single reliable metric.
- Discovered that employee dissatisfaction scales directly with tenure: veteran employees (11+ years) resign due to dissatisfaction at over 1.6 times the rate of early-career employees.
- Delivered an interactive Streamlit presentation dashboard built with an Apple-inspired Premium design language.

---

## 2. Survey data dictionary and schema harmonization

The raw surveys presented distinct naming conventions that were normalized during ETL processing:

<details>
<summary><b>Click to expand schema harmonization mapping</b></summary>

| Unified Column | DETE Original Source | TAFE Original Source | Description |
| :--- | :--- | :--- | :--- |
| `id` | `ID` | `Record ID` | Unique participant survey identifier |
| `institute` | Assigned as `'DETE'` | Assigned as `'TAFE'` | Educational institution body |
| `separationtype` | `SeparationType` | `CESSATION REASON` | Reason for departure (filtered for Resignations) |
| `institute_service` | Derived (`cease_year - start_year`) | Parsed from range strings | Total completed service duration in years |
| `service_cat` | Categorized from tenure | Categorized from tenure | Stage (`New`, `Experienced`, `Established`, `Veteran`) |
| `dissatisfied` | Boolean across 10 factors | Boolean across 3 factors | Flag indicating departure driven by dissatisfaction |
| `position` | `Position` | `Classification. Classification` | Professional role category |
| `age_bracket` | Standardized from `Age` | Standardized from `CurrentAge` | Age range (`Under 30`, `30-50`, `50+`) |
| `region` | `Region` | `Institute` campus location | Administrative district or regional institute |

</details>

---

## 3. Tech stack

- **Language:** Python
- **Package Management:** `uv`
- **Data Engineering:** `pandas`, `numpy`, `pyarrow`
- **Visualization & UI:** `plotly`, `streamlit`
- **Interactive Walkthrough:** `jupyter`, `nbformat`
- **Design Aesthetic:** `/premium` (Apple-inspired system typography, clean contrast, zero emojis)

---

## 4. System architecture and pipeline flow

The project enforces strict layer separation. Analytics and UI layers treat all processed Parquet files as read-only.

```text
                                [Raw Survey Records]
                         (data/raw/dete_survey.csv)
                         (data/raw/tafe_survey.csv)
                                     │
                                     ▼ (src/data_prep.py ETL)
                [data/processed/combined_resignations.parquet]
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                            ▼
[src/analytics.py]         [notebooks/*.ipynb]           [app.py Dashboard]
(Pure aggregation math)    (Cleaning walkthrough)        (Interactive Streamlit UI)
```

<details>
<summary><b>Click to expand file layout details</b></summary>

- `data/download_data.py`: Ingests and generates realistic DETE and TAFE survey samples.
- `src/data_prep.py`: Standardizes schemas, filters resignations, engineers service categories, and exports Parquet tables.
- `src/analytics.py`: Encapsulates pure metric calculations and factor prevalence rankings without modifying data.
- `notebooks/01_exit_survey_cleaning_and_eda.ipynb`: Documents the exploratory data cleaning narrative and visual findings.
- `app.py`: Presents an interactive, multi-tab dashboard with live sidebar filters.

</details>

---

## 5. Core analytical findings and takeaways

1. **Tenure Vulnerability Curve:**
   - **New Staff (<3 years):** 32.6% dissatisfaction rate. Primary reasons: external career opportunities in the private sector.
   - **Experienced Staff (3-6 years):** 36.6% dissatisfaction rate.
   - **Established Staff (7-10 years):** 45.8% dissatisfaction rate.
   - **Veteran Staff (11+ years):** 52.6% dissatisfaction rate. Over half of departing senior personnel cite job dissatisfaction, workload fatigue, or departmental friction.
2. **Institutional Disparity:**
   - DETE personnel report an overall dissatisfaction rate of 46.5%, compared to 30.2% in TAFE.
   - Teachers and education delivery roles report the highest dissatisfaction, driven primarily by workload and work-life balance pressure.
3. **Primary Friction Drivers:**
   - General job dissatisfaction (25.0% of resignations).
   - Private sector career competition (22.2% of resignations).
   - Workload and administrative fatigue (12.5% of resignations).
   - Department management friction (10.8% of resignations).

---

## 6. Installation and reproduction commands

You need Python 3.10 or newer and `uv` installed.

### Setup commands
1. Navigate to the project folder:
   ```bash
   cd 03_employee_exit_surveys
   ```
2. Synchronize virtual environment:
   ```bash
   uv sync
   ```
3. Generate raw data and execute the production ETL pipeline:
   ```bash
   uv run python data/download_data.py
   uv run python src/data_prep.py
   ```
4. Launch the local interactive dashboard:
   ```bash
   uv run streamlit run app.py --server.port 8503
   ```

---

## Quick reference card

### Core scripts
| Step | Command |
| :--- | :--- |
| Ingestion | `uv run python data/download_data.py` |
| Production ETL | `uv run python src/data_prep.py` |
| Interactive UI | `uv run streamlit run app.py` |

### Output Parquet files
- Unified Resignations: `data/processed/combined_resignations.parquet`
- Cleaned DETE: `data/processed/dete_clean.parquet`
- Cleaned TAFE: `data/processed/tafe_clean.parquet`
