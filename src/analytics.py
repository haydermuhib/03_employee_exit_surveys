import pandas as pd
import numpy as np

def get_kpi_summary(df):
    total = len(df)
    if total == 0:
        return {
            'total_resignations': 0,
            'overall_dissat_pct': 0.0,
            'dete_dissat_pct': 0.0,
            'tafe_dissat_pct': 0.0,
            'top_risk_stage': 'None'
        }
        
    overall_dissat = (df['dissatisfied'].sum() / total) * 100
    
    dete_mask = df['institute'] == 'DETE'
    tafe_mask = df['institute'] == 'TAFE'
    
    dete_dissat = (df[dete_mask]['dissatisfied'].sum() / max(dete_mask.sum(), 1)) * 100
    tafe_dissat = (df[tafe_mask]['dissatisfied'].sum() / max(tafe_mask.sum(), 1)) * 100
    
    stage_gb = df.groupby('service_cat')['dissatisfied'].mean()
    top_stage = stage_gb.idxmax() if not stage_gb.empty else 'None'
    
    return {
        'total_resignations': total,
        'overall_dissat_pct': round(overall_dissat, 1),
        'dete_dissat_pct': round(dete_dissat, 1),
        'tafe_dissat_pct': round(tafe_dissat, 1),
        'top_risk_stage': top_stage
    }

def get_dissatisfaction_by_service(df):
    order = ['New', 'Experienced', 'Established', 'Veteran']
    df_known = df[df['service_cat'] != 'Unspecified']
    
    gb = df_known.groupby('service_cat').agg(
        total=('dissatisfied', 'count'),
        dissatisfied=('dissatisfied', 'sum'),
        dissat_pct=('dissatisfied', lambda x: round((x.sum() / len(x)) * 100, 1))
    ).reindex(order).reset_index()
    
    return gb

def get_dissatisfaction_by_institute(df):
    order = ['New', 'Experienced', 'Established', 'Veteran']
    df_known = df[df['service_cat'] != 'Unspecified']
    
    gb = df_known.groupby(['service_cat', 'institute'])['dissatisfied'].agg(
        total='count',
        dissat_count='sum'
    ).reset_index()
    
    gb['rate_pct'] = round((gb['dissat_count'] / gb['total']) * 100, 1)
    
    pivot = gb.pivot(index='service_cat', columns='institute', values='rate_pct').reindex(order).reset_index()
    return pivot

def get_resignation_factor_breakdown(df):
    factor_definitions = {
        'Job Dissatisfaction': 'job_dissatisfaction',
        'Workload & Fatigue': 'workload',
        'Work-Life Balance': 'work_life_balance',
        'Department Dissatisfaction': 'dissatisfaction_with_the_department',
        'Interpersonal Conflicts': 'interpersonal_conflicts',
        'Physical Work Environment': 'physical_work_environment',
        'Lack of Recognition': 'lack_of_recognition',
        'Employment Conditions': 'employment_conditions',
        'Career Move - Private Sector': 'career_move_private',
        'Career Move - Public Sector': 'career_move_public',
        'Ill Health': 'ill_health',
        'Relocation': 'relocation',
        'Maternity / Family': 'maternity_family'
    }
    
    results = []
    total_res = len(df)
    
    for label, col in factor_definitions.items():
        if col in df.columns:
            count = df[col].sum()
            pct = round((count / total_res) * 100, 1) if total_res > 0 else 0.0
            results.append({
                'factor': label,
                'count': int(count),
                'prevalence_pct': pct
            })
            
    df_factors = pd.DataFrame(results).sort_values(by='count', ascending=False).reset_index(drop=True)
    return df_factors

def get_demographics_breakdown(df):
    age_order = ['Under 30', '30-50', '50+']
    df_age = df[df['age_bracket'].isin(age_order)]
    
    gb_age = df_age.groupby('age_bracket').agg(
        total=('dissatisfied', 'count'),
        dissat_count=('dissatisfied', 'sum')
    ).reindex(age_order).reset_index()
    gb_age['rate_pct'] = round((gb_age['dissat_count'] / gb_age['total']) * 100, 1)
    
    # Top positions
    top_pos = df['position'].value_counts().head(6).index
    df_pos = df[df['position'].isin(top_pos)]
    gb_pos = df_pos.groupby('position').agg(
        total=('dissatisfied', 'count'),
        dissat_count=('dissatisfied', 'sum')
    ).reset_index()
    gb_pos['rate_pct'] = round((gb_pos['dissat_count'] / gb_pos['total']) * 100, 1)
    gb_pos = gb_pos.sort_values(by='rate_pct', ascending=False).reset_index(drop=True)
    
    return gb_age, gb_pos
