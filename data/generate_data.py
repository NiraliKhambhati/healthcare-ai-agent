import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

def random_date(start_year=2023):
    start = datetime(start_year, 1, 1)
    end = datetime(start_year, 12, 31)
    return start + timedelta(days=random.randint(0, 364))

records = []
for i in range(100000):
    age = random.randint(18, 85)
    gender = random.choice(["M", "F"])
    province = random.choice(["ON", "BC", "AB", "QC"])
    
    # Conditions
    has_hypertension = random.random() < 0.4
    has_diabetes = random.random() < 0.3
    has_asthma = random.random() < 0.2
    has_mental_health = random.random() < 0.15
    in_hospice = random.random() < 0.05

    # HEDIS CBP
    bp_systolic = random.randint(110, 180) if has_hypertension else None
    bp_controlled = bp_systolic < 140 if bp_systolic else None

    # HEDIS CDC
    hba1c = round(random.uniform(5.5, 11.0), 1) if has_diabetes else None
    hba1c_controlled = hba1c < 8.0 if hba1c else None
    hba1c_poor = hba1c > 9.0 if hba1c else None

    # HEDIS AMR
    asthma_controller_ratio = round(random.uniform(0.2, 1.0), 2) if has_asthma else None
    amr_compliant = asthma_controller_ratio >= 0.5 if asthma_controller_ratio else None

    # HEDIS FUH
    had_mental_health_admission = has_mental_health and random.random() < 0.4
    followup_7day = random.random() < 0.55 if had_mental_health_admission else None
    followup_30day = random.random() < 0.70 if had_mental_health_admission else None

    # HEDIS BCS
    eligible_mammogram = gender == "F" and 50 <= age <= 74
    had_mammogram = random.random() < 0.65 if eligible_mammogram else None

    # HEDIS COL
    eligible_colonoscopy = 45 <= age <= 75
    had_colonoscopy = random.random() < 0.60 if eligible_colonoscopy else None

    # CIHI
    was_admitted = random.random() < 0.3
    readmitted_30day = random.random() < 0.085 if was_admitted else None
    alc_days = random.randint(0, 30) if was_admitted else 0
    alc_flag = alc_days > 5 if was_admitted else False

    records.append({
        "patient_id": f"PT{i+1:04d}",
        "age": age,
        "gender": gender,
        "province": province,
        "in_hospice": in_hospice,
        "has_hypertension": has_hypertension,
        "bp_systolic": bp_systolic,
        "bp_controlled": bp_controlled,
        "has_diabetes": has_diabetes,
        "hba1c": hba1c,
        "hba1c_controlled": hba1c_controlled,
        "hba1c_poor_control": hba1c_poor,
        "has_asthma": has_asthma,
        "asthma_controller_ratio": asthma_controller_ratio,
        "amr_compliant": amr_compliant,
        "had_mental_health_admission": had_mental_health_admission,
        "followup_7day": followup_7day,
        "followup_30day": followup_30day,
        "eligible_mammogram": eligible_mammogram,
        "had_mammogram": had_mammogram,
        "eligible_colonoscopy": eligible_colonoscopy,
        "had_colonoscopy": had_colonoscopy,
        "was_admitted": was_admitted,
        "readmitted_30day": readmitted_30day,
        "alc_days": alc_days,
        "alc_flag": alc_flag
    })

df = pd.DataFrame(records)
df.to_csv("data/patient_data.csv", index=False)
print(f"Generated {len(df)} patient records")
print(df.head())