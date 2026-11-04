"""Campaign funnel, channel performance, and prioritisation analysis.

Canonical source: the bundled 10,000-row Marketing Campaign Performance CSV used
by marketing_campaign_funnel_analysis.ipynb.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "marketing_campaign_performance_10000.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = PROJECT_ROOT / "figures"
MEMO_DIR = PROJECT_ROOT / "memo"


def safe_divide(numerator, denominator):
    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)
    return np.divide(
        numerator,
        denominator,
        out=np.full_like(numerator, np.nan, dtype=float),
        where=denominator != 0,
    )


def main() -> None:
    for directory in (OUTPUT_DIR, FIGURE_DIR, MEMO_DIR):
        directory.mkdir(exist_ok=True)

    data = pd.read_csv(DATA_PATH)
    required = {
        "CampaignID", "StartDate", "EndDate", "Channel", "Impressions", "Clicks",
        "Leads", "Conversions", "Cost_USD", "Revenue_USD", "ROI",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data["StartDate"] = pd.to_datetime(data["StartDate"], errors="raise")
    data["EndDate"] = pd.to_datetime(data["EndDate"], errors="raise")
    numeric = ["Impressions", "Clicks", "Leads", "Conversions", "Cost_USD", "Revenue_USD"]
    invalid_funnel = (
        (data["Impressions"] < data["Clicks"])
        | (data["Clicks"] < data["Leads"])
        | (data["Leads"] < data["Conversions"])
    )
    quality = pd.DataFrame({
        "Check": [
            "Duplicate rows", "Duplicate campaign IDs", "Missing rows",
            "Invalid dates", "Invalid funnel", "Negative values",
        ],
        "Count": [
            int(data.duplicated().sum()),
            int(data["CampaignID"].duplicated().sum()),
            int(data.isna().any(axis=1).sum()),
            int((data["EndDate"] < data["StartDate"]).sum()),
            int(invalid_funnel.sum()),
            int((data[numeric] < 0).any(axis=1).sum()),
        ],
    })
    if quality["Count"].sum() != 0:
        raise ValueError(f"Data-quality checks failed:\n{quality}")

    data["CTR"] = safe_divide(data["Clicks"], data["Impressions"])
    data["LeadRate"] = safe_divide(data["Leads"], data["Clicks"])
    data["ConversionRate"] = safe_divide(data["Conversions"], data["Clicks"])
    data["LeadToConversionRate"] = safe_divide(data["Conversions"], data["Leads"])
    data["CPC"] = safe_divide(data["Cost_USD"], data["Clicks"])
    data["CostPerLead"] = safe_divide(data["Cost_USD"], data["Leads"])
    data["CAC"] = safe_divide(data["Cost_USD"], data["Conversions"])
    data["ROAS"] = safe_divide(data["Revenue_USD"], data["Cost_USD"])
    data["StartMonth"] = data["StartDate"].dt.to_period("M").astype(str)

    kpis = ["CTR", "LeadRate", "ConversionRate", "LeadToConversionRate", "CPC", "CostPerLead", "CAC", "ROAS"]
    if data[kpis].isna().any().any() or np.isinf(data[kpis].to_numpy(dtype=float)).any():
        raise ValueError("KPI quality check failed: missing or infinite KPI values detected")

    totals = data[numeric].sum()
    overall = {
        "Campaigns": int(len(data)),
        "Impressions": int(totals["Impressions"]),
        "Clicks": int(totals["Clicks"]),
        "Leads": int(totals["Leads"]),
        "Conversions": int(totals["Conversions"]),
        "Spend": float(totals["Cost_USD"]),
        "Revenue": float(totals["Revenue_USD"]),
        "CTR": float(totals["Clicks"] / totals["Impressions"]),
        "Click to lead": float(totals["Leads"] / totals["Clicks"]),
        "Lead to conversion": float(totals["Conversions"] / totals["Leads"]),
        "Click to conversion": float(totals["Conversions"] / totals["Clicks"]),
        "CAC": float(totals["Cost_USD"] / totals["Conversions"]),
        "ROAS": float(totals["Revenue_USD"] / totals["Cost_USD"]),
    }

    channel = data.groupby("Channel", as_index=False).agg(
        Campaigns=("CampaignID", "size"),
        Impressions=("Impressions", "sum"),
        Clicks=("Clicks", "sum"),
        Leads=("Leads", "sum"),
        Conversions=("Conversions", "sum"),
        Spend=("Cost_USD", "sum"),
        Revenue=("Revenue_USD", "sum"),
    )
    channel["CTR"] = channel["Clicks"] / channel["Impressions"]
    channel["Click to lead"] = channel["Leads"] / channel["Clicks"]
    channel["Lead to conversion"] = channel["Conversions"] / channel["Leads"]
    channel["Conversion rate"] = channel["Conversions"] / channel["Clicks"]
    channel["CAC"] = channel["Spend"] / channel["Conversions"]
    channel["ROAS"] = channel["Revenue"] / channel["Spend"]
    channel = channel.sort_values("ROAS", ascending=False)

    # Same transparent median rules used in the canonical notebook.
    median_roas = data["ROAS"].median()
    median_cac = data["CAC"].median()
    median_conversions = data["Conversions"].median()
    median_ctr = data["CTR"].median()
    median_conversion_rate = data["ConversionRate"].median()

    def assign_priority(row: pd.Series) -> str:
        if row["ROAS"] >= median_roas and row["CAC"] <= median_cac and row["Conversions"] >= median_conversions:
            return "Scale Review"
        if row["ROAS"] < median_roas and row["CAC"] > median_cac:
            return "Reduce / Pause Review"
        if row["CTR"] >= median_ctr and row["ConversionRate"] < median_conversion_rate:
            return "Optimize"
        return "Investigate"

    data["PriorityGroup"] = data.apply(assign_priority, axis=1)
    priority_summary = data.groupby("PriorityGroup", as_index=False).agg(
        Campaigns=("CampaignID", "size"),
        TotalCost=("Cost_USD", "sum"),
        TotalRevenue=("Revenue_USD", "sum"),
        TotalConversions=("Conversions", "sum"),
        AvgCTR=("CTR", "mean"),
        AvgConversionRate=("ConversionRate", "mean"),
        AvgCAC=("CAC", "mean"),
        AvgROAS=("ROAS", "mean"),
    )

    monthly = data.groupby("StartMonth", as_index=False).agg(
        Spend=("Cost_USD", "sum"),
        Revenue=("Revenue_USD", "sum"),
        Conversions=("Conversions", "sum"),
        Impressions=("Impressions", "sum"),
        Clicks=("Clicks", "sum"),
    )
    monthly["CTR"] = monthly["Clicks"] / monthly["Impressions"]
    monthly["CAC"] = monthly["Spend"] / monthly["Conversions"]
    monthly["ROAS"] = monthly["Revenue"] / monthly["Spend"]

    pd.DataFrame({"Metric": overall.keys(), "Value": overall.values()}).to_csv(OUTPUT_DIR / "overall_metrics.csv", index=False)
    quality.to_csv(OUTPUT_DIR / "data_quality_summary.csv", index=False)
    channel.round(6).to_csv(OUTPUT_DIR / "channel_performance.csv", index=False)
    priority_summary.round(6).to_csv(OUTPUT_DIR / "priority_summary.csv", index=False)
    monthly.round(6).to_csv(OUTPUT_DIR / "monthly_performance.csv", index=False)
    data.round(8).to_csv(OUTPUT_DIR / "campaign_decision_table.csv", index=False)

    # Decision dashboard
    plt.close("all")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    transition_labels = ["Impression -> click", "Click -> lead", "Lead -> conversion"]
    transition_rates = [overall["CTR"] * 100, overall["Click to lead"] * 100, overall["Lead to conversion"] * 100]
    axes[0, 0].barh(transition_labels, transition_rates)
    axes[0, 0].set_title("Overall Funnel Conversion")
    axes[0, 0].set_xlabel("Conversion from previous stage (%)")

    channel_plot = channel.sort_values("ROAS")
    axes[0, 1].barh(channel_plot["Channel"], channel_plot["ROAS"])
    axes[0, 1].set_title("Observed ROAS by Channel")
    axes[0, 1].set_xlabel("Revenue / Spend")

    channel_cac = channel.sort_values("CAC", ascending=False)
    axes[1, 0].barh(channel_cac["Channel"], channel_cac["CAC"])
    axes[1, 0].set_title("CAC by Channel")
    axes[1, 0].set_xlabel("Spend / Conversion")

    counts = data["PriorityGroup"].value_counts().reindex([
        "Scale Review", "Optimize", "Investigate", "Reduce / Pause Review"
    ]).fillna(0)
    axes[1, 1].barh(counts.index, counts.values)
    axes[1, 1].set_title("Campaign Review Queue")
    axes[1, 1].set_xlabel("Campaigns")

    fig.suptitle("Campaign & Growth Performance — Decision Dashboard", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIGURE_DIR / "campaign_decision_dashboard.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    best_roas = channel.sort_values("ROAS", ascending=False).iloc[0]
    best_cac = channel.sort_values("CAC", ascending=True).iloc[0]
    memo = f"""# Campaign & Growth Performance — Decision Memo

