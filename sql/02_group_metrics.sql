-- 02_group_metrics.sql

-- 1. Headline metrics per group.
SELECT version,
       COUNT(*)                                AS players,
       ROUND(100.0 * AVG(retention_1), 2)      AS day1_retention_pct,
       ROUND(100.0 * AVG(retention_7), 2)      AS day7_retention_pct,
       ROUND(AVG(sum_gamerounds), 2)           AS mean_rounds,
       MAX(sum_gamerounds)                     AS max_rounds
FROM players
GROUP BY version
ORDER BY version;

-- 2. Median rounds per group (SQLite has no MEDIAN, so use row numbers).
WITH ranked AS (
    SELECT version, sum_gamerounds,
           ROW_NUMBER() OVER (PARTITION BY version ORDER BY sum_gamerounds) AS rn,
           COUNT(*)     OVER (PARTITION BY version)                         AS cnt
    FROM players
)
SELECT version, AVG(sum_gamerounds) AS median_rounds
FROM ranked
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
GROUP BY version;

-- 3. The five largest values per group (look for outliers).
WITH ranked AS (
    SELECT version, userid, sum_gamerounds,
           ROW_NUMBER() OVER (PARTITION BY version ORDER BY sum_gamerounds DESC) AS rn
    FROM players
)
SELECT version, userid, sum_gamerounds
FROM ranked
WHERE rn <= 5
ORDER BY version, rn;

-- 4. Mean rounds after removing the top 0.1% of players in each group.
WITH ranked AS (
    SELECT version, sum_gamerounds,
           ROW_NUMBER() OVER (PARTITION BY version ORDER BY sum_gamerounds DESC) AS rn_desc,
           COUNT(*)     OVER (PARTITION BY version)                              AS cnt
    FROM players
)
SELECT version, ROUND(AVG(sum_gamerounds), 2) AS mean_rounds_without_top_0_1pct
FROM ranked
WHERE rn_desc > cnt * 0.001
GROUP BY version;
