import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Add project root and src folder to python path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_DIR, "src")
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from analytics import (
    get_kpi_summary,
    get_dissatisfaction_by_service,
    get_dissatisfaction_by_institute,
    get_resignation_factor_breakdown,
    get_demographics_breakdown,
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
    parquet_path = os.path.join(PROJECT_DIR, "data", "processed", "combined_resignations.parquet")
    
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
    
    fig_service, ax_service = plt.subplots(figsize=(8.5, 4.2))
    fig_service.patch.set_facecolor("#0B0C10")
    ax_service.set_facecolor("#16181F")
    
    stages = df_service['service_cat'].tolist()
    rates = df_service['dissat_pct'].tolist()
    totals = df_service['total'].tolist()
    
    colors = ["#2563EB", "#0071E3", "#38BDF8", "#F59E0B"]
    bars = ax_service.bar(stages, rates, color=colors[:len(stages)], width=0.55, edgecolor=(1, 1, 1, 0.12), linewidth=1)
    
    for bar, rate, tot in zip(bars, rates, totals):
        yval = bar.get_height()
        ax_service.text(
            bar.get_x() + bar.get_width() / 2,
            yval + 1.8,
            f"{rate:.1f}%\n({tot:,} exits)",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#F5F5F7",
            fontweight="600"
        )
        
    ax_service.set_ylabel("Dissatisfaction Rate (%)", fontsize=10, color="#86868B", labelpad=8)
    ax_service.set_xlabel("Career Stage (Tenure Bracket)", fontsize=10, color="#86868B", labelpad=8)
    ax_service.tick_params(colors="#86868B", labelsize=9.5)
    ax_service.set_ylim(0, max(max(rates, default=40) * 1.35, 60))
    ax_service.yaxis.set_major_formatter(ticker.PercentFormatter())
    
    for spine in ['top', 'right', 'left']:
        ax_service.spines[spine].set_visible(False)
    ax_service.spines['bottom'].set_color((1, 1, 1, 0.15))
    ax_service.grid(axis='y', color=(1, 1, 1, 0.06), linestyle='--', linewidth=0.8)
    
    fig_service.tight_layout()
    st.pyplot(fig_service, width="stretch")
    plt.close(fig_service)

# Tab 2: Tenure & Service Matrix
with tab2:
    st.markdown("### Tenure Breakdown & Service Vulnerability")
    col_t1, col_t2 = st.columns([3, 2])
    
    with col_t1:
        st.markdown("#### Dissatisfaction Rate: DETE vs. TAFE")
        df_inst_service = get_dissatisfaction_by_institute(df_filtered)
        
        fig_inst, ax_inst = plt.subplots(figsize=(7, 4.5))
        fig_inst.patch.set_facecolor("#0B0C10")
        ax_inst.set_facecolor("#16181F")
        
        x_indices = np.arange(len(df_inst_service))
        bar_w = 0.35
        
        dete_rates = df_inst_service['DETE'].fillna(0).tolist() if 'DETE' in df_inst_service.columns else [0] * len(df_inst_service)
        tafe_rates = df_inst_service['TAFE'].fillna(0).tolist() if 'TAFE' in df_inst_service.columns else [0] * len(df_inst_service)
        
        bars_d = ax_inst.bar(x_indices - bar_w/2, dete_rates, bar_w, label="DETE", color="#0071E3", edgecolor=(1, 1, 1, 0.1))
        bars_t = ax_inst.bar(x_indices + bar_w/2, tafe_rates, bar_w, label="TAFE", color="#5E5CE6", edgecolor=(1, 1, 1, 0.1))
        
        for bar in bars_d:
            h = bar.get_height()
            if h > 0:
                ax_inst.text(bar.get_x() + bar.get_width()/2, h + 1.2, f"{h:.1f}%", ha='center', va='bottom', fontsize=8.5, color='#F5F5F7', fontweight='600')
        for bar in bars_t:
            h = bar.get_height()
            if h > 0:
                ax_inst.text(bar.get_x() + bar.get_width()/2, h + 1.2, f"{h:.1f}%", ha='center', va='bottom', fontsize=8.5, color='#F5F5F7', fontweight='600')
                
        ax_inst.set_xticks(x_indices)
        ax_inst.set_xticklabels(df_inst_service['service_cat'], fontsize=9, color="#86868B")
        ax_inst.set_ylabel("Dissatisfaction Rate (%)", fontsize=10, color="#86868B")
        ax_inst.tick_params(colors="#86868B", labelsize=9)
        max_rate = max(max(dete_rates + tafe_rates, default=30), 30)
        ax_inst.set_ylim(0, max_rate * 1.3)
        ax_inst.yaxis.set_major_formatter(ticker.PercentFormatter())
        
        for spine in ['top', 'right', 'left']:
            ax_inst.spines[spine].set_visible(False)
        ax_inst.spines['bottom'].set_color((1, 1, 1, 0.15))
        ax_inst.grid(axis='y', color=(1, 1, 1, 0.06), linestyle='--', linewidth=0.8)
        
        legend = ax_inst.legend(facecolor='#16181F', edgecolor=(1, 1, 1, 0.12), labelcolor='#F5F5F7', fontsize=9)
        
        fig_inst.tight_layout()
        st.pyplot(fig_inst, width="stretch")
        plt.close(fig_inst)
        
    with col_t2:
        st.markdown("#### Resignations by Career Stage")
        fig_pie, ax_pie = plt.subplots(figsize=(5.5, 4.5))
        fig_pie.patch.set_facecolor("#0B0C10")
        ax_pie.set_facecolor("#16181F")
        
        pie_labels = df_service['service_cat'].tolist()
        pie_values = df_service['total'].tolist()
        pie_colors = ['#0071E3', '#3B82F6', '#60A5FA', '#93C5FD']
        
        if sum(pie_values) > 0:
            wedges, texts, autotexts = ax_pie.pie(
                pie_values,
                labels=pie_labels,
                autopct='%1.1f%%',
                pctdistance=0.75,
                colors=pie_colors[:len(pie_labels)],
                startangle=140,
                wedgeprops=dict(width=0.42, edgecolor='#0B0C10', linewidth=2),
                textprops=dict(color="#86868B", fontsize=8.5)
            )
            for autotext in autotexts:
                autotext.set_color("#FFFFFF")
                autotext.set_fontsize(9)
                autotext.set_fontweight("600")
                
            # Center annotation
            total_sum = sum(pie_values)
            ax_pie.text(0, 0, f"{total_sum:,}\nExits", ha='center', va='center', fontsize=12, fontweight='bold', color='#F5F5F7')
        else:
            ax_pie.text(0, 0, "No data available", ha='center', va='center', color='#86868B')
            
        fig_pie.tight_layout()
        st.pyplot(fig_pie, width="stretch")
        plt.close(fig_pie)

# Tab 3: Friction Factor Breakdown
with tab3:
    st.markdown("### Ranked Departure Friction Factors")
    df_factors = get_resignation_factor_breakdown(df_filtered)
    
    fig_factors, ax_factors = plt.subplots(figsize=(9, 5.5))
    fig_factors.patch.set_facecolor("#0B0C10")
    ax_factors.set_facecolor("#16181F")
    
    df_factors_sorted = df_factors.sort_values(by='count', ascending=True).reset_index(drop=True)
    factors_list = df_factors_sorted['factor'].tolist()
    counts_list = df_factors_sorted['count'].tolist()
    pcts_list = df_factors_sorted['prevalence_pct'].tolist()
    
    y_pos = np.arange(len(factors_list))
    bar_colors = ["#0071E3" if p >= 20.0 else "#2563EB" if p >= 10.0 else "#1E3A8A" for p in pcts_list]
    
    h_bars = ax_factors.barh(y_pos, counts_list, color=bar_colors, height=0.65, edgecolor=(1, 1, 1, 0.1))
    
    for bar, c, p in zip(h_bars, counts_list, pcts_list):
        width = bar.get_width()
        ax_factors.text(
            width + max(counts_list, default=1) * 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{c:,} ({p:.1f}%)",
            va="center",
            ha="left",
            fontsize=8.5,
            color="#F5F5F7",
            fontweight="500"
        )
        
    ax_factors.set_yticks(y_pos)
    ax_factors.set_yticklabels(factors_list, fontsize=9, color="#86868B")
    ax_factors.set_xlabel("Number of Departing Employees", fontsize=10, color="#86868B", labelpad=8)
    ax_factors.tick_params(colors="#86868B", labelsize=9)
    ax_factors.set_xlim(0, max(counts_list, default=10) * 1.25)
    
    for spine in ['top', 'right', 'bottom']:
        ax_factors.spines[spine].set_visible(False)
    ax_factors.spines['left'].set_color((1, 1, 1, 0.15))
    ax_factors.grid(axis='x', color=(1, 1, 1, 0.06), linestyle='--', linewidth=0.8)
    
    fig_factors.tight_layout()
    st.pyplot(fig_factors, width="stretch")
    plt.close(fig_factors)
    
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
        st.markdown("#### Department of Education (DETE)")
        st.write(f"- **Total Survey Resignations:** {dete_count:,}")
        st.write(f"- **Dissatisfaction Proportion:** {dete_pct}%")
        st.write(f"- **Average Service Length:** {df_dete_only['institute_service'].mean():.1f} years")
        
    with col_d2:
        tafe_count = len(df_tafe_only)
        tafe_pct = round((df_tafe_only['dissatisfied'].sum() / max(tafe_count, 1)) * 100, 1)
        st.markdown("#### Vocational Institutes (TAFE)")
        st.write(f"- **Total Survey Resignations:** {tafe_count:,}")
        st.write(f"- **Dissatisfaction Proportion:** {tafe_pct}%")
        st.write(f"- **Average Service Length:** {df_tafe_only['institute_service'].mean():.1f} years")
        
    st.markdown("---")
    st.markdown("#### Role Breakdown Across Institutes")
    gb_age, gb_pos = get_demographics_breakdown(df_filtered)
    
    if not gb_pos.empty:
        fig_pos, ax_pos = plt.subplots(figsize=(8.5, 4.5))
        fig_pos.patch.set_facecolor("#0B0C10")
        ax_pos.set_facecolor("#16181F")
        
        gb_pos_sorted = gb_pos.sort_values(by='rate_pct', ascending=True).reset_index(drop=True)
        pos_labels = gb_pos_sorted['position'].tolist()
        pos_rates = gb_pos_sorted['rate_pct'].tolist()
        pos_dissat = gb_pos_sorted['dissat_count'].tolist()
        pos_totals = gb_pos_sorted['total'].tolist()
        
        y_indices = np.arange(len(pos_labels))
        pos_bars = ax_pos.barh(y_indices, pos_rates, height=0.6, color="#0071E3", edgecolor=(1, 1, 1, 0.1))
        
        for bar, rate, d_cnt, t_cnt in zip(pos_bars, pos_rates, pos_dissat, pos_totals):
            w = bar.get_width()
            ax_pos.text(
                w + max(pos_rates, default=1) * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{rate:.1f}% ({d_cnt:,}/{t_cnt:,})",
                va="center",
                ha="left",
                fontsize=8.5,
                color="#F5F5F7",
                fontweight="500"
            )
            
        ax_pos.set_yticks(y_indices)
        ax_pos.set_yticklabels(pos_labels, fontsize=9, color="#86868B")
        ax_pos.set_xlabel("Dissatisfaction Rate (%)", fontsize=10, color="#86868B", labelpad=8)
        ax_pos.tick_params(colors="#86868B", labelsize=9)
        ax_pos.set_xlim(0, max(pos_rates, default=30) * 1.35)
        ax_pos.xaxis.set_major_formatter(ticker.PercentFormatter())
        
        for spine in ['top', 'right', 'bottom']:
            ax_pos.spines[spine].set_visible(False)
        ax_pos.spines['left'].set_color((1, 1, 1, 0.15))
        ax_pos.grid(axis='x', color=(1, 1, 1, 0.06), linestyle='--', linewidth=0.8)
        
        fig_pos.tight_layout()
        st.pyplot(fig_pos, width="stretch")
        plt.close(fig_pos)
    else:
        st.info("No position data available for current selection.")

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