## Decision question

Where does the marketing funnel lose efficiency, and which campaigns deserve scale, optimisation, investigation, or reduce/pause review?

## Headline evidence

- The full dataset contains **{len(data):,} campaigns**.
- Weighted CTR is **{overall['CTR']:.2%}**.
- Click-to-lead conversion is **{overall['Click to lead']:.2%}**.
- Lead-to-conversion is **{overall['Lead to conversion']:.2%}**.
- Observed CAC is **${overall['CAC']:.2f}**.
- Observed ROAS is **{overall['ROAS']:.2f}x**.
- The largest funnel loss is the impression-to-click stage.

## Channel interpretation

Channel averages are relatively close, so channel-level ranking alone is not a strong budget decision rule. **{best_roas['Channel']}** has the highest observed ROAS at **{best_roas['ROAS']:.2f}x**, while **{best_cac['Channel']}** has the lowest weighted CAC at **${best_cac['CAC']:.2f}**. Campaign-level variation is therefore more decision-useful than channel averages alone.

## Campaign review queue

The notebook's transparent median-based rules group campaigns into:

- **Scale Review** — stronger ROAS, lower CAC, and solid conversion volume.
- **Optimize** — stronger click response but weaker post-click conversion.
- **Investigate** — mixed performance that needs more context.
- **Reduce / Pause Review** — weaker ROAS combined with higher CAC.

These labels are triage rules for human review, not an automatic budget-allocation algorithm.

## Limits and next test

The source is campaign-level and does not contain user-level behaviour, creative, landing-page, audience, device, campaign objective, contribution margin, or an experimental holdout. The analysis identifies descriptive performance differences; it does not establish causal incrementality. A real budget decision should incorporate additional business context and, where feasible, controlled testing.
"""
    (MEMO_DIR / "business_memo.md").write_text(memo, encoding="utf-8")

    print("PASS — campaign analysis completed")
    print(f"Campaigns: {len(data):,}")
    print(f"CTR: {overall['CTR']:.2%}")
    print(f"Click -> Lead: {overall['Click to lead']:.2%}")
    print(f"Lead -> Conversion: {overall['Lead to conversion']:.2%}")
    print(f"CAC: ${overall['CAC']:.2f}")
    print(f"ROAS: {overall['ROAS']:.2f}x")


if __name__ == "__main__":
    main()
