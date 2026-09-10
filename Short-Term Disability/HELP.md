# **claimGenerator.py help file** 

## <ins>**rand_date(y0=2023, y1=2025)**</ins>

Returns one random calendar date between Jan 1 of y0 and Dec 31 of y1, inclusive.

> a, b — the two inclusive boundaries (first/last day of the window)

> (b - a).days — subtracting two date objects returns a timedelta (a duration), not a date. .days reduces it to a plain integer: the total number of days in your window (e.g. 1,095 for 2023–2025).

> random.randint(0, span) — draws an integer offset from 0 to 1,095, all values equally likely. Note both endpoints are inclusive in randint, so 0 (= exactly Jan 1) and 1,095 (= exactly Dec 31, 2025) can both occur.

> a + timedelta(offset) — adds the offset back to the start date. Adding a timedelta to a date returns a new date (dates are immutable), so this is the random date itself.

It avoids the naive "pick random month, then random day" method, which biases shorter months downward, and gives perfectly uniform day probabilities. Combined with the fixed seed, the 1,000 dates are reproducible. A second snippet then overwrites ~30% of these with Q1 dates, creating the seasonality spike in your dashboard.


## **<ins>def lognormal_wks(median, spread)</ins>**

### **Why lognormal?**

Human durations like hospital stays, claim durations, or absence lengths are almost always right-skewed: most claims resolve around a typical value (say, 4 weeks), but a few outliers drag on much longer. A bell curve would be wrong because it's symmetric and could return absurd values like negative weeks or equal mass above and below. A lognormal distribution is naturally skewed this way: most values cluster near a lower bound, with a long tail stretching to the right.

Its defining trick: if X is lognormal, then ln(X) is a nice symmetric normal distribution. That's why the log appears in the code.

### **Step by step**

<ins>math.log(median)</ins>

<sub>median is the claim's median duration in weeks (e.g., 4.0 weeks for musculoskeletal). Taking its natural log gives the mean of the underlying normal — the center of the bell curve on the log scale. Using the median as the center is deliberate: for a lognormal, exp(mean of log) equals the median, not the mean. So a "median = 4 weeks" input really does produce draws whose median is 4 weeks. The arithmetic mean of the draws will sit slightly higher (lognormal distributions are skewed), which matches reality — a handful of very long claims pull the average up.</sub>

<ins>spread * 0.75</ins>

<sub>This scales your chosen spread value to become sigma (σ) — the standard deviation of the underlying normal. Sigma is what controls the shape of the lognormal, not just shifts it: with sigma ≈ 0, every draw lands right on the median; with larger sigma, draws spread out and the right tail gets heavier. The 0.75 factor is just a softening constant chosen so that typical spread inputs (1.0–1.2) produce realistic claim variation rather than extreme tails — nothing deeper than tuning. (A purist would derive sigma from the desired coefficient of variation; multiplying by a constant is the pragmatic equivalent.)</sub>

<ins>random.lognormvariate(mu, sigma)</ins>

<sub>The core sampler. It draws one random value from a lognormal with the given parameters — internally it draws z ~ N(0,1), computes mu + sigma * z, then applies exp() to the result. Statistically, this is exactly how real disability duration behaves: most claims resolve quickly, occasional ones stretch out for months.</sub>

<ins>max(0.25, ...) and min(52.0, ...) — the clamps</ins>

<sub>Note Python evaluates these inside out: first the max clamps the bottom, then min clamps the top. So the result is clamped to the range [0.25, 52.0]</sub>

> <sub>Floor at 0.25 — a claim can't be shorter than a quarter-week (~1.75 business days). This guards the downstream math: the lognormal can theoretically produce a value as close to zero as the RNG allows, and elsewhere the code does end = start + timedelta(days=max(weeks,0.25)*7 + elim) and weekly * weeks — a zero or near-zero duration would produce a degenerate same-day claim and would skew averages downward unrealistically.</sub>

> <sub>Ceiling at 52.0 — no simulated STD claim runs longer than a year. In group STD, claims running past 26 weeks typically convert to long-term disability and leave this dataset, so a 52-week cap keeps durations realistic.
One consequence worth knowing for your dashboard: because of that floor, the resulting distribution is a mix of "clip at 0.25" mass plus a smooth lognormal body — visually it will look like a small spike at the minimum followed by a smooth decay. And because of spread * 0.75, your spread parameter acts roughly as a one-sigma-width dial rather than a hard percent — the same input value yields the same spread every time thanks to the fixed seed.</sub>

<sub>Net effect: lognormal_wks(4.0, 1.1) gives you a claim duration that's most often around 3–5 weeks, occasionally 10+, and physically plausible throughout — which is precisely why this shape, not a plain average ± noise, is the standard choice for modeling absence durations.</sub>

## <ins>**DX data structure**</ins>

**weight**  reflect the general pattern reported repeatedly in group STD claim-mix studies and insurer/reinsurer publications — the kind of material from LIMRA, LIMRA Secure Retirement Institute surveys, and reinsurers like Gen Re or Munich Re that publish STD incidence and diagnosis-mix benchmarking reports.
> used once, when picking a diagnosis: random.choices(DX, weights=[d[2] for d in DX])[0]. The list comprehension [d[2] for d in DX] extracts position 2 from every tuple (that's why column order matters). Values are relative, not absolute percentages — 24 vs 6 means "musculoskeletal is 4× as common as respiratory." Summing to 97 rather than 100 is harmless; random.choices normalizes automatically. The ordering mirrors real-world STD claim mix: musculoskeletal and pregnancy dominate, rare categories like oncology at the bottom.

**median_weeks** 
> passed to lognormal_wks(med_wks, spread) as the center of the duration distribution. Note the clinical realism baked in: pregnancy has a tight, predictable duration (median 6.0, spread only 0.35 — deliveries don't vary much), while mental/behavioral claims run long (8.0 weeks) with high variability (1.2), and oncology is the longest (12.0).

**spread** 
>  spread * 0.75 = sigma of the underlying log-normal. Higher spread = fatter right tail = more occasional very long claims. Pregnancy's low spread is exactly why you won't see a 40-week maternity claim in the data.

**icd10_prefix** 
> written straight into the CSV as icd10_prefix. These are real ICD-10 chapter families (M54 = dorsalgia/back pain, O80 = normal delivery, F41 = anxiety, C50 = breast cancer), chosen so the data looks credible to anyone familiar with medical coding. It also demonstrates a deliberate simplification: a prefix stands in for dozens of specific codes — fine for demo purposes, unrealistic for actuarial work.



## **<ins>employers = {}</ins>**
This builds a dictionary of dictionaries a lookup table of 120 synthetic employers, keyed by employer ID.

## **<ins>employees = {}</ins>**
This builds a dictionary of dictionaries a lookup table of 120 synthetic employees, keyed by employee ID.

