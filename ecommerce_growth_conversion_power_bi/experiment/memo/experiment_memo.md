# Checkout Experiment — Decision Memo

## Decision

**Staged rollout.** Move from 25% to 50% and then 100% exposure while monitoring the pre-declared guardrails. Do not use exploratory segment estimates to target the rollout because the test was powered for the overall effect, not subgroup effects.

## Experiment design

- **Hypothesis:** simplifying checkout increases purchase conversion without materially reducing average order value or worsening refund and bounce rates.
- **Randomisation unit:** user; each of 32,000 users appears in one variant only.
- **Primary metric:** user-level purchase conversion.
- **Guardrails:** average order value, refund rate among purchasers, and bounce rate.
- **Quality gates:** Sample Ratio Mismatch (SRM), pre-treatment balance, confidence interval, p-value, 80% power Minimum Detectable Effect (MDE), and guardrail thresholds.

## Quality and result

- Allocation was 16,000/16,000; SRM p-value = **1.000**, so the assignment-ratio gate passed.
- All pre-treatment balance checks passed: categorical share gaps were below 2 percentage points and the numeric standardised mean difference was below 0.10.
- Control conversion was **5.28%** and treatment conversion was **6.06%**.
- Absolute lift was **0.78%** (14.7% relative), with a 95% CI of **[0.27%, 1.28%]** and p-value **0.0027**.
- The approximate 80% power MDE was **0.72%**; the observed effect exceeded it.
- AOV changed by **-1.5%**, refund rate by **0.31%**, and bounce rate by **-0.68%**. All remained inside their pre-declared thresholds.

## Limits

The user covariates come from this project's synthetic GA4-style population, and the assignment and outcomes are also deterministic synthetic data. The case proves the analytical workflow, not a real commercial uplift. Multiple subgroup comparisons are exploratory and are not evidence of heterogeneous treatment effects. A real launch would also require instrumentation QA, exposure logging, novelty monitoring, and contribution-margin guardrails.
