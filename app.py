import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add src folder to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from analytics import (
    get_kpi_summary,
    get_dissatisfaction_by_service,
    get_dissatisfaction_by_institute,
    get_resignation_factor_breakdown,
    get_demographics_breakdown
)

# Page configuration
st.set_page_config(
    page_title="Employee Exit Survey Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Apple-inspired CSS styling overrides
st.html("""
<style>
/* Base app container */
.stApp {
    background-color: #0B0C10 !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif !important;
}

/* Premium KPI Card */
div[data-testid="stMetric"] {
    background: #16181F !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #86868B !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

div[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #F5F5F7 !important;
}

/* Tab headers styling */
button[data-baseweb="tab"] {
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    color: #86868B !important;
    padding: 10px 18px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #F5F5F7 !important;
    border-bottom: 2px solid #0071E3 !important;
}

/* Headers */
h1, h2, h3, h4 {
    color: #F5F5F7 !important;
    letter-spacing: -0.02em !important;
}

/* Section Card Wrapper */
.apple-card {
    background: #16181F;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 24px;
}
</style>
""")

# Load Cleaned Data from Parquet (Read-Only)
@st.cache_data
def load_data():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(project_dir, "data", "processed", "combined_resignations.parquet")
    
    # Run ETL if processed dataset missing
    if not os.path.exists(parquet_path):
        from data_prep import run_pipeline
        run_pipeline()
        
    df = pd.read_parquet(parquet_path)
    return df

df_all = load_data()

# Header
st.title("Employee Exit Survey Analysis")
st.markdown("Quantifying resignation drivers, career stage vulnerability, and institutional dissatisfaction across Queensland educational bodies.")

# Sidebar Filters
st.sidebar.header("Filter Options")

# Institute filter
institutes = ["All Institutes"] + sorted(list(df_all['institute'].unique()))
selected_institute = st.sidebar.selectbox("Educational Institute", institutes)

# Career Stage filter
career_stages = ["All Career Stages", "New (<3 yrs)", "Experienced (3-6 yrs)", "Established (7-10 yrs)", "Veteran (11+ yrs)"]
selected_stage = st.sidebar.selectbox("Career Stage", career_stages)

# Age Bracket filter
age_brackets = ["All Age Brackets", "Under 30", "30-50", "50+"]
selected_age = st.sidebar.selectbox("Age Bracket", age_brackets)

# Filter Application
df_filtered = df_all.copy()

if selected_institute != "All Institutes":
    df_filtered = df_filtered[df_filtered['institute'] == selected_institute]

if selected_stage != "All Career Stages":
    stage_key_map = {
        "New (<3 yrs)": "New",
        "Experienced (3-6 yrs)": "Experienced",
        "Established (7-10 yrs)": "Established",
        "Veteran (11+ yrs)": "Veteran"
    }
    df_filtered = df_filtered[df_filtered['service_cat'] == stage_key_map[selected_stage]]

if selected_age != "All Age Brackets":
    df_filtered = df_filtered[df_filtered['age_bracket'] == selected_age]

# Global KPIs
kpis = get_kpi_summary(df_filtered)

# Layout Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Overview",
    "Tenure & Service Matrix",
    "Friction Factor Breakdown",
    "Institute Comparison",
    "Survey Records Explorer"
])

# Tab 1: Executive Overview
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Resignations", f"{kpis['total_resignations']:,}")
    with col2:
        st.metric("Overall Dissatisfaction", f"{kpis['overall_dissat_pct']}%")
    with col3:
        st.metric("DETE Resignations", f"{len(df_filtered[df_filtered['institute'] == 'DETE']):,}")
    with col4:
        st.metric("TAFE Resignations", f"{len(df_filtered[df_filtered['institute'] == 'TAFE']):,}")

    st.markdown("---")
    
    st.markdown("### Resignation Dissatisfaction Rate by Career Stage")
    df_service = get_dissatisfaction_by_service(df_filtered)
    
    fig_service = px.bar(
        df_service,
        x='service_cat',
        y='dissat_pct',
        text='dissat_pct',
        labels={'service_cat': 'Career Stage', 'dissat_pct': 'Dissatisfaction Rate (%)'},
        color='dissat_pct',
        color_continuous_scale=['#1E3A8A', '#0071E3', '#60A5FA']
    )
    fig_service.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside',
        marker_line_color='rgba(255, 255, 255, 0.1)',
        marker_line_width=1
    )
    fig_service.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F5F5F7',
        yaxis_range=[0, max(df_service['dissat_pct'].max() * 1.2, 50)],
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_service, width="stretch")

