# Recommendation memo

**To:** Product Lead, Cookie Cats
**From:** Fazle Karim
**Date:** 2026-10-11

## Recommendation

Do not move the first gate from level 30 to level 40 yet — the data cannot rule
out a meaningful drop in day-7 retention. Collect more data before deciding.

## Evidence

- **Primary metric (day-7 retention):** gate_30 = 19.02%, gate_40 = 18.20%.
  Difference = -0.82 pp (95% CI -1.33 to -0.31 pp, p = 0.0016). The effect is
  statistically significant, but the interval overlaps the -0.5 pp threshold
  we defined as "smallest change that matters."

- **Secondary metrics:** day-1 retention dropped -0.59 pp (95% CI -1.24 to
  +0.06 pp, p = 0.0744). Game rounds showed no significant difference after
  Holm correction (Mann-Whitney p = 0.0502 → adjusted 0.1506; trimmed Welch
  p = 0.8699). No secondary metric is significant after multiple-testing
  correction.

- **Robustness:** a bootstrap 95% CI (-1.34 to -0.31 pp) closely matches the
  formula CI, so the interval is reliable. The largest game-round value
  (49,854) is a single outlier; it does not drive the retention result.

## What this means in numbers

If the measured effect is real, at 100,000 new installs per month we would
expect roughly 820 fewer retained players at day 7 — but the interval spans
310 to 1,330 fewer, so the size is uncertain.

## Risks and limits

- Only day-1 and day-7 retention are available. No revenue, no longer-term
  retention.
- Random assignment is assumed; the sample ratio check shows mild imbalance
  (p = 0.0086), above the serious-alarm threshold but worth monitoring.
- The test was powered for effects of 0.74 pp or larger, but not for the
  0.5 pp threshold from the plan. Non-significant secondary results reflect
  this, not evidence of no effect.

## Next steps

1. Run the test for a longer period or with more traffic to reach ~98,000
   players per group and settle the 0.5 pp question.
2. Instrument revenue per retained player so future decisions can weigh
   retention loss against monetization gain.
3. Keep the gate at level 30 in the meantime — the direction of the current
   evidence is negative, not positive.