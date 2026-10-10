# Analysis plan

**Written before looking at any results.** Date written: ____-__-__

## 1. Question and decision
- Question: Does moving the first gate from level 30 to level 40 change player retention?
- Decision this supports: keep the gate at level 30, or move it to level 40.

## 2. Groups
- Control: gate_30 (current game). Treatment: gate_40 (new version).
- Difference is always treatment minus control.

## 3. Metrics (fixed now)
- Primary: day-7 retention (share of players who return 7 days after install).
- Secondary: day-1 retention; game rounds in the first 14 days.
- Guardrail: day-1 retention must not drop meaningfully.

## 4. Statistical plan
- Significance level alpha = 0.05 (two-sided).
- Primary test: two-proportion z-test with a 95% confidence interval.
- Cross-check: bootstrap interval.
- Secondary tests: Holm adjustment for the several secondary p-values.
- Game rounds are heavy-tailed: use Mann-Whitney U and a trimmed Welch test.
- Sample ratio check on the group sizes before any other test.

## 5. Decision rule
- Smallest change that matters (practical threshold): 0.5 percentage points of day-7 retention.
- Why this number: (write your own reasoning here, one or two sentences)
- Ship gate_40 only if the whole confidence interval is above +0.5 pp.
- Keep gate_30 if the whole interval is below -0.5 pp.
- If the interval lies inside -0.5 to +0.5 pp: no practical difference.
- Otherwise: inconclusive, and say how much more data is needed.

## 6. Things I will NOT do
- Change the primary metric or the threshold after seeing results.
- Report only the tests that look good.
- Slice by variables affected by the treatment and call it proof.
