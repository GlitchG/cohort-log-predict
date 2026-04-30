-- cohort_retention.sql
-- Extract Day 1 and Day 7 retention per weekly cohort from GA4 in BigQuery
-- Output: cohort_week, users, day1_retention, day7_retention

CREATE OR REPLACE VIEW `your_project.cohort_analysis.weekly_cohort_retention` AS
WITH user_first_visit AS (
  -- When did each user first appear?
  SELECT
    user_pseudo_id,
    DATE_TRUNC(MIN(PARSE_DATE('%Y%m%d', event_date)), WEEK(MONDAY)) AS cohort_week
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20210101' AND '20221231'
  GROUP BY 1
),
user_activity AS (
  -- Which days did each user return?
  SELECT
    user_pseudo_id,
    PARSE_DATE('%Y%m%d', event_date) AS event_date
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20210101' AND '20221231'
  GROUP BY 1, 2
),
cohort_retention AS (
  SELECT
    f.cohort_week,
    f.user_pseudo_id,
    MIN(a.event_date) AS first_date,
    MAX(a.event_date) AS last_date,
    -- Days between cohort start and each activity
    DATE_DIFF(MIN(a.event_date), f.cohort_week, DAY) AS day_0_offset,
    -- Returned on Day 1? (next day after cohort start)
    MAX(CASE WHEN DATE_DIFF(a.event_date, f.cohort_week, DAY) = 1 THEN 1 ELSE 0 END) AS returned_day1,
    -- Returned on Day 7?
    MAX(CASE WHEN DATE_DIFF(a.event_date, f.cohort_week, DAY) = 7 THEN 1 ELSE 0 END) AS returned_day7
  FROM user_first_visit f
  JOIN user_activity a ON f.user_pseudo_id = a.user_pseudo_id
  GROUP BY 1, 2
)
SELECT
  cohort_week,
  COUNT(DISTINCT user_pseudo_id) AS cohort_size,
  -- Day 1 retention (next-day return)
  ROUND(SUM(returned_day1) / COUNT(DISTINCT user_pseudo_id), 4) AS d1_retention,
  -- Day 7 retention (week-later return)
  ROUND(SUM(returned_day7) / COUNT(DISTINCT user_pseudo_id), 4) AS d7_retention,
  -- D7/D1 stickiness ratio
  ROUND(
    SAFE_DIVIDE(
      SUM(returned_day7),
      NULLIF(SUM(returned_day1), 0)
    ), 4
  ) AS stickiness_ratio
FROM cohort_retention
GROUP BY 1
HAVING cohort_size >= 30  -- Minimum cohort size for statistical validity
ORDER BY cohort_week;
