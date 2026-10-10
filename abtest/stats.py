"""Statistical helpers for the Cookie Cats A/B test.

Convention used everywhere:
    control   = gate_30 (the existing game)
    treatment = gate_40 (the new version)
    difference = treatment - control, in absolute terms (0.01 = 1 percentage point)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import stats
from scipy.optimize import brentq


@dataclass(frozen=True)
class ProportionTest:
    p_control: float
    p_treatment: float
    diff: float        # treatment - control (absolute)
    rel_lift: float    # diff / p_control
    z: float
    p_value: float     # two-sided
    ci_low: float      # confidence interval for diff
    ci_high: float


def _check_counts(x: int, n: int) -> None:
    if n <= 0:
        raise ValueError("n must be positive")
    if x < 0 or x > n:
        raise ValueError("x must be between 0 and n")


def two_proportion_test(x_control, n_control, x_treatment, n_treatment, alpha=0.05):
    """Two-sided two-proportion z-test plus a Wald confidence interval."""
    _check_counts(x_control, n_control)
    _check_counts(x_treatment, n_treatment)

    p1 = x_control / n_control
    p2 = x_treatment / n_treatment
    diff = p2 - p1

    # Test statistic uses the pooled rate because H0 says both rates are equal.
    pooled = (x_control + x_treatment) / (n_control + n_treatment)
    se_pooled = math.sqrt(pooled * (1 - pooled) * (1 / n_control + 1 / n_treatment))
    z = diff / se_pooled if se_pooled > 0 else 0.0
    p_value = float(2 * stats.norm.sf(abs(z)))

    # Confidence interval uses separate rates (no assumption that they are equal).
    se = math.sqrt(p1 * (1 - p1) / n_control + p2 * (1 - p2) / n_treatment)
    z_crit = stats.norm.ppf(1 - alpha / 2)
    rel = diff / p1 if p1 > 0 else float("nan")
    return ProportionTest(p1, p2, diff, rel, float(z), p_value,
                          diff - z_crit * se, diff + z_crit * se)


def sample_ratio_mismatch(n_control, n_treatment, expected_share_control=0.5):
    """Chi-square test that group sizes match the planned split.

    Returns (chi2, p_value). A very small p-value means the split is not what
    was planned, which can mean the randomisation or the data is broken.
    """
    if n_control <= 0 or n_treatment <= 0:
        raise ValueError("group sizes must be positive")
    total = n_control + n_treatment
    expected = [total * expected_share_control, total * (1 - expected_share_control)]
    chi2, p = stats.chisquare([n_control, n_treatment], f_exp=expected)
    return float(chi2), float(p)


def bootstrap_diff(x_control, n_control, x_treatment, n_treatment,
                   n_boot=10_000, alpha=0.05, seed=42):
    """Parametric bootstrap interval for the difference in proportions.

    Each replicate draws new success counts from binomial distributions that use
    the observed rates, then recomputes the difference. It is a cross-check on
    the formula-based interval.
    """
    _check_counts(x_control, n_control)
    _check_counts(x_treatment, n_treatment)
    rng = np.random.default_rng(seed)
    p1 = rng.binomial(n_control, x_control / n_control, size=n_boot) / n_control
    p2 = rng.binomial(n_treatment, x_treatment / n_treatment, size=n_boot) / n_treatment
    diffs = p2 - p1
    low, high = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"diff_mean": float(diffs.mean()), "ci_low": float(low), "ci_high": float(high)}


def welch_from_summary(mean_c, std_c, n_c, mean_t, std_t, n_t, alpha=0.05):
    """Welch t-test (unequal variances) from summary statistics."""
    t, p = stats.ttest_ind_from_stats(mean_t, std_t, n_t, mean_c, std_c, n_c,
                                      equal_var=False)
    diff = mean_t - mean_c
    v_t, v_c = std_t ** 2 / n_t, std_c ** 2 / n_c
    se = math.sqrt(v_t + v_c)
    df = (v_t + v_c) ** 2 / (v_t ** 2 / (n_t - 1) + v_c ** 2 / (n_c - 1))
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    return {"diff": diff, "t": float(t), "p_value": float(p),
            "ci_low": diff - t_crit * se, "ci_high": diff + t_crit * se}


def holm_adjust(p_values: dict) -> dict:
    """Holm-Bonferroni adjustment for several tests (controls false positives)."""
    items = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted, running_max = {}, 0.0
    for i, (name, p) in enumerate(items):
        running_max = max(running_max, min(1.0, (m - i) * p))
        adjusted[name] = running_max
    return adjusted


# ---- Power and sample size ------------------------------------------------

def required_n_per_group(p_base, mde_abs, alpha=0.05, power=0.80):
    """Players needed in EACH group to detect an absolute lift of mde_abs."""
    p1, p2 = p_base, p_base + mde_abs
    if not (0 < p1 < 1 and 0 < p2 < 1) or mde_abs == 0:
        raise ValueError("rates must be inside (0, 1) and the effect must be non-zero")
    z_a = stats.norm.ppf(1 - alpha / 2)
    z_b = stats.norm.ppf(power)
    p_bar = (p1 + p2) / 2
    numerator = (z_a * math.sqrt(2 * p_bar * (1 - p_bar))
                 + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(numerator / mde_abs ** 2)


def power_for_n(p_base, mde_abs, n_per_group, alpha=0.05):
    """Probability that the test detects an effect of mde_abs with n per group."""
    p1, p2 = p_base, p_base + mde_abs
    z_a = stats.norm.ppf(1 - alpha / 2)
    p_bar = (p1 + p2) / 2
    se0 = math.sqrt(2 * p_bar * (1 - p_bar) / n_per_group)
    se1 = math.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / n_per_group)
    d = abs(mde_abs)
    return float(stats.norm.cdf((d - z_a * se0) / se1)
                 + stats.norm.cdf((-d - z_a * se0) / se1))


def minimum_detectable_effect(p_base, n_per_group, alpha=0.05, power=0.80):
    """Smallest absolute lift the test could detect with the stated power."""
    upper = min(0.5, 1 - p_base - 1e-6)
    return float(brentq(lambda d: power_for_n(p_base, d, n_per_group, alpha) - power,
                        1e-7, upper))


def impact_scenario(diff, ci_low, ci_high, players, value_per_player):
    """Turn a rate difference into extra players and value for a scenario."""
    return {"expected_players": diff * players,
            "low_players": ci_low * players,
            "high_players": ci_high * players,
            "expected_value": diff * players * value_per_player,
            "low_value": ci_low * players * value_per_player,
            "high_value": ci_high * players * value_per_player}


def classify_result(ci_low, ci_high, threshold):
    """Apply a decision rule that was written down BEFORE looking at the data.

    threshold = smallest absolute change that would matter to the business.
    Returns one of: ship, keep_control, no_practical_difference, inconclusive.
    """
    if ci_low >= threshold:
        return "ship"                       # clearly better by a meaningful amount
    if ci_high <= -threshold:
        return "keep_control"               # clearly worse by a meaningful amount
    if ci_low > -threshold and ci_high < threshold:
        return "no_practical_difference"    # whole interval is trivially small
    return "inconclusive"                   # interval mixes meaningful and trivial


DECISION_TEXT = {
    "ship": "Move to the new version: the improvement is large enough to matter.",
    "keep_control": "Keep the current version: the new version is clearly worse.",
    "no_practical_difference": "No practical difference: choose on cost or other factors.",
    "inconclusive": "Inconclusive: the data cannot rule out a meaningful effect either way.",
}
