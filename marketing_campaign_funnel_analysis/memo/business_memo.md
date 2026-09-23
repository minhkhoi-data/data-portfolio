# Campaign & Growth Performance — Decision Memo

## Decision question

Where does the marketing funnel lose efficiency, and which campaigns deserve scale, optimisation, investigation, or reduce/pause review?

## Headline evidence

- The full dataset contains **10,000 campaigns**.
- Weighted CTR is **5.48%**.
- Click-to-lead conversion is **30.13%**.
- Lead-to-conversion is **40.23%**.
- Observed CAC is **$2.53**.
- Observed ROAS is **2.00x**.
- The largest funnel loss is the impression-to-click stage.

## Channel interpretation

Channel averages are relatively close, so channel-level ranking alone is not a strong budget decision rule. **Search** has the highest observed ROAS at **2.01x**, while **Email** has the lowest weighted CAC at **$2.44**. Campaign-level variation is therefore more decision-useful than channel averages alone.

## Campaign review queue

The notebook's transparent median-based rules group campaigns into:

- **Scale Review** — stronger ROAS, lower CAC, and solid conversion volume.
- **Optimize** — stronger click response but weaker post-click conversion.
- **Investigate** — mixed performance that needs more context.
- **Reduce / Pause Review** — weaker ROAS combined with higher CAC.

These labels are triage rules for human review, not an automatic budget-allocation algorithm.

## Limits and next test

The source is campaign-level and does not contain user-level behaviour, creative, landing-page, audience, device, campaign objective, contribution margin, or an experimental holdout. The analysis identifies descriptive performance differences; it does not establish causal incrementality. A real budget decision should incorporate additional business context and, where feasible, controlled testing.
