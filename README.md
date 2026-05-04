# Cohort Retention: 2-Point Forecast

A practical approach to predicting how long users stick around — using just two data points and a logarithm.

## The problem

You run a product. You have cohorts. You know Day 1 retention (how many came back the next day) and Day 7 retention (how many came back a week later). You want to know: what will Day 30, 90, or 365 look like?

You could wait months. Or you can do math.

## How it works

User retention tends to follow a power law:

```
retention(t) = a × t^b
```

If you know two points — say Day 1 and Day 7 — you can solve for `a` and `b`:

```
b = ln(D7_retention / D1_retention) / ln(7)
a = D1_retention
```

Now plug any `t` into the formula. That's it. No ML, no black box — just curve fitting through two known points.

This approach is used by companies like Uber and Spotify when they need quick cohort forecasts without waiting for data to accumulate. It won't replace a full survival model, but it's directionally correct and takes 5 minutes.

## Try it

```bash
git clone https://github.com/GlitchG/cohort-log-predict.git
cd cohort-log-predict
pip install -r requirements.txt
python python/cohort_log_predict.py
```

Or use it directly:

```python
from python.cohort_log_predict import CohortLogPredictor

cohort = CohortLogPredictor(day1=0.45, day7=0.18, label="2025-Q1")
cohort.summary()
```

Output:

```
Cohort: 2025-Q1 Users
────────────────────────────────────────
  Day 1:  45.0%  (observed)
  Day 7:  18.0%  (observed)
  Model:  retention(t) = 0.4500 * t^-0.4709

  Day 30:    9.1%
  Day 90:    5.4%
  Day 180:   3.9%
  Day 365:   2.8%

  Half-life: 4 days
  Lifetime:  3243 days (108 months)
```

## Step-by-step: from raw data to forecast

### Step 1: Get your D1 and D7 numbers

If you use BigQuery + GA4, run [`sql/cohort_retention.sql`](sql/cohort_retention.sql). It groups users by their first-visit week and calculates Day 1 and Day 7 return rates. Minimum cohort size is set to 30 to avoid noise.

```sql
-- Extracts weekly cohorts with D1 & D7 retention
-- Uses public GA4 sample data, so you can run it without setup
```

### Step 2: Feed into the predictor

```python
from python.cohort_log_predict import CohortLogPredictor

# Your numbers from BigQuery
cohort = CohortLogPredictor(day1=0.45, day7=0.18, label="Jan 2025")
cohort.summary()
```

### Step 3: Compare cohorts

```python
from python.cohort_log_predict import MultiCohortPredictor

mc = MultiCohortPredictor()
mc.add_cohort("2024-Q4", day1=0.50, day7=0.22)
mc.add_cohort("2025-Q1", day1=0.45, day7=0.18)
mc.add_cohort("2025-Q2", day1=0.42, day7=0.15)

mc.compare()
mc.plot_comparison(days=365)
```

The comparison table shows which cohorts are decaying faster. A steeper `b` coefficient means users churn quicker — useful for spotting when product changes hurt retention.

## What you get

- Predictions for any day: 7, 30, 90, 180, 365
- Half-life: days until retention drops to 50% of Day 1
- Lifetime: days until retention falls below 1%
- Multi-cohort comparison with log-scale plots
- BigQuery SQL that works on GA4's public dataset

## Limitations

This is a two-point interpolation, not a fitted model. If your retention curve isn't a power law (some products aren't), the long-term predictions will drift. For critical decisions, validate against actual data once enough time passes.

## Files

```
python/cohort_log_predict.py    — Predictor class + multi-cohort comparison
sql/cohort_retention.sql        — BigQuery SQL to extract D1/D7 from GA4
requirements.txt                — numpy, pandas, scipy, matplotlib
```

## Related projects

- [GA4 Attribution Models](https://github.com/GlitchG/ga4-attribution-models) — SQL-based attribution
- [Marketing Analytics dbt](https://github.com/GlitchG/marketing_analytics_sample_reporting) — dbt pipeline for paid ads

---

MIT License
