# Employee Exit Survey Analysis (DETE vs. TAFE)
## Executive Technical Portfolio Presentation

**Live Application:** https://03employeeexitsurveys.streamlit.app/  
**Duration:** 10 minutes review  
**Audience:** Technical Recruiters and Hiring Managers  
**Date:** 2026-10-03  

---

## Executive Summary and Key Takeaways

1. Tenure-Driven Dissatisfaction Escalation: Employee dissatisfaction scales directly with tenure. Veteran staff with 11 or more years of service resign due to dissatisfaction at over 1.6 times the rate of early-career employees (52.6% vs. 32.6%).
2. Institutional Friction Disparity: The Department of Education (DETE) exhibits significantly higher resignation dissatisfaction (46.5%) compared to the Technical and Further Education institute (TAFE, 30.2%), driven by structural workload fatigue and administrative friction.
3. Schema Harmonization Across Divergent Systems: Successfully consolidated two completely independent survey structures comprising over 6,600 raw survey records and 3,868 voluntary resignations into a unified, high-performance columnar Parquet datastore.

---

## Timed 10-Minute Presentation Agenda

1. Executive Overview and Problem Framing (0:00 - 2:00)
2. Schema Harmonization and Data Dictionary (2:00 - 4:00)
3. Technology Architecture and Package Management (4:00 - 5:00)
4. Interactive Dashboard Walkthrough (5:00 - 8:00)
5. Local Setup, Reproducibility, and Verification (8:00 - 10:00)

---

## 1. Project Overview and Features

This project delivers an end-to-end People Analytics solution quantifying voluntary resignation drivers, career stage vulnerability, and institutional dissatisfaction across Queensland educational bodies.

### Analytical Scope and Business Discipline
This project represents a dedicated **People Analytics and Talent Retention Diagnostics** solution. The system analyzes empirical historical exit survey responses to identify attrition patterns across tenure brackets and quantify specific organizational friction drivers.

- **Analytical Discipline:** People Analytics, Talent Retention Diagnostics, Cross-Institutional Survey Harmonization, Career Stage Vulnerability Modeling.
- **Core Business Questions Answered:**
  1. Does resignation dissatisfaction concentrate among junior employees or experienced senior staff?
  2. How do attrition drivers differ between primary/secondary education (DETE) and vocational training (TAFE)?
  3. Which specific friction factors (workload, leadership, compensation, recognition) contribute most heavily to preventable talent loss?
- **Target Stakeholders:** Chief People Officers, HR Directors, Talent Retention Committees, and Educational Institution Leadership.

### Analytical Capabilities
- Executive Overview: Tracks total resignations, overall dissatisfaction rate, and institutional breakdown with custom Matplotlib career stage bars.
- Tenure and Service Matrix: Evaluates career stage vulnerability (New, Experienced, Established, Veteran) comparing DETE and TAFE cohorts.
- Friction Factor Breakdown: Ranks specific departure drivers including workload fatigue, work-life balance, interpersonal conflict, and private sector moves.
- Institutional Deep Dive: Side-by-side comparison of organizational metrics, average service duration, and high-risk role classifications.
- Survey Record Explorer: Live multi-field text search and filtering across positions, employment types, and administrative regions with CSV export.
- Exploratory Cleaning Notebook: Features an in-depth Jupyter notebook documenting dirty data normalization, regular expression extraction, and statistical findings.

### Visualization Design Rationale: Cleveland and McGill Hierarchy
All dashboard visualizations are constructed using the Matplotlib and Seaborn Object-Oriented API (`fig, ax = plt.subplots(...)`) following empirical graphical perception principles established by Cleveland and McGill (1984):

1. **Position Along a Common Scale:** Horizontal bar charts (`barh`) are used for ranking friction factors and role vulnerability instead of pie charts or radar charts. Human vision decodes differences in position along an aligned axis with the lowest perceptual error, whereas angle and area judgments carry significantly higher cognitive error rates.
2. **Horizontal Label Legibility:** Ranking categories contain lengthy text strings (e.g., "Dissatisfaction with the department", "Physical work environment"). Horizontal orientation ensures labels are read naturally from left to right without awkward vertical tilting, truncation, or clipping.
3. **Aligned Grouped Bars:** Direct comparison between DETE and TAFE is displayed via side-by-side bars sharing identical baseline axes, facilitating immediate ratio comparison across all four career stages.

