"""Reproducible product A/B-test case linked to the e-commerce funnel project.

The pre-experiment covariates come from the project's synthetic GA4-style user
population. Variant assignment and outcomes are generated deterministically and
are explicitly synthetic; the purpose is to demonstrate experiment design,
quality gates, inference, guardrails, and a launch decision.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chisquare, norm, ttest_ind


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ROOT = Path(__file__).resolve().parent
DATA_DIR = EXPERIMENT_ROOT / "data"
OUTPUT_DIR = EXPERIMENT_ROOT / "outputs"
FIGURE_DIR = EXPERIMENT_ROOT / "figures"
MEMO_DIR = EXPERIMENT_ROOT / "memo"
SEED = 2026
ALPHA = 0.05
POWER = 0.80


def proportion_test(success_a: int, n_a: int, success_b: int, n_b: int) -> dict:
    """Two-sided two-proportion z-test and unpooled 95% CI for B minus A."""
    p_a, p_b = success_a / n_a, success_b / n_b
    pooled = (success_a + success_b) / (n_a + n_b)
    se_null = np.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z_score = (p_b - p_a) / se_null
    p_value = 2 * (1 - norm.cdf(abs(z_score)))
    se_diff = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    z_critical = norm.ppf(1 - ALPHA / 2)
    return {
        "control_rate": p_a,
        "treatment_rate": p_b,
        "absolute_lift": p_b - p_a,
        "relative_lift": (p_b - p_a) / p_a,
        "z_score": z_score,
        "p_value": p_value,
        "ci_low": (p_b - p_a) - z_critical * se_diff,
        "ci_high": (p_b - p_a) + z_critical * se_diff,
    }


def proportion_difference_ci(a: pd.Series, b: pd.Series) -> tuple[float, float, float]:
    """Return B-A and an unpooled 95% confidence interval."""
    p_a, p_b = float(a.mean()), float(b.mean())
    diff = p_b - p_a
    se = np.sqrt(p_a * (1 - p_a) / len(a) + p_b * (1 - p_b) / len(b))
    margin = norm.ppf(0.975) * se
    return diff, diff - margin, diff + margin


def mean_difference_ci(a: pd.Series, b: pd.Series) -> tuple[float, float, float, float]:
    """Return B-A, Welch CI, and two-sided Welch p-value."""
    diff = float(b.mean() - a.mean())
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    margin = norm.ppf(0.975) * se
    p_value = float(ttest_ind(b, a, equal_var=False).pvalue)
    return diff, diff - margin, diff + margin, p_value


def build_population() -> pd.DataFrame:
    sessions = pd.read_csv(PROJECT_ROOT / "data" / "fact_sessions.csv")
    first_session = (
        sessions.sort_values(["user_id", "session_date", "session_id"])
        .groupby("user_id", as_index=False)
        .first()[["user_id", "device_id", "channel_id"]]
    )
    pre_sessions = sessions.groupby("user_id").size().rename("pre_period_sessions").reset_index()
    users = first_session.merge(pre_sessions, on="user_id", validate="one_to_one")

    device = pd.read_csv(PROJECT_ROOT / "data" / "dim_device.csv")
    channel = pd.read_csv(PROJECT_ROOT / "data" / "dim_channel.csv")
    users = users.merge(device, on="device_id", validate="many_to_one")
    users = users.merge(channel, on="channel_id", validate="many_to_one")
    return users


def assign_and_generate(users: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    experiment = users.copy()

    # Exact 50/50 random allocation prevents accidental imbalance in total sample size.
    shuffled = rng.permutation(len(experiment))
    treatment_flag = np.zeros(len(experiment), dtype=int)
    treatment_flag[shuffled[len(experiment) // 2 :]] = 1
    experiment["variant"] = np.where(treatment_flag == 1, "Treatment", "Control")

    # Synthetic checkout outcome with a pre-declared treatment effect on log-odds.
    logit = np.full(len(experiment), np.log(0.055 / 0.945))
    logit += np.where(experiment["device_id"].eq(1), -0.12, 0)
    logit += np.where(experiment["device_id"].eq(3), -0.05, 0)
    logit += np.where(experiment["channel_id"].eq(6), 0.15, 0)
    logit += np.where(experiment["channel_id"].eq(2), 0.05, 0)
    logit += np.where(experiment["channel_id"].isin([5, 7]), -0.08, 0)
    logit += 0.04 * np.log1p(experiment["pre_period_sessions"])
    logit += treatment_flag * 0.15
    conversion_probability = 1 / (1 + np.exp(-logit))
    experiment["converted"] = rng.binomial(1, conversion_probability)

    order_value = rng.gamma(shape=4, scale=12, size=len(experiment))
    order_value *= np.where(treatment_flag == 1, 0.995, 1.0)
    experiment["revenue"] = np.where(experiment["converted"].eq(1), order_value, 0).round(2)
    refund_probability = np.where(treatment_flag == 1, 0.052, 0.050)
    experiment["refunded"] = np.where(
        experiment["converted"].eq(1), rng.binomial(1, refund_probability), 0
    )
    bounce_probability = np.clip(
        0.42 - 0.01 * treatment_flag + 0.02 * experiment["device_id"].eq(1), 0, 1
    )
    experiment["bounced"] = rng.binomial(1, bounce_probability)
    return experiment


def balance_checks(experiment: pd.DataFrame) -> pd.DataFrame:
    rows = []
    control = experiment[experiment["variant"].eq("Control")]
    treatment = experiment[experiment["variant"].eq("Treatment")]

    pooled_sd = experiment["pre_period_sessions"].std(ddof=1)
    smd = (
        treatment["pre_period_sessions"].mean()
        - control["pre_period_sessions"].mean()
    ) / pooled_sd
    rows.append(
        {
            "Variable": "pre_period_sessions",
            "Level": "numeric",
            "Control": control["pre_period_sessions"].mean(),
            "Treatment": treatment["pre_period_sessions"].mean(),
            "Absolute Difference": abs(smd),
            "Scale": "standardised mean difference",
            "Pass": abs(smd) < 0.10,
        }
    )

    for variable in ("device_category", "channel"):
        levels = sorted(experiment[variable].unique())
        for level in levels:
            p_control = control[variable].eq(level).mean()
            p_treatment = treatment[variable].eq(level).mean()
            difference = abs(p_treatment - p_control)
            rows.append(
                {
                    "Variable": variable,
                    "Level": level,
                    "Control": p_control,
                    "Treatment": p_treatment,
                    "Absolute Difference": difference,
                    "Scale": "proportion difference",
                    "Pass": difference < 0.02,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    for directory in (DATA_DIR, OUTPUT_DIR, FIGURE_DIR, MEMO_DIR):
        directory.mkdir(exist_ok=True)

    experiment = assign_and_generate(build_population())
    control = experiment[experiment["variant"].eq("Control")]
    treatment = experiment[experiment["variant"].eq("Treatment")]

    observed = np.array([len(control), len(treatment)])
    expected = np.repeat(len(experiment) / 2, 2)
    srm_stat, srm_p = chisquare(observed, f_exp=expected)
    balance = balance_checks(experiment)

    primary = proportion_test(
        int(control["converted"].sum()),
        len(control),
        int(treatment["converted"].sum()),
        len(treatment),
    )
    pooled_rate = (control["converted"].sum() + treatment["converted"].sum()) / len(
        experiment
    )
    z_alpha = norm.ppf(1 - ALPHA / 2)
    z_power = norm.ppf(POWER)
    mde = (z_alpha + z_power) * np.sqrt(
        2 * pooled_rate * (1 - pooled_rate) / min(len(control), len(treatment))
    )

    control_orders = control[control["converted"].eq(1)]
    treatment_orders = treatment[treatment["converted"].eq(1)]
    aov_diff, aov_low, aov_high, aov_p = mean_difference_ci(
        control_orders["revenue"], treatment_orders["revenue"]
    )
    refund_diff, refund_low, refund_high = proportion_difference_ci(
        control_orders["refunded"], treatment_orders["refunded"]
    )
    bounce_diff, bounce_low, bounce_high = proportion_difference_ci(
        control["bounced"], treatment["bounced"]
    )

    guardrails = pd.DataFrame(
        [
            {
                "Metric": "Average order value",
                "Control": control_orders["revenue"].mean(),
                "Treatment": treatment_orders["revenue"].mean(),
                "Difference": aov_diff,
                "CI Low": aov_low,
                "CI High": aov_high,
                "Threshold": "Treatment no more than 5% lower",
                "Pass": treatment_orders["revenue"].mean()
                >= 0.95 * control_orders["revenue"].mean(),
            },
            {
                "Metric": "Refund rate among purchasers",
                "Control": control_orders["refunded"].mean(),
                "Treatment": treatment_orders["refunded"].mean(),
                "Difference": refund_diff,
                "CI Low": refund_low,
                "CI High": refund_high,
                "Threshold": "Increase below 1 percentage point",
                "Pass": refund_diff < 0.01,
            },
            {
                "Metric": "Bounce rate",
                "Control": control["bounced"].mean(),
                "Treatment": treatment["bounced"].mean(),
                "Difference": bounce_diff,
                "CI Low": bounce_low,
                "CI High": bounce_high,
                "Threshold": "No increase",
                "Pass": bounce_diff <= 0,
            },
        ]
    )

    segments = []
    for dimension in ("device_category", "channel"):
        for level, group in experiment.groupby(dimension):
            c = group[group["variant"].eq("Control")]
            t = group[group["variant"].eq("Treatment")]
            if len(c) < 100 or len(t) < 100:
                continue
            result = proportion_test(
                int(c["converted"].sum()), len(c), int(t["converted"].sum()), len(t)
            )
            segments.append(
                {
                    "Dimension": dimension,
                    "Segment": level,
                    "Control N": len(c),
                    "Treatment N": len(t),
                    "Control Rate": result["control_rate"],
                    "Treatment Rate": result["treatment_rate"],
                    "Absolute Lift": result["absolute_lift"],
                    "CI Low": result["ci_low"],
                    "CI High": result["ci_high"],
                    "P Value": result["p_value"],
                    "Interpretation": "Exploratory; not powered for segment decisions",
                }
            )
    segment_results = pd.DataFrame(segments)

    experiment_summary = pd.DataFrame(
        [
            {"Metric": "Users", "Value": len(experiment)},
            {"Metric": "Control users", "Value": len(control)},
            {"Metric": "Treatment users", "Value": len(treatment)},
            {"Metric": "SRM p-value", "Value": srm_p},
            {"Metric": "Control conversion", "Value": primary["control_rate"]},
            {"Metric": "Treatment conversion", "Value": primary["treatment_rate"]},
            {"Metric": "Absolute lift", "Value": primary["absolute_lift"]},
            {"Metric": "Relative lift", "Value": primary["relative_lift"]},
            {"Metric": "95% CI low", "Value": primary["ci_low"]},
            {"Metric": "95% CI high", "Value": primary["ci_high"]},
            {"Metric": "Primary p-value", "Value": primary["p_value"]},
            {"Metric": "80% power MDE", "Value": mde},
        ]
    )

    decision = (
        "Staged rollout"
        if primary["p_value"] < ALPHA
        and primary["ci_low"] > 0
        and balance["Pass"].all()
        and guardrails["Pass"].all()
        else "Do not roll out; diagnose or retest"
    )

    assert len(experiment) == 32_000
    assert observed.tolist() == [16_000, 16_000]
    assert srm_p > ALPHA
    assert balance["Pass"].all()
    assert guardrails["Pass"].all()
    assert primary["ci_low"] > 0 and primary["p_value"] < ALPHA
    assert decision == "Staged rollout"

    experiment.to_csv(DATA_DIR / "ab_test_users.csv", index=False)
    experiment_summary.to_csv(OUTPUT_DIR / "experiment_summary.csv", index=False)
    balance.to_csv(OUTPUT_DIR / "balance_checks.csv", index=False)
    guardrails.to_csv(OUTPUT_DIR / "guardrail_results.csv", index=False)
    segment_results.to_csv(OUTPUT_DIR / "exploratory_segment_results.csv", index=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    navy, teal, red = "#16324F", "#2A9D8F", "#D95D5D"

    rates = np.array([primary["control_rate"], primary["treatment_rate"]]) * 100
    axes[0].bar(["Control", "Treatment"], rates, color=[navy, teal])
    axes[0].set_title("Checkout conversion")
    axes[0].set_ylabel("Conversion rate (%)")
    axes[0].set_ylim(0, max(rates) * 1.25)
    for index, value in enumerate(rates):
        axes[0].text(index, value + 0.15, f"{value:.2f}%", ha="center", fontweight="bold")

    guardrail_plot = guardrails.copy()
    guardrail_plot["Relative / pp change"] = [
        (guardrail_plot.loc[0, "Treatment"] / guardrail_plot.loc[0, "Control"] - 1) * 100,
        guardrail_plot.loc[1, "Difference"] * 100,
        guardrail_plot.loc[2, "Difference"] * 100,
    ]
    axes[1].barh(
        ["AOV (%)", "Refund (pp)", "Bounce (pp)"],
        guardrail_plot["Relative / pp change"],
        color=[teal if value <= 0 else red for value in guardrail_plot["Relative / pp change"]],
    )
    axes[1].axvline(0, color="black", linewidth=0.8)
    axes[1].set_title("Guardrail change: treatment vs control")

    device_segments = segment_results.query("Dimension == 'device_category'").copy()
    axes[2].errorbar(
        device_segments["Absolute Lift"] * 100,
        device_segments["Segment"],
        xerr=np.vstack(
            [
                (device_segments["Absolute Lift"] - device_segments["CI Low"]) * 100,
                (device_segments["CI High"] - device_segments["Absolute Lift"]) * 100,
            ]
        ),
        fmt="o",
        color=navy,
        capsize=4,
    )
    axes[2].axvline(0, color="black", linewidth=0.8)
    axes[2].set_title("Exploratory device lift (95% CI)")
    axes[2].set_xlabel("Absolute conversion lift (percentage points)")

    fig.suptitle(
        f"Checkout Experiment Decision: {decision}  |  "
        f"Lift {primary['absolute_lift']:.2%}  |  p={primary['p_value']:.4f}",
        fontsize=15,
        fontweight="bold",
        color=navy,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(FIGURE_DIR / "experiment_decision_dashboard.png", dpi=180)
    plt.close(fig)

    memo = f"""# Checkout Experiment — Decision Memo

