import os
import random
import numpy as np
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(DATA_DIR, "raw")

def generate_dete_survey(n_records=3400, seed=42):
    np.random.seed(seed)
    random.seed(seed)
    
    separation_types = [
        "Resignation-Other reasons",
        "Resignation-Other employer",
        "Resignation-Move overseas/interstate",
        "Retirement",
        "Voluntary Early Retirement (VER)",
        "Ill Health",
        "Contract Expired",
        "Termination"
    ]
    sep_weights = [0.28, 0.22, 0.12, 0.16, 0.08, 0.06, 0.05, 0.03]
    
    positions = [
        "Teacher", "Teacher Aide", "Cleaner", "School Administrative Staff",
        "Head of Curriculum", "Guidance Officer", "Principal", "Schools Officer"
    ]
    pos_weights = [0.45, 0.15, 0.12, 0.14, 0.05, 0.03, 0.03, 0.03]
    
    regions = [
        "Metropolitan", "Central Queensland", "South East", "North Coast",
        "Darling Downs South West", "Far North Queensland", "Central Office"
    ]
    
    employment_statuses = [
        "Permanent Full-time", "Permanent Part-time", 
        "Temporary Full-time", "Temporary Part-time"
    ]
    status_weights = [0.65, 0.18, 0.12, 0.05]
    
    age_brackets = [
        "20 or younger", "21-25", "26-30", "31-35", "36-40",
        "41-45", "46-50", "51-55", "56-60", "61 or older"
    ]
    
    records = []
    for i in range(1, n_records + 1):
        sep_type = np.random.choice(separation_types, p=sep_weights)
        is_resignation = "Resignation" in sep_type
        
        cease_year = random.choice([2010, 2011, 2012, 2013, 2014])
        
        # Tenure distributions (New, Experienced, Established, Veteran)
        tenure_pool = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 18, 22, 28]
        tenure_weights = [0.12, 0.14, 0.12, 0.10, 0.08, 0.08, 0.06, 0.05, 0.05, 0.04, 0.05, 0.04, 0.03, 0.02, 0.02]
        tenure_years = int(np.random.choice(tenure_pool, p=tenure_weights))
        
        start_year = cease_year - tenure_years
        
        # Simulate 'Not Stated' missing data common in original DETE survey
        start_date_val = "Not Stated" if random.random() < 0.08 else str(start_year)
        role_start_val = "Not Stated" if random.random() < 0.12 else str(max(start_year, cease_year - random.randint(1, 8)))
        cease_date_val = "Not Stated" if random.random() < 0.03 else (f"{random.randint(1, 12):02d}/{cease_year}" if random.random() < 0.4 else str(cease_year))
        
        # Dissatisfaction factors correlated with resignation
        dissat_prob = 0.48 if (is_resignation and tenure_years >= 7) else (0.35 if is_resignation else 0.08)
        is_dissatisfied = random.random() < dissat_prob
        
        job_dissat = is_dissatisfied and random.random() < 0.65
        dept_dissat = is_dissatisfied and random.random() < 0.50
        workload_dissat = is_dissatisfied and random.random() < 0.55
        work_life_balance = is_dissatisfied and random.random() < 0.45
        env_dissat = is_dissatisfied and random.random() < 0.30
        lack_recognition = is_dissatisfied and random.random() < 0.40
        career_move_pub = random.random() < 0.15
        career_move_priv = random.random() < 0.20
        relocation = random.random() < 0.12
        ill_health = True if sep_type == "Ill Health" else (random.random() < 0.04)
        
        # Map age appropriately
        if tenure_years > 20:
            age = np.random.choice(["51-55", "56-60", "61 or older"])
        elif tenure_years > 10:
            age = np.random.choice(["36-40", "41-45", "46-50", "51-55"])
        elif tenure_years > 3:
            age = np.random.choice(["26-30", "31-35", "36-40", "41-45"])
        else:
            age = np.random.choice(["20 or younger", "21-25", "26-30", "31-35"])
            
        record = {
            "ID": i,
            "SeparationType": sep_type,
            "Cease Date": cease_date_val,
            "DETE Start Date": start_date_val,
            "Role Start Date": role_start_val,
            "Position": np.random.choice(positions, p=pos_weights),
            "Classification": "Not Stated" if random.random() < 0.45 else "Primary",
            "Region": random.choice(regions),
            "Business Unit": "Not Stated" if random.random() < 0.8 else "Education Services",
            "Employment Status": np.random.choice(employment_statuses, p=status_weights),
            "Career move to public sector": career_move_pub,
            "Career move to private sector": career_move_priv,
            "Interpersonal conflicts": is_dissatisfied and random.random() < 0.25,
            "Job dissatisfaction": job_dissat,
            "Dissatisfaction with the department": dept_dissat,
            "Physical work environment": env_dissat,
            "Lack of recognition": lack_recognition,
            "Lack of job security": is_dissatisfied and random.random() < 0.20,
            "Work location": random.random() < 0.10,
            "Employment conditions": is_dissatisfied and random.random() < 0.35,
            "Maternity/family": random.random() < 0.08,
            "Relocation": relocation,
            "Study/travel": random.random() < 0.06,
            "Ill Health": ill_health,
            "Traumatic incident": False,
            "Work life balance": work_life_balance,
            "Workload": workload_dissat,
            "Gender": np.random.choice(["Female", "Male"], p=[0.72, 0.28]),
            "Age": age,
            "Aboriginal": "Yes" if random.random() < 0.03 else np.nan,
            "Torres Strait": np.nan,
            "South Sea": np.nan,
            "Disability": "Yes" if random.random() < 0.04 else np.nan,
            "NESB": "Yes" if random.random() < 0.05 else np.nan
        }
        records.append(record)
        
    return pd.DataFrame(records)