---

## 2. Survey Data Dictionary and Schema Harmonization

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

<details>
<summary><b>Click to expand career stage definitions</b></summary>

- `New`: Less than 3 years of service at the institute.
- `Experienced`: 3 to 6 years of completed service.
- `Established`: 7 to 10 years of completed service.
- `Veteran`: 11 or more years of completed service.

</details>

---

## 3. Technology Stack

- **Package Management:** Pixi (Conda-forge ecosystem for reproducible cross-platform environments)
- **Runtime:** Python 3.11+
- **Data Engineering:** Pandas, NumPy, PyArrow
- **Visualization:** Matplotlib and Seaborn Object-Oriented API
- **Web Interface:** Streamlit (Apple-inspired Dark Theme configured via `.streamlit/config.toml`)
- **Version Control:** Git, GitHub

---

## 4. System Architecture and Pipeline Flow

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
[src/analytics.py]         [notebooks/*.ipynb]           [streamlit_app.py]
(Pure aggregation math)    (Cleaning walkthrough)        (app.py bridge)
```

<details>
<summary><b>Click to expand codebase directory structure</b></summary>

- `data/download_data.py`: Ingests and generates realistic DETE and TAFE survey samples.
- `src/data_prep.py`: Standardizes schemas, filters resignations, engineers service categories, and exports Parquet tables.
- `src/analytics.py`: Encapsulates pure metric calculations and factor prevalence rankings without modifying data.
- `notebooks/01_exit_survey_cleaning_and_eda.ipynb`: Fully executed exploratory notebook with narrative takeaways and inline charts.
- `streamlit_app.py`: Main dashboard implementation using Matplotlib and Seaborn Object-Oriented charts.
- `app.py`: Backwards-compatible entrypoint forwarding to `streamlit_app.py` for cloud deployments.
- `pixi.toml`: Explicit dependency specifications and executable task commands.
- `requirements.txt`: Streamlit Community Cloud package manifest.
- `.streamlit/config.toml`: Enforces default dark mode (`#0B0C10` background, `#0071E3` electric blue accent).

</details>

---

## 5. Core Analytical Findings and Takeaways

### Tenure Vulnerability Curve
- New staff with under 3 years of service have a 32.6% dissatisfaction rate, primarily resigning for private sector career opportunities.
- Experienced staff (3 to 6 years) show a 36.6% dissatisfaction rate.
- Established staff (7 to 10 years) show a 45.8% dissatisfaction rate.
- Veteran staff with 11 or more years reach a 52.6% dissatisfaction rate, with over half citing job dissatisfaction, workload fatigue, or departmental friction.

### Institutional Disparity
- DETE staff report a 46.5% dissatisfaction rate compared to 30.2% in TAFE.
- Teachers and education delivery roles report the highest dissatisfaction, driven by workload and work-life balance pressure.

### Leading Friction Drivers
- General job dissatisfaction accounts for 25.0% of resignations.
- Private sector career moves account for 22.2% of resignations.
- Workload and administrative fatigue account for 12.5% of resignations.
- Department management friction accounts for 10.8% of resignations.

---

## 6. Local Setup and Execution

### Prerequisites
Install Pixi on your machine:
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

### Setup Commands
1. Navigate to the project directory:
   ```bash
   cd 03_employee_exit_surveys
   ```

2. Install dependencies:
   ```bash
   pixi install
   ```

3. Run data preparation ETL pipeline:
   ```bash
   pixi run data-prep
   ```

4. Launch local Streamlit analytics dashboard:
   ```bash
   pixi run app
   ```
   The application will open at `http://localhost:8501`.

---

## Quick Reference Task Table

| Action | Command | Output |
| :--- | :--- | :--- |
| Ingest Raw Data | `pixi run download-data` | `data/raw/*.csv` |
| Execute ETL Pipeline | `pixi run data-prep` | `data/processed/*.parquet` |
| Launch Dashboard | `pixi run app` | Streamlit Dashboard Server |
| Run Environment Check | `pixi run test` | Environment verification message |
| Run Exploratory Notebook | Open Jupyter in Pixi env | `notebooks/*.ipynb` |