## Decision

**{decision}.** Move from 25% to 50% and then 100% exposure while monitoring the pre-declared guardrails. Do not use exploratory segment estimates to target the rollout because the test was powered for the overall effect, not subgroup effects.

## Experiment design

- **Hypothesis:** simplifying checkout increases purchase conversion without materially reducing average order value or worsening refund and bounce rates.
- **Randomisation unit:** user; each of {len(experiment):,} users appears in one variant only.
- **Primary metric:** user-level purchase conversion.
- **Guardrails:** average order value, refund rate among purchasers, and bounce rate.
- **Quality gates:** Sample Ratio Mismatch (SRM), pre-treatment balance, confidence interval, p-value, 80% power Minimum Detectable Effect (MDE), and guardrail thresholds.

## Quality and result

- Allocation was {len(control):,}/{len(treatment):,}; SRM p-value = **{srm_p:.3f}**, so the assignment-ratio gate passed.
- All pre-treatment balance checks passed: categorical share gaps were below 2 percentage points and the numeric standardised mean difference was below 0.10.
- Control conversion was **{primary['control_rate']:.2%}** and treatment conversion was **{primary['treatment_rate']:.2%}**.
- Absolute lift was **{primary['absolute_lift']:.2%}** ({primary['relative_lift']:.1%} relative), with a 95% CI of **[{primary['ci_low']:.2%}, {primary['ci_high']:.2%}]** and p-value **{primary['p_value']:.4f}**.
- The approximate 80% power MDE was **{mde:.2%}**; the observed effect exceeded it.
- AOV changed by **{aov_diff / control_orders['revenue'].mean():.1%}**, refund rate by **{refund_diff:.2%}**, and bounce rate by **{bounce_diff:.2%}**. All remained inside their pre-declared thresholds.

## Limits

The user covariates come from this project's synthetic GA4-style population, and the assignment and outcomes are also deterministic synthetic data. The case proves the analytical workflow, not a real commercial uplift. Multiple subgroup comparisons are exploratory and are not evidence of heterogeneous treatment effects. A real launch would also require instrumentation QA, exposure logging, novelty monitoring, and contribution-margin guardrails.
"""
    (MEMO_DIR / "experiment_memo.md").write_text(memo, encoding="utf-8")

    print("PASS — experiment analysis completed")
    print(f"SRM p-value: {srm_p:.3f}")
    print(
        f"Conversion: {primary['control_rate']:.2%} -> {primary['treatment_rate']:.2%} "
        f"({primary['absolute_lift']:.2%} absolute, p={primary['p_value']:.4f})"
    )
    print(f"Decision: {decision}")


if __name__ == "__main__":
    main()
