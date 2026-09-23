"""Campaign funnel, channel efficiency, and budget-review analysis."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "marketing_campaign_performance_10000.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = PROJECT_ROOT / "figures"
MEMO_DIR = PROJECT_ROOT / "memo"


def safe_divide(numerator: pd.Series | float, denominator: pd.Series | float):
    return np.divide(
        numerator,
        denominator,
        out=np.full_like(np.asarray(numerator, dtype=float), np.nan, dtype=float),
        where=np.asarray(denominator) != 0,
    )


def main() -> None:
    for directory in (OUTPUT_DIR, FIGURE_DIR, MEMO_DIR):
        directory.mkdir(exist_ok=True)

    data = pd.read_csv(DATA_PATH)
    required = {
        "CampaignID", "StartDate", "EndDate", "Channel", "Impressions", "Clicks",
        "Leads", "Conversions", "Cost_USD", "Revenue_USD",
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
    quality = pd.DataFrame(
        {
            "Check": ["Duplicate rows", "Missing rows", "Invalid dates", "Invalid funnel", "Negative values"],
            "Count": [
                int(data.duplicated().sum()),
                int(data.isna().any(axis=1).sum()),
                int((data["EndDate"] < data["StartDate"]).sum()),
                int(invalid_funnel.sum()),
                int((data[numeric] < 0).any(axis=1).sum()),
            ],
        }
    )
    assert quality["Count"].sum() == 0
    assert data["CampaignID"].is_unique

    data["CTR"] = safe_divide(data["Clicks"], data["Impressions"])
    data["ClickToLead"] = safe_divide(data["Leads"], data["Clicks"])
    data["LeadToConversion"] = safe_divide(data["Conversions"], data["Leads"])
    data["ClickToConversion"] = safe_divide(data["Conversions"], data["Clicks"])
    data["CPC"] = safe_divide(data["Cost_USD"], data["Clicks"])
    data["CPL"] = safe_divide(data["Cost_USD"], data["Leads"])
    data["CAC"] = safe_divide(data["Cost_USD"], data["Conversions"])
    data["ROAS"] = safe_divide(data["Revenue_USD"], data["Cost_USD"])
    data["StartMonth"] = data["StartDate"].dt.to_period("M").astype(str)

    totals = data[numeric].sum()
    overall = {
        "Campaigns": len(data),
        "Impressions": int(totals["Impressions"]),
        "Clicks": int(totals["Clicks"]),
        "Leads": int(totals["Leads"]),
        "Conversions": int(totals["Conversions"]),
        "Spend": float(totals["Cost_USD"]),
        "Revenue": float(totals["Revenue_USD"]),
        "CTR": float(totals["Clicks"] / totals["Impressions"]),
        "Click to lead": float(totals["Leads"] / totals["Clicks"]),
        "Lead to conversion": float(totals["Conversions"] / totals["Leads"]),
        "CAC": float(totals["Cost_USD"] / totals["Conversions"]),
        "ROAS": float(totals["Revenue_USD"] / totals["Cost_USD"]),
    }

    channel = (
        data.groupby("Channel", as_index=False)
        .agg(
            Campaigns=("CampaignID", "size"), Impressions=("Impressions", "sum"),
            Clicks=("Clicks", "sum"), Leads=("Leads", "sum"),
            Conversions=("Conversions", "sum"), Spend=("Cost_USD", "sum"),
            Revenue=("Revenue_USD", "sum"),
        )
    )
    channel["CTR"] = channel["Clicks"] / channel["Impressions"]
    channel["Click to lead"] = channel["Leads"] / channel["Clicks"]
    channel["Lead to conversion"] = channel["Conversions"] / channel["Leads"]
    channel["CAC"] = channel["Spend"] / channel["Conversions"]
    channel["ROAS"] = channel["Revenue"] / channel["Spend"]
    channel = channel.sort_values("ROAS", ascending=False)

    roas_median = data["ROAS"].median()
    cac_median = data["CAC"].median()
    conversion_median = data["Conversions"].median()
    ctr_median = data["CTR"].median()
    click_conversion_median = data["ClickToConversion"].median()
    spend_median = data["Cost_USD"].median()

    def priority(row: pd.Series) -> str:
        if row["ROAS"] < 1 and row["Cost_USD"] >= spend_median:
            return "Reduce / pause review"
        if row["ROAS"] >= roas_median and row["CAC"] <= cac_median and row["Conversions"] >= conversion_median:
            return "Scale review"
        if row["CTR"] >= ctr_median and row["ClickToConversion"] < click_conversion_median:
            return "Landing / offer optimisation"
        return "Investigate"

    data["Priority"] = data.apply(priority, axis=1)
    priority_summary = (
        data.groupby("Priority", as_index=False)
        .agg(
            Campaigns=("CampaignID", "size"), Spend=("Cost_USD", "sum"),
            Revenue=("Revenue_USD", "sum"), Conversions=("Conversions", "sum"),
        )
    )
    priority_summary["CAC"] = priority_summary["Spend"] / priority_summary["Conversions"]
    priority_summary["ROAS"] = priority_summary["Revenue"] / priority_summary["Spend"]

    monthly = (
        data.groupby("StartMonth", as_index=False)
        .agg(Spend=("Cost_USD", "sum"), Revenue=("Revenue_USD", "sum"), Conversions=("Conversions", "sum"))
    )
    monthly["CAC"] = monthly["Spend"] / monthly["Conversions"]
    monthly["ROAS"] = monthly["Revenue"] / monthly["Spend"]

    pd.DataFrame({"Metric": overall.keys(), "Value": overall.values()}).to_csv(
        OUTPUT_DIR / "overall_metrics.csv", index=False
    )
    quality.to_csv(OUTPUT_DIR / "data_quality_summary.csv", index=False)
    channel.round(6).to_csv(OUTPUT_DIR / "channel_performance.csv", index=False)
    priority_summary.round(6).to_csv(OUTPUT_DIR / "priority_summary.csv", index=False)
    monthly.round(6).to_csv(OUTPUT_DIR / "monthly_performance.csv", index=False)
    data.to_csv(OUTPUT_DIR / "campaign_decision_table.csv", index=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    navy, teal, gold, red = "#16324F", "#2A9D8F", "#E9C46A", "#D95D5D"
    transition_labels = ["Impression → click", "Click → lead", "Lead → conversion"]
    transition_rates = [
        overall["CTR"] * 100,
        overall["Click to lead"] * 100,
        overall["Lead to conversion"] * 100,
    ]
    axes[0, 0].barh(transition_labels, transition_rates, color=navy)
    axes[0, 0].set_title("Weighted funnel transition rates")
    axes[0, 0].set_xlabel("Conversion from previous stage (%)")
    for index, value in enumerate(transition_rates):
        axes[0, 0].text(value + 0.3, index, f"{value:.1f}%", va="center")

    axes[0, 1].bar(channel["Channel"], channel["ROAS"], color=teal)
    axes[0, 1].axhline(1, color=red, linestyle="--", linewidth=1)
    axes[0, 1].set_title("Weighted ROAS by channel")
    axes[0, 1].tick_params(axis="x", rotation=20)

    axes[1, 0].bar(channel["Channel"], channel["CAC"], color=gold)
    axes[1, 0].set_title("Weighted CAC by channel")
    axes[1, 0].tick_params(axis="x", rotation=20)

    plot_priority = priority_summary.sort_values("Campaigns")
    axes[1, 1].barh(plot_priority["Priority"], plot_priority["Campaigns"], color=teal)
    axes[1, 1].set_title("Campaign action queue")
    fig.suptitle(
        f"Campaign & Growth Decision View  |  CTR {overall['CTR']:.2%}  |  "
        f"CAC ${overall['CAC']:.2f}  |  ROAS {overall['ROAS']:.2f}x",
        fontsize=15, fontweight="bold", color=navy,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(FIGURE_DIR / "campaign_decision_dashboard.png", dpi=180)
    plt.close(fig)

    best = channel.iloc[0]
    worst = channel.iloc[-1]
    memo = f"""# Campaign & Growth Performance — Decision Memo

