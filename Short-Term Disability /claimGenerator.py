"""Synthetic Short-Term Disability claims generator -> std_claims.csv"""
import csv, random, math
from datetime import date, timedelta


random.seed(42)
N_CLAIMS = 1000 # Number of claims you want to generate

"""" Function to create dates from a custom range **default will be in between 2023 and 2025**"""
def rand_date(y0=2023, y1=2025):
    a, b = date(y0, 1, 1), date(y1, 12, 31)
    return a + timedelta(days=random.randint(0, (b - a).days))

""""  function simulatiung disability claim duration in weeks from a lognormal distribution — the standard statistical model for "how long people are out sick.""""
def lognormal_wks(median, spread):
    return min(52.0, max(0.25, random.lognormvariate(math.log(median), spread * 0.75)))

# (category, icd10_prefix, weight, median_weeks, spread)
DX = [
    ("Musculoskeletal", "M54", 24, 4.0, 1.1),
    ("Pregnancy/Obstetric", "O80", 18, 6.0, 0.35),
    ("Mental/Behavioral", "F41", 14, 8.0, 1.2),
    ("Post-surgical recovery", "Z48", 11, 5.0, 0.9),
    ("Digestive", "K52", 7, 2.5, 0.8),
    ("Respiratory", "J45", 6, 2.0, 0.7),
    ("Fracture/Trauma", "S72", 5, 6.0, 1.0),
    ("Cardiovascular", "I20", 4, 5.0, 1.0),
    ("Oncology treatment", "C50", 4, 12.0, 1.1),
    ("Other", "R69", 4, 3.0, 0.9),
]

JOBS = ["Sedentary", "Light", "Medium", "Heavy"]
IND = ["Healthcare", "Manufacturing", "Technology", "Retail", "Education",
       "Construction", "Finance", "Logistics", "Government", "Hospitality"]

# --- Employers (120) ---
employers = {}
for i in range(1, 121):
    employers[f"E{i:04d}"] = {
        "industry": random.choice(IND),
        "size": random.choice(["Small", "Mid", "Large", "Enterprise"]),
        "max_weeks": random.choice([13, 26, 26, 52]),
        "repl_pct": random.choice([50, 60, 60, 67]),
    }

# --- Employees (~2,400 covered lives) ---
employees = []
for i in range(1, 2401):
    employees.append({
        "employee_id": f"EMP{i:05d}",
        "age_band": random.choice(["20-29", "30-39", "40-49", "50-59", "60+"]),
        "gender": random.choice(["F", "M"]),
        "tenure_band": random.choice(["<1yr", "1-3yrs", "3-5yrs", "5-10yrs", "10+yrs"]),
        "job_class": random.choices(JOBS, weights=[30, 30, 26, 14])[0],
        "state": random.choice(["CA", "NY", "TX", "FL", "IL", "PA", "OH", "WA", "MA", "CO"]),
        "weekly_pay": round(max(400, random.gauss(1100, 350)), 2),
        "employer_id": random.choice(list(employers.keys())),
    })

# --- Claims (1,000) ---
with open("std_claims.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["claim_id", "employee_id", "employer_id", "claim_start", "claim_end",
                "icd_category", "icd10_prefix", "elimination_period_days",
                "benefit_weeks", "weekly_benefit", "benefit_paid",
                "claim_status", "denial_reason", "pregnancy_flag", "recurrence_flag"])

    for c in range(1, N_CLAIMS + 1):
        emp = random.choice(employees)                              # emp is a dict
        plan = employers[emp["employer_id"]]
        cat, icd, wgt, med_wks, spread = random.choices(
            DX, weights=[d[2] for d in DX])[0]

        start = rand_date()
        if random.random() < 0.30:                                  # Q1 seasonality spike
            start = date(start.year, random.randint(1, 3), random.randint(1, 28))

        elim = random.choice([0, 7, 7, 14])
        status = random.choices(
            ["Closed", "Open", "Pending", "Denied", "Recurrence"],
            weights=[50, 14, 9, 14, 6])[0]

        # initialize everything so every branch writes a valid row
        weeks = 0.0
        weekly = 0.0
        paid = 0.0
        reason = ""

        if status == "Denied":
            reason = random.choice([
                "Elimination period not met",
                "Insufficient medical documentation",
                "Policy exclusion",
                "Concurrent workers comp",
                "Late filing"])
        elif status != "Pending":                                   # Closed / Open / Recurrence
            weeks = round(min(lognormal_wks(med_wks, spread), plan["max_weeks"]), 1)
            weekly = round(plan["repl_pct"] / 100 * min(emp["weekly_pay"], 2500), 2)
            paid = round(weekly * weeks, 2)

        end = start + timedelta(days=int(max(weeks, 0.25) * 7 + elim))
        recurrence = int(status == "Recurrence")

        w.writerow([
            f"CLM{c:05d}", emp["employee_id"], emp["employer_id"],
            start.isoformat(), end.isoformat(),
            cat, icd, elim, weeks, weekly, paid,
            status, reason, int(cat == "Pregnancy/Obstetric"), recurrence])
