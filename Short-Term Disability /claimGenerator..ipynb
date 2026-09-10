import csv, random
from datetime import date, timedelta

random.seed(42)
N_CLAIMS = 1000

def rand_date(y0=2023, y1=2025):
    a, b = date(y0,1,1), date(y1,12,31)
    return a + timedelta(days=random.randint(0,(b-a).days))

def lognormal_wks(median, spread):
    return min(52.0, max(0.25, random.lognormvariate(__import__("math").log(median), spread*0.75)))

DX = [  # (category, icd10, weight, median_weeks, spread)
    ("Musculoskeletal","M54",24,4.0,1.1),("Pregnancy/Obstetric","O80",18,6.0,0.35),
    ("Mental/Behavioral","F41",14,8.0,1.2),("Post-surgical recovery","Z48",11,5.0,0.9),
    ("Digestive","K52",7,2.5,0.8),("Respiratory","J45",6,2.0,0.7),
    ("Fracture/Trauma","S72",5,6.0,1.0),("Cardiovascular","I20",4,5.0,1.0),
    ("Oncology treatment","C50",4,12.0,1.1),("Other","R69",3,3.0,0.9)]
JOBS = ["Sedentary","Light","Medium","Heavy"]
IND  = ["Healthcare","Manufacturing","Technology","Retail","Education",
        "Construction","Finance","Logistics","Government","Hospitality"]

# Employers
employers = {}
for i in range(1,121):
    ind = random.choice(IND)
    employers[f"E{i:04d}"] = {"industry": ind,
        "size": random.choice(["Small","Mid","Large","Enterprise"]),
        "max_weeks": random.choice([13,26,26,52]),
        "repl_pct": random.choice([50,60,60,67])}

# Employees
employees = []
for i in range(1,2401):
    eid = f"EMP{i:05d}"
    er  = random.choice(list(employers.keys()))
    employees.append({"employee_id":eid, "age_band":random.choice(
        ["20-29","30-39","40-49","50-59","60+"]), "gender":random.choice(["F","M"]),
        "tenure_band":random.choice(["<1yr","1-3yrs","3-5yrs","5-10yrs","10+yrs"]),
        "job_class":random.choices(JOBS,[30,30,26,14])[0], "state":random.choice(
        ["CA","NY","TX","FL","IL","PA","OH","WA","MA","CO"]),
        "weekly_pay":round(max(400,random.gauss(1100,350)),2),
        "employer_id":er})

# Claims
with open("std_claims.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["claim_id","employee_id","claim_start","claim_end","elimination_period_days",
                "icd_category","icd10_prefix","elimination_period_wks",
                "benefit_weeks","weekly_benefit","benefit_paid","claim_status",
                "denial_reason","pregnancy_flag","recurrence_flag"])
    for c in range(1,1001):
        emp = random.choice(employees); cat,icd,wgt,mw,sp = random.choices(
            DX,[x[2] for x in DX])[0] if False else random.choice(DX)
        start = rand_date()
        if random.random() < 0.30:               # Q1 seasonality spike
            start = date(start.year, random.randint(1,3), random.randint(1,28))
        elim = random.choice([0,7,7,14])
        st   = random.choices(
            ["Closed","Open","Pending","Denied","Recurrence"],[50,14,9,14,6])[0]
        preg = int(cat=="Pregnancy/Obstetric")
        recur= int(st=="Recurrence")
        reason = ""
        if st=="Denied":
            reason = random.choice(["Elimination period not met",
                "Insufficient medical documentation","Policy exclusion",
                "Concurrent workers comp","Late filing"])
            weeks = 0.0
        elif st=="Pending":
            weeks = 0.0
        else:
            plan = employers[emp["employer_id"]]
            weeks = round(min(lognormal_wks(mw,sp), plan["max_weeks"]),1)
            weekly = round(plan["repl_pct"]/100 * min(emp[ "weekly_pay"],2500),2)
            paid = round(weekly*weeks,2)
        end = start + timedelta(days=int((max(weeks,0.25))*7 + elim))
        w.writerow([f"CLM{c:05d}",emp[0],start,end,elim,cat,icd,elim/7,
            weeks,weekly,paid,st,reason,preg,recur])

print("std_claims.csv written: 1,000 claims")
