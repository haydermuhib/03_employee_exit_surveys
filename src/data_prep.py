import os
import re
import numpy as np
import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")

def clean_dete():
    dete_path = os.path.join(RAW_DIR, "dete_survey.csv")
    df = pd.read_csv(dete_path, na_values=['Not Stated'])
    
    # Clean column names
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('/', '_')
    
    # Filter resignations
    df_res = df[df['separationtype'].astype(str).str.contains('Resignation', case=False, na=False)].copy()
    
    # Clean cease_date and extract year
    def extract_year(val):
        if pd.isna(val):
            return np.nan
        val = str(val).strip()
        match = re.search(r'(20[0-9]{2})', val)
        if match:
            return float(match.group(1))
        return np.nan

    df_res['cease_year'] = df_res['cease_date'].apply(extract_year)
    df_res['start_year'] = pd.to_numeric(df_res['dete_start_date'], errors='coerce')
    df_res['institute_service'] = df_res['cease_year'] - df_res['start_year']
    
    # Filter out invalid negative service or outliers > 60 years
    df_res.loc[(df_res['institute_service'] < 0) | (df_res['institute_service'] > 60), 'institute_service'] = np.nan
    
    # Dissatisfaction and contributing factor columns in DETE
    dete_factors = {
        'career_move_to_public_sector': 'career_move_public',
        'career_move_to_private_sector': 'career_move_private',
        'study_travel': 'study_travel',
        'maternity_family': 'maternity_family',
        'relocation': 'relocation'
    }
    df_res = df_res.rename(columns=dete_factors)
    
    dissat_cols = [
        'job_dissatisfaction',
        'dissatisfaction_with_the_department',
        'physical_work_environment',
        'lack_of_recognition',
        'lack_of_job_security',
        'work_location',
        'employment_conditions',
        'work_life_balance',
        'workload',
        'interpersonal_conflicts',
        'ill_health',
        'career_move_public',
        'career_move_private',
        'study_travel',
        'maternity_family',
        'relocation'
    ]
    
    for col in dissat_cols:
        if col in df_res.columns:
            df_res[col] = df_res[col].fillna(False).astype(bool)
            
    core_dissat = [
        'job_dissatisfaction', 'dissatisfaction_with_the_department',
        'physical_work_environment', 'lack_of_recognition',
        'lack_of_job_security', 'work_location', 'employment_conditions',
        'work_life_balance', 'workload', 'interpersonal_conflicts'
    ]
    df_res['dissatisfied'] = df_res[core_dissat].any(axis=1)
    df_res['institute'] = 'DETE'
    
    return df_res

def clean_tafe():
    tafe_path = os.path.join(RAW_DIR, "tafe_survey.csv")
    df = pd.read_csv(tafe_path)
    
    # Column mapping dictionary
    col_map = {
        'Record ID': 'id',
        'CESSATION REASON': 'separationtype',
        'Reason for ceasing employment': 'cessation_reason',
        'LengthofServiceOverall. Overall Length of Service at Institute (in years)': 'institute_service_raw',
        'LengthofServiceCurrent. Length of Service at current workplace (in years)': 'workplace_service_raw',
        'Contributing Factors. Dissatisfaction': 'dissatisfaction',
        'Contributing Factors. Job Dissatisfaction': 'job_dissatisfaction',
        'Contributing Factors. Interpersonal Conflict': 'interpersonal_conflicts',
        'Contributing Factors. Career Move - Public Sector ': 'career_move_public',
        'Contributing Factors. Career Move - Private Sector ': 'career_move_private',
        'Contributing Factors. Ill Health': 'ill_health',
        'Contributing Factors. Travel': 'travel',
        'Contributing Factors. Other': 'other',
        'Contributing Factors. Maternity/Family': 'maternity_family',
        'Gender. What is your Gender?': 'gender',
        'CurrentAge. Current Age': 'age',
        'Employment Type. Employment Type': 'employment_status',
        'Classification. Classification': 'position',
        'Institute': 'region'
    }
    
    df = df.rename(columns=col_map)
    
    # Filter resignations
    df_res = df[df['separationtype'].astype(str).str.contains('Resignation', case=False, na=False)].copy()
    
    # Standardize TAFE service string into numeric years
    def parse_tafe_service(val):
        if pd.isna(val) or val == '-':
            return np.nan
        val = str(val).strip()
        if 'Less than 1' in val:
            return 0.5
        elif '1-2' in val:
            return 1.5
        elif '3-4' in val:
            return 3.5
        elif '5-6' in val:
            return 5.5
        elif '7-10' in val:
            return 8.5
        elif '11-20' in val:
            return 15.0
        elif 'More than 20' in val:
            return 25.0
        return np.nan

    df_res['institute_service'] = df_res['institute_service_raw'].apply(parse_tafe_service)
    
    # Dissatisfaction and contributing factors mapping to boolean
    def is_factor_present(val):
        if pd.isna(val) or str(val).strip() == '-' or str(val).strip() == '':
            return False
        return True
        
    factor_tafe_cols = [
        'dissatisfaction', 'job_dissatisfaction', 'interpersonal_conflicts',
        'career_move_public', 'career_move_private', 'ill_health',
        'travel', 'other', 'maternity_family'
    ]
    for c in factor_tafe_cols:
        if c in df_res.columns:
            df_res[c] = df_res[c].apply(is_factor_present).astype(bool)
            
    dissat_tafe_cols = ['dissatisfaction', 'job_dissatisfaction', 'interpersonal_conflicts']
    df_res['dissatisfied'] = df_res[dissat_tafe_cols].any(axis=1)
    df_res['institute'] = 'TAFE'
    
    return df_res

