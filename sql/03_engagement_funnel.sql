-- 03_engagement_funnel.sql
-- NOTE: game rounds are not the same as levels, so these thresholds describe
-- how engaged players were. They do not mark the exact position of the gate.

-- 1. Engagement funnel per group (counts).
SELECT version,
       COUNT(*)                  AS installs,
       SUM(sum_gamerounds >= 1)  AS played_1_plus,
       SUM(sum_gamerounds >= 30) AS played_30_plus,
       SUM(sum_gamerounds >= 40) AS played_40_plus,
       SUM(retention_1)          AS back_day_1,
       SUM(retention_7)          AS back_day_7
FROM players
GROUP BY version;

-- 2. The same funnel as a percentage of installs.
SELECT version,
       ROUND(100.0 * SUM(sum_gamerounds >= 1)  / COUNT(*), 2) AS pct_played_1_plus,
       ROUND(100.0 * SUM(sum_gamerounds >= 30) / COUNT(*), 2) AS pct_played_30_plus,
       ROUND(100.0 * SUM(sum_gamerounds >= 40) / COUNT(*), 2) AS pct_played_40_plus,
       ROUND(100.0 * SUM(retention_1)          / COUNT(*), 2) AS pct_back_day_1,
       ROUND(100.0 * SUM(retention_7)          / COUNT(*), 2) AS pct_back_day_7
FROM players
GROUP BY version;

-- 3. Day-7 retention by engagement bucket (DESCRIPTIVE ONLY).
-- Rounds are affected by the version a player saw, so slicing by them cannot
-- show cause and effect. Use this to describe players, not to prove a result.
WITH bucketed AS (
    SELECT version, retention_7,
           CASE WHEN sum_gamerounds = 0   THEN '0'
                WHEN sum_gamerounds < 10  THEN '1-9'
                WHEN sum_gamerounds < 30  THEN '10-29'
                WHEN sum_gamerounds < 100 THEN '30-99'
                ELSE '100+' END AS rounds_bucket
    FROM players
)
SELECT rounds_bucket, version, COUNT(*) AS players,
       ROUND(100.0 * AVG(retention_7), 2) AS day7_retention_pct
FROM bucketed
GROUP BY rounds_bucket, version
ORDER BY rounds_bucket, version;