def generate_tafe_survey(n_records=3200, seed=123):
    np.random.seed(seed)
    random.seed(seed)
    
    institutes = [
        "Southern Queensland Institute of TAFE",
        "Brisbane North Institute of TAFE",
        "Gold Coast Institute of TAFE",
        "Southbank Institute of TAFE",
        "Sunshine Coast Institute of TAFE",
        "Barrier Reef Institute of TAFE",
        "Tropical North Institute of TAFE",
        "SkillsTech Australia",
        "The Bremer Institute of TAFE"
    ]
    
    cessation_reasons = [
        "Resignation", "Retirement", "Contract Expired",
        "Retrenchment/ Redundancy", "Transfer"
    ]
    cess_weights = [0.55, 0.18, 0.15, 0.08, 0.04]
    
    tenure_categories = [
        "Less than 1 year", "1-2", "3-4", "5-6", "7-10", "11-20", "More than 20 years"
    ]
    tenure_weights = [0.18, 0.20, 0.16, 0.14, 0.12, 0.12, 0.08]
    
    classifications = [
        "Administration (AO)", "Teaching (including LOTE)", 
        "Operational (OO)", "Technical (TO)", "Executive (SES/CEO)"
    ]
    class_weights = [0.45, 0.38, 0.10, 0.05, 0.02]
    
    age_brackets = [
        "20 or younger", "21  25", "26  30", "31  35", "36  40",
        "41  45", "46  50", "51  55", "56 or older"
    ]
    
    records = []
    for i in range(1, n_records + 1):
        cess_reason = np.random.choice(cessation_reasons, p=cess_weights)
        is_resignation = (cess_reason == "Resignation")
        
        tenure_str = np.random.choice(tenure_categories, p=tenure_weights)
        is_veteran = tenure_str in ["7-10", "11-20", "More than 20 years"]
        
        # Dissatisfaction patterns in TAFE survey
        dissat_prob = 0.44 if (is_resignation and is_veteran) else (0.30 if is_resignation else 0.05)
        is_dissat = random.random() < dissat_prob
        
        contrib_dissat = "Contributing Factors. Dissatisfaction " if (is_dissat and random.random() < 0.60) else "-"
        job_dissat = "Job Dissatisfaction" if (is_dissat and random.random() < 0.70) else "-"
        career_pub = "Career Move - Public Sector" if (random.random() < 0.12) else "-"
        career_priv = "Career Move - Private Sector" if (random.random() < 0.22) else "-"
        interpersonal = "Interpersonal Conflict" if (is_dissat and random.random() < 0.25) else "-"
        ill_health = "Ill Health" if (random.random() < 0.06) else "-"
        travel = "Travel" if (random.random() < 0.07) else "-"
        other = "Other" if (random.random() < 0.15) else "-"
        
        record = {
            "Record ID": 6.34e17 + i,
            "Institute": random.choice(institutes),
            "WorkArea": "Non-Delivery (Support)" if random.random() < 0.5 else "Delivery (Education)",
            "CESSATION REASON": cess_reason,
            "Reason for ceasing employment": cess_reason,
            "LengthofServiceOverall. Overall Length of Service at Institute (in years)": tenure_str,
            "LengthofServiceCurrent. Length of Service at current workplace (in years)": tenure_str,
            "Contributing Factors. Career Move - Public Sector ": career_pub,
            "Contributing Factors. Career Move - Private Sector ": career_priv,
            "Contributing Factors. Career Move - Self-employment": "-",
            "Contributing Factors. Ill Health": ill_health,
            "Contributing Factors. Maternity/Family": "-" if random.random() < 0.9 else "Maternity/Family",
            "Contributing Factors. Dissatisfaction": contrib_dissat,
            "Contributing Factors. Job Dissatisfaction": job_dissat,
            "Contributing Factors. Interpersonal Conflict": interpersonal,
            "Contributing Factors. Study": "-" if random.random() < 0.92 else "Study",
            "Contributing Factors. Travel": travel,
            "Contributing Factors. Other": other,
            "Gender. What is your Gender?": np.random.choice(["Female", "Male"], p=[0.68, 0.32]),
            "CurrentAge. Current Age": random.choice(age_brackets),
            "Employment Type. Employment Type": np.random.choice(
                ["Permanent Full-time", "Permanent Part-time", "Temporary Full-time", "Temporary Part-time"],
                p=[0.55, 0.15, 0.20, 0.10]
            ),
            "Classification. Classification": np.random.choice(classifications, p=class_weights)
        }
        records.append(record)
        
    return pd.DataFrame(records)

def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    print("Generating raw DETE survey records...")
    df_dete = generate_dete_survey(n_records=3400)
    dete_path = os.path.join(RAW_DIR, "dete_survey.csv")
    df_dete.to_csv(dete_path, index=False)
    print(f"Saved {len(df_dete):,} DETE records to {dete_path}")
    
    print("Generating raw TAFE survey records...")
    df_tafe = generate_tafe_survey(n_records=3200)
    tafe_path = os.path.join(RAW_DIR, "tafe_survey.csv")
    df_tafe.to_csv(tafe_path, index=False)
    print(f"Saved {len(df_tafe):,} TAFE records to {tafe_path}")
    
    print(f"Total raw records generated: {len(df_dete) + len(df_tafe):,}")

if __name__ == "__main__":
    main()