def assign_service_cat(years):
    if pd.isna(years):
        return 'Unspecified'
    elif years < 3:
        return 'New'
    elif years < 7:
        return 'Experienced'
    elif years <= 10:
        return 'Established'
    else:
        return 'Veteran'

def assign_age_bracket(age_str):
    if pd.isna(age_str) or age_str == 'Not Stated':
        return 'Unspecified'
    age_str = str(age_str).strip()
    if any(k in age_str for k in ['20 or younger', '21-25', '21  25', '26-30', '26  30']):
        return 'Under 30'
    elif any(k in age_str for k in ['31-35', '31  35', '36-40', '36  40', '41-45', '41  45', '46-50', '46  50']):
        return '30-50'
    elif any(k in age_str for k in ['51-55', '51  55', '56-60', '56 or older', '61 or older']):
        return '50+'
    return '30-50'

def run_pipeline():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("Executing DETE survey cleaning pipeline...")
    df_dete = clean_dete()
    print(f"DETE resignations cleaned: {len(df_dete):,} records.")
    
    print("Executing TAFE survey cleaning pipeline...")
    df_tafe = clean_tafe()
    print(f"TAFE resignations cleaned: {len(df_tafe):,} records.")
    
    # Common harmonized schema columns
    common_cols = [
        'id', 'institute', 'separationtype', 'institute_service',
        'dissatisfied', 'gender', 'age', 'position', 'employment_status', 'region'
    ]
    
    # Align DETE columns
    if 'id' not in df_dete.columns and 'id' in df_dete.columns:
        pass
    elif 'id' not in df_dete.columns:
        df_dete = df_dete.rename(columns={'id': 'id'})
        
    # Combine resignations
    combined = pd.concat([df_dete, df_tafe], axis=0, ignore_index=True)
    
    # Categorize career stages
    combined['service_cat'] = combined['institute_service'].apply(assign_service_cat)
    df_dete['service_cat'] = df_dete['institute_service'].apply(assign_service_cat)
    df_tafe['service_cat'] = df_tafe['institute_service'].apply(assign_service_cat)
    
    # Standardize age brackets
    combined['age_bracket'] = combined['age'].apply(assign_age_bracket)
    df_dete['age_bracket'] = df_dete['age'].apply(assign_age_bracket)
    df_tafe['age_bracket'] = df_tafe['age'].apply(assign_age_bracket)
    
    # Export Parquet tables
    combined_path = os.path.join(PROCESSED_DIR, "combined_resignations.parquet")
    dete_path = os.path.join(PROCESSED_DIR, "dete_clean.parquet")
    tafe_path = os.path.join(PROCESSED_DIR, "tafe_clean.parquet")
    
    combined.to_parquet(combined_path, index=False, engine='pyarrow')
    df_dete.to_parquet(dete_path, index=False, engine='pyarrow')
    df_tafe.to_parquet(tafe_path, index=False, engine='pyarrow')
    
    print(f"Exported combined resignations: {len(combined):,} rows -> {combined_path}")
    print(f"Exported DETE clean table: {len(df_dete):,} rows -> {dete_path}")
    print(f"Exported TAFE clean table: {len(df_tafe):,} rows -> {tafe_path}")
    print("ETL complete.")

if __name__ == "__main__":
    run_pipeline()
