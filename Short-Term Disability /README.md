### **SHORT-TERM DISABILITY**
## claimGenerator.py 
#def lognormal_wks(median, spread)

**Why lognormal?**

Human durations like hospital stays, claim durations, or absence lengths are almost always right-skewed: most claims resolve around a typical value (say, 4 weeks), but a few outliers drag on much longer. A bell curve would be wrong because it's symmetric and could return absurd values like negative weeks or equal mass above and below. A lognormal distribution is naturally skewed this way: most values cluster near a lower bound, with a long tail stretching to the right.

Its defining trick: if X is lognormal, then ln(X) is a nice symmetric normal distribution. That's why the log appears in the code.

**Step by step**

<ins>math.log(median)</ins>

<sub>median is the claim's median duration in weeks (e.g., 4.0 weeks for musculoskeletal). Taking its natural log gives the mean of the underlying normal — the center of the bell curve on the log scale. Using the median as the center is deliberate: for a lognormal, exp(mean of log) equals the median, not the mean. So a "median = 4 weeks" input really does produce draws whose median is 4 weeks. The arithmetic mean of the draws will sit slightly higher (lognormal distributions are skewed), which matches reality — a handful of very long claims pull the average up.</sub>

<ins>spread * 0.75</ins>

<sub>This scales your chosen spread value to become sigma (σ) — the standard deviation of the underlying normal. Sigma is what controls the shape of the lognormal, not just shifts it: with sigma ≈ 0, every draw lands right on the median; with larger sigma, draws spread out and the right tail gets heavier. The 0.75 factor is just a softening constant chosen so that typical spread inputs (1.0–1.2) produce realistic claim variation rather than extreme tails — nothing deeper than tuning. (A purist would derive sigma from the desired coefficient of variation; multiplying by a constant is the pragmatic equivalent.)</sub>

random.lognormvariate(mu, sigma)

The core sampler. It draws one random value from a lognormal with the given parameters — internally it draws z ~ N(0,1), computes mu + sigma * z, then applies exp() to the result. Statistically, this is exactly how real disability duration behaves: most claims resolve quickly, occasional ones stretch out for months.

max(0.25, ...) and min(52.0, ...) — the clamps

Note Python evaluates these inside out: first the max clamps the bottom, then min clamps the top. So the result is clamped to the range [0.25, 52.0]

Floor at 0.25 — a claim can't be shorter than a quarter-week (~1.75 business days). This guards the downstream math: the lognormal can theoretically produce a value as close to zero as the RNG allows, and elsewhere the code does end = start + timedelta(days=max(weeks,0.25)*7 + elim) and weekly * weeks — a zero or near-zero duration would produce a degenerate same-day claim and would skew averages downward unrealistically.
Ceiling at 52.0 — no simulated STD claim runs longer than a year. In group STD, claims running past 26 weeks typically convert to long-term disability and leave this dataset, so a 52-week cap keeps durations realistic.
One consequence worth knowing for your dashboard: because of that floor, the resulting distribution is a mix of "clip at 0.25" mass plus a smooth lognormal body — visually it will look like a small spike at the minimum followed by a smooth decay. And because of spread * 0.75, your spread parameter acts roughly as a one-sigma-width dial rather than a hard percent — the same input value yields the same spread every time thanks to the fixed seed.

Net effect: lognormal_wks(4.0, 1.1) gives you a claim duration that's most often around 3–5 weeks, occasionally 10+, and physically plausible throughout — which is precisely why this shape, not a plain average ± noise, is the standard choice for modeling absence durations.

