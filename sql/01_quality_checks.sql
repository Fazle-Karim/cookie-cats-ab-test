-- 01_quality_checks.sql
-- Run each query separately and write down what you see in docs/data_quality.md.

-- 1. Row count and distinct users. Both numbers must be equal.
SELECT COUNT(*) AS total_rows, COUNT(DISTINCT userid) AS distinct_users
FROM players;

-- 2. Missing values in every column. All should be 0.
SELECT SUM(userid IS NULL)         AS null_userid,
       SUM(version IS NULL)        AS null_version,
       SUM(sum_gamerounds IS NULL) AS null_rounds,
       SUM(retention_1 IS NULL)    AS null_ret1,
       SUM(retention_7 IS NULL)    AS null_ret7
FROM players;

-- 3. Which group labels exist? Expect exactly two.
SELECT version, COUNT(*) AS players
FROM players
GROUP BY version;

-- 4. Range of game rounds. Look at the maximum: is it believable?
SELECT MIN(sum_gamerounds) AS min_rounds, MAX(sum_gamerounds) AS max_rounds
FROM players;

-- 5. Players who never played a round, by group.
SELECT version, SUM(sum_gamerounds = 0) AS zero_round_players
FROM players
GROUP BY version;

-- 6. Logic check: retained on day 7 but not on day 1 (possible, but note it).
SELECT version, COUNT(*) AS ret7_without_ret1
FROM players
WHERE retention_7 = 1 AND retention_1 = 0
GROUP BY version;

-- 7. Logic check: retained although they played zero rounds.
SELECT version, COUNT(*) AS retained_but_zero_rounds
FROM players
WHERE sum_gamerounds = 0 AND (retention_1 = 1 OR retention_7 = 1)
GROUP BY version;
