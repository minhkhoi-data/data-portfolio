# Analysis Report

## Executive Summary

The CRM dataset contains **1,800 synthetic leads** covering January 2025 to August 2026.

The final workbook reports:

- **$9.78M** in won revenue
- **$13.01M** in open pipeline
- **$7.83M** in weighted pipeline
- **26.0%** closed-deal win rate
- **$27,079** average won deal
- **358** stale open opportunities older than 30 days

The analysis points to four management priorities: late-stage funnel leakage, stale-pipeline control, uneven channel efficiency, and the need to evaluate sales reps using both revenue and target attainment.

---

## 1. Funnel Performance

| Stage | Reached Stage | Conversion from Previous | Drop-off from Previous |
|---|---:|---:|---:|
| Lead Created | 1,800 | 100.0% | 0.0% |
| Qualified | 1,757 | 97.6% | 2.4% |
| Demo / Meeting | 1,481 | 84.3% | 15.7% |
| Proposal | 1,142 | 77.1% | 22.9% |
| Negotiation | 792 | 69.4% | 30.6% |
| Closed Won | 361 | 45.6% | 54.4% |

The largest proportional loss occurs between **Negotiation and Closed Won**. Only 361 of the 792 opportunities that reached Negotiation became won deals.

This makes late-stage conversion the clearest funnel issue in the workbook. Practical investigation should focus on negotiation objections, pricing approval, proposal quality, follow-up discipline, and whether weak opportunities remain active too long.

---

## 2. Channel Performance

Channel performance differs meaningfully across both volume and conversion quality.

| Channel | Leads | Win Rate | Won Revenue | Revenue / Lead |
|---|---:|---:|---:|---:|
| Paid Search | 346 | 20.9% | $1,255,405 | $3,628 |
| Organic Search | 335 | 28.7% | $1,821,606 | $5,438 |
| LinkedIn | 271 | 26.5% | $1,633,109 | $6,026 |
| Referral | 225 | 29.7% | $1,518,294 | $6,748 |
| Email | 215 | 32.0% | $1,656,502 | $7,705 |
| Webinar | 138 | 24.3% | $679,313 | $4,923 |
| Outbound | 217 | 21.0% | $921,554 | $4,247 |
| Other | 53 | 23.7% | $289,847 | $5,469 |

**Email** shows the strongest observed combination of win rate and revenue per lead.

**Paid Search** contributes the largest lead volume but has a materially lower win rate than stronger channels such as Email, Referral and Organic Search.

The management implication is not to optimise on one metric alone. Channel decisions should consider lead volume, win rate, revenue per lead, average deal size, pipeline contribution and strategic role together.

---

## 3. Sales-Rep Performance

Rep performance changes depending on whether the comparison is based on absolute revenue or target attainment.

| Rep | Won Revenue | Revenue Target | Target Attainment |
|---|---:|---:|---:|
| An Nguyen | $1,014,864 | $1,035,000 | 98.1% |
| Bao Tran | $1,296,394 | $1,232,000 | 105.2% |
| Chi Le | $1,164,807 | $1,258,000 | 92.6% |
| Duy Pham | $1,187,010 | $1,163,000 | 102.1% |
| Ha Vo | $1,007,131 | $1,057,000 | 95.3% |
| Minh Do | $1,168,309 | $1,075,000 | 108.7% |
| Quynh Vu | $1,594,527 | $1,754,000 | 90.9% |
| Tuan Bui | $1,342,588 | $1,289,000 | 104.2% |

**Quynh Vu** generates the highest absolute won revenue at approximately **$1.59M**, but reaches **90.9%** of target.

**Minh Do** has the highest target attainment at **108.7%**.

Bao Tran, Duy Pham and Tuan Bui also exceed target.

Therefore, rep performance should be interpreted across several measures rather than from revenue ranking alone. Useful context includes win rate, target attainment, pipeline coverage, average sales cycle and the quality of open opportunities.

---

## 4. Pipeline Health

The workbook identifies **358 open leads older than 30 days** and flags them as `STALE`.

These opportunities represent a pipeline-governance issue because inactive or weak opportunities can inflate headline pipeline values.

Recommended management actions are to:

- review ageing opportunities on a recurring cadence
- confirm next-step ownership
- requalify weak opportunities
- progress valid opportunities
- close opportunities that no longer represent realistic pipeline

The purpose is not simply to reduce the stale count, but to improve the credibility of the active pipeline.

---

## 5. Interpretation

The workbook demonstrates how a CRM dataset can be translated into a management view rather than treated as a collection of isolated KPIs.

The findings connect:

**lead acquisition → funnel progression → sales-rep execution → pipeline quality → realised revenue**

This makes it possible to identify where management attention is likely to have the greatest operational value.

---

## Limitations

- The dataset is synthetic and is used to demonstrate analytical workflow rather than real company performance.
- Marketing spend is not available, so CAC and ROAS are not calculated.
- Gross margin is not available, so revenue should not be interpreted as profit.
- Revenue targets are synthetic management assumptions.
- The 30-day stale threshold is analyst-defined.
- Findings are descriptive and should not be interpreted as causal relationships.
