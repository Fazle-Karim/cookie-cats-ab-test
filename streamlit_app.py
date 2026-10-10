"""Streamlit app: Cookie Cats A/B test (first gate at level 30 vs level 40)."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from abtest import stats as ab

st.set_page_config(page_title="Cookie Cats A/B Test", layout="wide")

DATA = Path(__file__).parent / "data" / "processed"
CONTROL, TREATMENT = "gate_30", "gate_40"
THRESHOLD = 0.005   # smallest change that matters: 0.5 percentage points

# Edit this text after you finish the analysis (it should match docs/memo.md).
RECOMMENDATION = (
    "Replace this paragraph with your recommendation from docs/memo.md: "
    "what to do, the evidence in one sentence, and the main caveat."
)


@st.cache_data
def load_data():
    summary = pd.read_csv(DATA / "summary.csv").set_index("version")
    hist = pd.read_csv(DATA / "rounds_hist.csv")
    return summary, hist


summary, hist = load_data()
ctrl, treat = summary.loc[CONTROL], summary.loc[TREATMENT]

st.sidebar.header("Settings")
alpha = st.sidebar.slider("Significance level (alpha)", 0.01, 0.10, 0.05, 0.01)
st.sidebar.caption("A lower alpha asks for stronger evidence. The intervals use "
                   "a confidence level of 1 - alpha.")


def pct(x):
    return f"{100 * x:.2f}%"


def pp(x):
    return f"{100 * x:+.2f} pp"


def retention_test(column):
    return ab.two_proportion_test(int(ctrl[column]), int(ctrl["players"]),
                                  int(treat[column]), int(treat["players"]), alpha)


st.title("Does moving the first gate from level 30 to level 40 change retention?")

tab_overview, tab_groups, tab_results, tab_impact, tab_methods = st.tabs(
    ["Overview", "Groups and checks", "Test results", "Impact and power",
     "Methods and limits"])

# ---------------------------------------------------------------- Overview
with tab_overview:
    day7 = retention_test("retained_day7")
    decision = ab.classify_result(day7.ci_low, day7.ci_high, THRESHOLD)

    st.subheader("The question")
    st.write("A mobile game pauses progress at a gate. Half of new players hit the "
             f"gate at level 30 ({CONTROL}, control) and half at level 40 "
             f"({TREATMENT}, new). Should the game move the gate to level 40?")
    st.write("**Primary metric:** share of players who return 7 days after installing. "
             f"**Smallest change that matters:** {pp(THRESHOLD)}.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Day-7 retention, gate 30 (control)", pct(day7.p_control))
    col2.metric("Day-7 retention, gate 40 (new)", pct(day7.p_treatment), pp(day7.diff))
    col3.metric("Decision rule result", decision.replace("_", " ").title())
    st.info(ab.DECISION_TEXT[decision])

    st.subheader("Recommendation")
    st.write(RECOMMENDATION)

# ---------------------------------------------------------- Groups and checks
with tab_groups:
    st.subheader("Group sizes and balance")
    chi2, p_srm = ab.sample_ratio_mismatch(int(ctrl["players"]), int(treat["players"]))
    st.dataframe(summary[["players", "retained_day1", "retained_day7",
                          "zero_round_players", "median_rounds", "max_rounds"]])
    st.write(f"Sample ratio check against a 50/50 split: chi-square = {chi2:.2f}, "
             f"p = {p_srm:.4f}.")
    if p_srm < 0.001:
        st.warning("The group sizes differ from the planned split more than chance "
                   "would explain. Investigate before trusting the results.")
    else:
        st.success("Group sizes are consistent with the planned 50/50 split.")

    st.subheader("Distribution of game rounds (first 14 days)")
    labels = [f"{s}-{s + 9}" if s < 200 else "200+" for s in
              sorted(hist["bin_start"].unique())]
    fig = go.Figure()
    for version in (CONTROL, TREATMENT):
        part = hist[hist["version"] == version].sort_values("bin_start")
        fig.add_bar(x=labels, y=part["players"], name=version)
    fig.update_layout(barmode="group", xaxis_title="Game rounds",
                      yaxis_title="Players", height=380)
    st.plotly_chart(fig)
    st.caption("Most players play very few rounds, and a few play thousands, so "
               "averages of rounds can be misleading. Medians are more reliable.")

# ------------------------------------------------------------- Test results
with tab_results:
    choice = st.selectbox("Metric", ["Day-7 retention (primary)",
                                     "Day-1 retention (secondary)"])
    column = "retained_day7" if choice.startswith("Day-7") else "retained_day1"
    r = retention_test(column)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Control (gate 30)", pct(r.p_control))
    c2.metric("New (gate 40)", pct(r.p_treatment))
    c3.metric("Difference", pp(r.diff))
    c4.metric("p-value", f"{r.p_value:.4f}")

    fig = go.Figure()
    fig.add_vrect(x0=-100 * THRESHOLD, x1=100 * THRESHOLD, opacity=0.15, line_width=0)
    fig.add_vline(x=0, line_dash="dash")
    fig.add_trace(go.Scatter(
        x=[100 * r.diff], y=["gate_40 minus gate_30"], mode="markers",
        error_x=dict(type="data", symmetric=False,
                     array=[100 * (r.ci_high - r.diff)],
                     arrayminus=[100 * (r.diff - r.ci_low)])))
    fig.update_layout(xaxis_title="Difference in retention (percentage points)",
                      height=260, showlegend=False)
    st.plotly_chart(fig)
    st.caption("The dot is the measured difference and the line is the confidence "
               "interval. The shaded band is the zone where a change is too small "
               "to matter.")

    verdict = "is" if r.p_value < alpha else "is not"
    st.write(f"The difference {verdict} statistically significant at alpha = "
             f"{alpha:.2f}. The interval runs from {pp(r.ci_low)} to {pp(r.ci_high)}. "
             f"Relative change: {100 * r.rel_lift:+.1f}%.")

    with st.expander("Cross-check with a bootstrap"):
        b = ab.bootstrap_diff(int(ctrl[column]), int(ctrl["players"]),
                              int(treat[column]), int(treat["players"]), alpha=alpha)
        st.write(f"Bootstrap interval: {pp(b['ci_low'])} to {pp(b['ci_high'])}. "
                 "It should be close to the interval above.")

    st.subheader("Engagement (game rounds)")
    w = ab.welch_from_summary(
        float(ctrl["trim_mean_rounds"]), float(ctrl["trim_std_rounds"]),
        int(ctrl["trim_n"]), float(treat["trim_mean_rounds"]),
        float(treat["trim_std_rounds"]), int(treat["trim_n"]), alpha)
    st.write(f"After removing the top 0.1% of players in each group, the difference "
             f"in mean rounds is {w['diff']:+.2f} (interval {w['ci_low']:+.2f} to "
             f"{w['ci_high']:+.2f}, p = {w['p_value']:.4f}). Median rounds: "
             f"{ctrl['median_rounds']:.0f} (gate 30) vs {treat['median_rounds']:.0f} "
             "(gate 40).")

# --------------------------------------------------------- Impact and power
with tab_impact:
    st.subheader("What could this mean for the business? (a scenario, not data)")
    players = st.number_input("New players per month", min_value=1000,
                              value=100000, step=5000)
    value = st.number_input("Value of one player retained at day 7 (any currency unit)",
                            min_value=0.0, value=1.0, step=0.1)
    day7 = retention_test("retained_day7")
    s = ab.impact_scenario(day7.diff, day7.ci_low, day7.ci_high, players, value)

    m1, m2, m3 = st.columns(3)
    m1.metric("Extra retained players per month (low)", f"{s['low_players']:+,.0f}")
    m2.metric("Expected", f"{s['expected_players']:+,.0f}")
    m3.metric("High", f"{s['high_players']:+,.0f}")
    st.write(f"In value terms: {s['low_value']:+,.0f} to {s['high_value']:+,.0f} "
             f"per month (expected {s['expected_value']:+,.0f}).")
    st.caption("These numbers multiply the measured difference by values you choose. "
               "They show the size of the decision, not a forecast.")

    st.subheader("Could this test detect an effect that matters?")
    base_default = min(max(round(100 * day7.p_control, 1), 5.0), 40.0)
    base = st.slider("Baseline day-7 retention (%)", 5.0, 40.0, base_default, 0.1) / 100
    target = st.slider("Effect you want to detect (percentage points)", 0.1, 3.0,
                       0.5, 0.1)
    power = st.slider("Power", 0.5, 0.95, 0.8, 0.05)

    need = ab.required_n_per_group(base, target / 100, alpha, power)
    st.metric("Players needed in each group", f"{need:,}")
    n_obs = int(min(ctrl["players"], treat["players"]))
    mde_obs = ab.minimum_detectable_effect(base, n_obs, alpha, power)
    st.write(f"With {n_obs:,} players per group, the smallest effect this test could "
             f"reliably detect is about {pp(mde_obs)}.")

# ------------------------------------------------------------------ Methods
with tab_methods:
    st.subheader("How the numbers were produced")
    st.markdown("""
- **Data:** the public Cookie Cats mobile-game A/B test (players, version, game
  rounds in the first 14 days, and whether the player returned on day 1 and day 7).
- **Primary metric:** day-7 retention, chosen before looking at results.
- **Test:** two-proportion z-test, with a confidence interval for the difference.
  A bootstrap gives a cross-check.
- **Secondary metrics:** day-1 retention and game rounds, treated with caution
  because several tests raise the chance of a false positive.
- **Decision rule:** written in advance. Smallest meaningful change: 0.5 percentage
  points.
- **Sample ratio check:** confirms the groups are the size the 50/50 split predicts.
""")
    st.subheader("Limits")
    st.markdown("""
- Only retention flags are available. There is no revenue or purchase data.
- Players are measured after 7 days at most, so long-term effects are unknown.
- Random assignment is assumed. The sample ratio check can reveal problems but
  cannot prove the assignment was random.
- Game rounds are not the same as levels reached.
- This is a learning project using public data.
""")
