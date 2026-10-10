import pytest
from scipy.stats import chi2_contingency

from abtest import stats as ab


def test_identical_groups_have_no_difference():
    r = ab.two_proportion_test(450, 1000, 450, 1000)
    assert r.diff == 0
    assert r.p_value == pytest.approx(1.0)
    assert r.ci_low == pytest.approx(-r.ci_high)


def test_matches_independent_chi_square_test():
    # A 2x2 chi-square test without correction gives the same p-value as the z-test.
    r = ab.two_proportion_test(200, 1000, 250, 1000)
    chi2, p, _, _ = chi2_contingency([[200, 800], [250, 750]], correction=False)
    assert r.p_value == pytest.approx(p, rel=1e-6)
    assert r.z ** 2 == pytest.approx(chi2, rel=1e-6)


def test_interval_contains_the_estimate():
    r = ab.two_proportion_test(200, 1000, 250, 1000)
    assert r.ci_low < r.diff < r.ci_high
    assert r.diff == pytest.approx(0.05)
    assert r.rel_lift == pytest.approx(0.25)


def test_bad_inputs_raise():
    with pytest.raises(ValueError):
        ab.two_proportion_test(5, 0, 5, 10)
    with pytest.raises(ValueError):
        ab.two_proportion_test(11, 10, 5, 10)


def test_sample_ratio_mismatch():
    _, p_equal = ab.sample_ratio_mismatch(5000, 5000)
    _, p_skewed = ab.sample_ratio_mismatch(5000, 5500)
    assert p_equal == pytest.approx(1.0)
    assert p_skewed < 0.001


def test_bootstrap_is_reproducible_and_close_to_formula():
    a = ab.bootstrap_diff(4000, 10000, 4200, 10000, seed=1)
    b = ab.bootstrap_diff(4000, 10000, 4200, 10000, seed=1)
    assert a == b
    f = ab.two_proportion_test(4000, 10000, 4200, 10000)
    assert a["ci_low"] == pytest.approx(f.ci_low, abs=0.003)
    assert a["ci_high"] == pytest.approx(f.ci_high, abs=0.003)


def test_welch_from_summary_detects_a_clear_difference():
    r = ab.welch_from_summary(10, 2, 1000, 11, 2, 1000)
    assert r["diff"] == pytest.approx(1.0)
    assert r["p_value"] < 0.001
    assert r["ci_low"] < 1.0 < r["ci_high"]


def test_holm_adjustment():
    adj = ab.holm_adjust({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj["a"] == pytest.approx(0.03)
    assert adj["c"] == pytest.approx(0.06)
    assert adj["b"] == pytest.approx(0.06)


def test_required_sample_size_known_case():
    # Detecting 10% -> 12% at alpha 0.05 and 80% power needs about 3,800 per group.
    n = ab.required_n_per_group(0.10, 0.02)
    assert 3700 < n < 3950


def test_power_and_sample_size_are_consistent():
    n = ab.required_n_per_group(0.18, 0.005)
    assert ab.power_for_n(0.18, 0.005, n) == pytest.approx(0.80, abs=0.005)


def test_minimum_detectable_effect_inverts_sample_size():
    n = ab.required_n_per_group(0.18, 0.01)
    assert ab.minimum_detectable_effect(0.18, n) == pytest.approx(0.01, rel=0.02)


def test_impact_scenario_scales_with_players():
    r = ab.impact_scenario(0.01, 0.005, 0.015, 100_000, 2.0)
    assert r["expected_players"] == pytest.approx(1000)
    assert r["expected_value"] == pytest.approx(2000)
    assert r["low_value"] < r["expected_value"] < r["high_value"]


def test_decision_rule():
    assert ab.classify_result(0.006, 0.012, 0.005) == "ship"
    assert ab.classify_result(-0.012, -0.006, 0.005) == "keep_control"
    assert ab.classify_result(-0.002, 0.003, 0.005) == "no_practical_difference"
    assert ab.classify_result(-0.004, 0.009, 0.005) == "inconclusive"