# Tab 2: Tenure & Service Matrix
with tab2:
    st.markdown("### Tenure Breakdown & Service Vulnerability")
    col_t1, col_t2 = st.columns([3, 2])
    
    with col_t1:
        st.markdown("#### Dissatisfaction Trend Across Institutes")
        df_inst_service = get_dissatisfaction_by_institute(df_filtered)
        
        # Melt for plotting
        df_melt = pd.melt(
            df_inst_service,
            id_vars=['service_cat'],
            var_name='Institute',
            value_name='Rate'
        ).dropna()
        
        fig_inst = px.bar(
            df_melt,
            x='service_cat',
            y='Rate',
            color='Institute',
            barmode='group',
            labels={'service_cat': 'Career Stage', 'Rate': 'Dissatisfaction Rate (%)'},
            color_discrete_map={'DETE': '#0071E3', 'TAFE': '#5E5CE6'}
        )
        fig_inst.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F5F5F7'
        )
        st.plotly_chart(fig_inst, width="stretch")
        
    with col_t2:
        st.markdown("#### Resignations Count by Stage")
        fig_pie = px.pie(
            df_service,
            names='service_cat',
            values='total',
            color='service_cat',
            color_discrete_sequence=['#2563EB', '#3B82F6', '#60A5FA', '#93C5FD'],
            hole=0.45
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F5F5F7'
        )
        st.plotly_chart(fig_pie, width="stretch")

# Tab 3: Friction Factor Breakdown
with tab3:
    st.markdown("### Ranked Departure Friction Factors")
    df_factors = get_resignation_factor_breakdown(df_filtered)
    
    fig_factors = px.bar(
        df_factors.sort_values(by='count', ascending=True),
        x='count',
        y='factor',
        orientation='h',
        labels={'count': 'Number of Departing Employees', 'factor': 'Reported Friction Factor'},
        color='prevalence_pct',
        color_continuous_scale=['#1E3A8A', '#0071E3']
    )
    fig_factors.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F5F5F7',
        coloraxis_showscale=False,
        height=520
    )
    st.plotly_chart(fig_factors, width="stretch")
    
    st.markdown("#### Factor Prevalence Table")
    st.dataframe(df_factors, width="stretch")

# Tab 4: Institute Comparison
with tab4:
    st.markdown("### Institutional Deep Dive: DETE vs. TAFE")
    
    df_dete_only = df_filtered[df_filtered['institute'] == 'DETE']
    df_tafe_only = df_filtered[df_filtered['institute'] == 'TAFE']
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dete_count = len(df_dete_only)
        dete_pct = round((df_dete_only['dissatisfied'].sum() / max(dete_count, 1)) * 100, 1)
        st.markdown(f"#### Department of Education (DETE)")
        st.write(f"- **Total Survey Resignations:** {dete_count:,}")
        st.write(f"- **Dissatisfaction Proportion:** {dete_pct}%")
        st.write(f"- **Average Service Length:** {df_dete_only['institute_service'].mean():.1f} years")
        
    with col_d2:
        tafe_count = len(df_tafe_only)
        tafe_pct = round((df_tafe_only['dissatisfied'].sum() / max(tafe_count, 1)) * 100, 1)
        st.markdown(f"#### Vocational Institutes (TAFE)")
        st.write(f"- **Total Survey Resignations:** {tafe_count:,}")
        st.write(f"- **Dissatisfaction Proportion:** {tafe_pct}%")
        st.write(f"- **Average Service Length:** {df_tafe_only['institute_service'].mean():.1f} years")
        
    st.markdown("---")
    st.markdown("#### Role Breakdown Across Institutes")
    gb_age, gb_pos = get_demographics_breakdown(df_filtered)
    
    fig_pos = px.bar(
        gb_pos,
        x='rate_pct',
        y='position',
        orientation='h',
        labels={'rate_pct': 'Dissatisfaction Rate (%)', 'position': 'Job Role'},
        color_discrete_sequence=['#0071E3']
    )
    fig_pos.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F5F5F7'
    )
    st.plotly_chart(fig_pos, width="stretch")

# Tab 5: Survey Record Explorer
with tab5:
    st.markdown("### Survey Exit Record Explorer")
    
    search_query = st.text_input("Search position, employment status, or region")
    
    df_display = df_filtered.copy()
    if search_query:
        mask = (
            df_display['position'].astype(str).str.contains(search_query, case=False, na=False) |
            df_display['employment_status'].astype(str).str.contains(search_query, case=False, na=False) |
            df_display['region'].astype(str).str.contains(search_query, case=False, na=False)
        )
        df_display = df_display[mask]
        
    cols_to_show = [
        'id', 'institute', 'position', 'service_cat', 'institute_service',
        'age_bracket', 'employment_status', 'dissatisfied', 'region'
    ]
    st.dataframe(df_display[cols_to_show].reset_index(drop=True), width="stretch")
    
    # CSV download
    csv_bytes = df_display[cols_to_show].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Survey Data (CSV)",
        data=csv_bytes,
        file_name="filtered_employee_exit_surveys.csv",
        mime="text/csv"
    )
