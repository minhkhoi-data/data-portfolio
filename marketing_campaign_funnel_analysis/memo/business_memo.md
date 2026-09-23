# Campaign & Growth Performance — Decision Memo

## Decision

Use channel metrics for diagnosis and campaign-level rules for review—not automatic budget reallocation. Review high-ROAS, low-CAC campaigns for scalable capacity; fix landing/offer friction where CTR is strong but downstream conversion is weak; and require a holdout test before claiming incrementality.

## Evidence

- 10,000 campaigns generated 629,162,153 impressions, 1,258,028 conversions, **4.20% CTR**, **$22.52 CAC**, and **3.35x ROAS**.
- **Email** has the strongest weighted observed ROAS at **4.31x**; **Display** has the weakest at **1.49x**.
- Channel rates are calculated from summed numerators and denominators, not by averaging row-level rates.

## Limits and next test

The data are deterministic synthetic records. ROAS is observed return, not causal incrementality. The action queue uses transparent median-based triage rules and should start a human review, not execute spend changes automatically. The next step is a geo or audience holdout test using contribution margin and customer quality guardrails.
