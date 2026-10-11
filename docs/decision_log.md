# Decision log

# Decision log

## Primary metric
Day-7 retention. Chosen before seeing results. Predicts long-term engagement
better than day-1 retention, which is noisier.

## Practical threshold
0.5 percentage points. Below this, the change is likely too small to justify
changing a live game.

## Outlier handling
Game rounds have a heavy right tail (max 49,854). Use medians and trimmed
Welch test for the secondary rounds comparison. Keep the outlier in retention
counts to avoid bias.
