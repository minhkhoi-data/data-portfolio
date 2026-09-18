# Analysis Report

## Executive summary

The CRM dataset contains 1,800 leads and produces $9.78M in closed-won revenue.

The overall closed-deal win rate is 26.0%. Open pipeline is $13.01M, while probability-weighted pipeline is $7.83M.

The main operational issues are:

1. a 54.4% drop-off from Negotiation to Closed Won;
2. 358 stale open opportunities older than 30 days;
3. high-volume Paid Search leads converting below stronger channels;
4. meaningful differences between absolute rep revenue and target attainment.

## Funnel

| Stage | Reached | Conversion from prior |
|---|---:|---:|
| Lead Created | 1,800 | 100.0% |
| Qualified | 1,757 | 97.6% |
| Demo / Meeting | 1,481 | 84.3% |
| Proposal | 1,142 | 77.1% |
| Negotiation | 792 | 69.4% |
| Closed Won | 361 | 45.6% |

The biggest proportional loss occurs after Negotiation.

## Channel performance

Email has the strongest observed win rate at 32.0% and about $7.7K revenue per lead.

Referral is also strong, with a 29.7% win rate.

Paid Search provides the most volume but only a 20.9% win rate.

Outbound is similarly weak on win rate at 21.0%.

The recommended interpretation is not to optimize on one metric. Volume, win rate, revenue per lead, average deal size, and strategic channel role should be considered together.

## Rep performance

Quynh Vu leads on absolute won revenue at about $1.59M, but reaches 90.9% of target.

Minh Do reaches the highest target attainment at 108.7%.

Bao Tran and Tuan Bui also exceed target.

Target attainment therefore changes the interpretation of pure revenue ranking.

## Pipeline health

358 open leads are older than 30 days.

The workbook flags them as `STALE`.

Management action should focus on requalification, next-step ownership, aging reviews, and removal of low-quality opportunities from the active pipeline.

## Limitations

- synthetic portfolio data
- no marketing spend, therefore CAC/ROAS are not calculated
- no gross margin, therefore revenue is not profit
- target values are synthetic management targets
- findings are descriptive rather than causal
