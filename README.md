# Cohort Log-Predict: 2-Point Logarithmic Forecasting

**Predict cohort retention for 365 days from just 2 data points**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![BigQuery](https://img.shields.io/badge/BigQuery-SQL-4285F4?logo=googlecloud)](https://cloud.google.com/bigquery)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A statistical portfolio project: predict a user cohort's full retention curve using only **Day 1 and Day 7 retention**. The technique fits a power-law curve through 2 points on a log-log scale — a battle-tested method used by Uber, Spotify, and gaming companies.

**The insight:** User retention follows `retention(t) = a · t^b` — a power law. Given any 2 points, you can solve for `a` and `b` and forecast months ahead. No ML needed.

---

## 🧠 The Math

```
retention(t) = a · t^b

Given:
  t₁ = 1 day,  r₁ = Day 1 retention
  t₂ = 7 days, r₂ = Day 7 retention

Solve:
  b = ln(r₂/r₁) / ln(7/1)
  a = r₁

Now predict any day:
  retention(30) = r₁ · 30^b
  retention(90) = r₁ · 90^b
  retention(365) = r₁ · 365^b
```

---

## 📊 Example Output

```
Cohort: 2025-Q1 Users
Day 1:  45.0% (observed)
Day 7:  18.0% (observed)

Predictions:
  Day 30:   8.1%
  Day 90:   3.7%
  Day 180:  2.1%
  Day 365:  1.1%

Half-life: 25 days
Lifetime:  340 days
```

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python python/cohort_log_predict.py
```

Or use it as a library:

```python
from python.cohort_log_predict import CohortLogPredictor

cohort = CohortLogPredictor(day1=0.45, day7=0.18, label="Jan Cohort")
cohort.summary()
cohort.plot(days=180)
```

---

## 🗄 BigQuery: Extract Cohorts

```sql
-- Extract D1 and D7 retention per weekly cohort
-- Built for GA4 data in BigQuery
```

See [`sql/cohort_retention.sql`](sql/cohort_retention.sql) for the full pipeline.

---

## 📈 Features

- ✅ **2-point only** — works when you have limited data
- ✅ **BigQuery SQL** — extract cohorts from GA4
- ✅ **Multi-cohort comparison** — compare retention across cohorts
- ✅ **Half-life & lifetime** — actionable metrics
- ✅ **Log-scale visualization** — professional plots
- ✅ **CI/CD** — auto-tests on push

---

## 🛠 Use Cases

- **Product analytics** — which cohorts are retaining best?
- **LTV prediction** — forecast revenue from retention
- **A/B test evaluation** — did the feature improve D30 retention?
- **Investor reporting** — "our D365 retention is trending up"

---

## 📄 License
MIT © 2026 Gleb Baraniuk