## Decision

Use channel metrics for diagnosis and campaign-level rules for review—not automatic budget reallocation. Review high-ROAS, low-CAC campaigns for scalable capacity; fix landing/offer friction where CTR is strong but downstream conversion is weak; and require a holdout test before claiming incrementality.

## Evidence

- {len(data):,} campaigns generated {overall['Impressions']:,.0f} impressions, {overall['Conversions']:,.0f} conversions, **{overall['CTR']:.2%} CTR**, **${overall['CAC']:.2f} CAC**, and **{overall['ROAS']:.2f}x ROAS**.
- **{best['Channel']}** has the strongest weighted observed ROAS at **{best['ROAS']:.2f}x**; **{worst['Channel']}** has the weakest at **{worst['ROAS']:.2f}x**.
- Channel rates are calculated from summed numerators and denominators, not by averaging row-level rates.

## Limits and next test

The data are deterministic synthetic records. ROAS is observed return, not causal incrementality. The action queue uses transparent median-based triage rules and should start a human review, not execute spend changes automatically. The next step is a geo or audience holdout test using contribution margin and customer quality guardrails.
"""
    (MEMO_DIR / "business_memo.md").write_text(memo, encoding="utf-8")

    print("PASS — campaign analysis completed")
    print(f"Campaigns: {len(data):,}")
    print(f"CTR: {overall['CTR']:.2%}")
    print(f"CAC: ${overall['CAC']:.2f}")
    print(f"ROAS: {overall['ROAS']:.2f}x")


if __name__ == "__main__":
    main()
