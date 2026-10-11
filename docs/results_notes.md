# Results notes

My interpretation of docs/results.md. Written after running run_analysis.py.

## 1. Data checks

The groups are close to 50/50 but not exactly (44,700 vs 45,489). The sample
ratio p-value is 0.0086 — moderate, above the serious threshold of 0.001 but
worth mentioning. The 49,854-round outlier stands out clearly.

## 2. Primary result (day-7 retention)

Day-7 retention was 19.02% for gate_30 and 18.20% for gate_40 — a difference
of -0.82 pp. The 95% CI runs from -1.33 to -0.31 pp, entirely below zero.
With p = 0.0016, the difference is statistically significant. The bootstrap
CI (-1.34 to -0.31) matches the formula CI closely, so I am confident in the
result.

## 3. Decision-rule outcome

The decision rule returned "inconclusive." Even though the effect is
significant, the confidence interval straddles the -0.5 pp practical
threshold — I can't confirm gate_40 is worse by more than the smallest
change that matters.

## 4. Secondary metrics

Day-1 retention showed a -0.59 pp drop with p = 0.0744 — not significant
after Holm correction (adjusted to 0.1506). Game rounds also showed no
significant effect after adjustment. The trimmed Welch test (p = 0.8699)
confirmed the raw difference in rounds is driven by the outlier.

## 5. Power

With 44,700 players per group, the smallest effect I can reliably detect is
about 0.74 pp. Detecting the plan's 0.5 pp threshold would require ~97,700
per group — over double what we have. So the test could not resolve effects
in the 0.5 to 0.74 pp range, and my inconclusive result reflects this.