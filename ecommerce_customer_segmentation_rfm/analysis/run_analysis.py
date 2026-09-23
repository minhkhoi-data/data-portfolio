"""Customer lifecycle, retention, and RFM analysis.

Run from any directory with:
    python ecommerce_customer_segmentation_rfm/analysis/run_analysis.py

The script uses project-relative paths, writes auditable CSV outputs and figures,
and fails loudly if core reconciliation checks do not pass.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "online_retail_II.csv.gz"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = PROJECT_ROOT / "figures"
MEMO_DIR = PROJECT_ROOT / "memo"


def assign_rfm_segment(row: pd.Series) -> str:
    """Map transparent RFM rules to business-friendly segment labels."""
    if row["R_Score"] >= 4 and row["F_Score"] >= 4 and row["M_Score"] >= 4:
        return "Champions"
    if row["R_Score"] >= 3 and row["F_Score"] >= 4:
        return "Loyal Customers"
    if row["R_Score"] >= 4 and row["F_Score"] in (2, 3):
        return "Potential Loyalists"
    if row["R_Score"] >= 4 and row["F_Score"] == 1:
        return "New Customers"
    if row["R_Score"] <= 2 and row["F_Score"] >= 3:
        return "At Risk"
    if row["R_Score"] <= 2 and row["F_Score"] <= 2:
        return "Hibernating"
    return "Needs Attention"


def lifecycle_status(row: pd.Series) -> str:
    """Classify the latest observable customer state using disclosed cut-offs."""
    if row["Orders"] == 1 and row["RecencyDays"] <= 90:
        return "New"
    if row["Orders"] >= 2 and row["RecencyDays"] <= 90:
        return "Active repeat"
    if 90 < row["RecencyDays"] <= 180:
        return "At risk"
    return "Dormant"


def crm_action(row: pd.Series, high_value_cutoff: float) -> str:
    """Prioritise actions using lifecycle, value, and observed purchase history."""
    if row["Lifecycle"] == "Active repeat" and row["Monetary"] >= high_value_cutoff:
        return "Protect high-value active"
    if row["Lifecycle"] == "At risk" and row["Monetary"] >= high_value_cutoff:
        return "Win back high-value"
    if row["Lifecycle"] == "New":
        return "Drive second purchase"
    if row["Lifecycle"] == "Active repeat":
        return "Develop loyalty"
    if row["Lifecycle"] == "At risk":
        return "Test win-back"
    return "Low-cost reactivation"


def save_dashboard(
    lifecycle_summary: pd.DataFrame,
    retention_kpis: pd.DataFrame,
    priority_summary: pd.DataFrame,
    repeat_rate: float,
    repeat_90_rate: float,
) -> None:
    """Create a compact decision dashboard from the validated outputs."""
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    navy, teal, gold, red = "#16324F", "#2A9D8F", "#E9C46A", "#D95D5D"

    life = lifecycle_summary.sort_values("Customers", ascending=True)
    axes[0, 0].barh(life["Lifecycle"], life["Customers"], color=teal)
    axes[0, 0].set_title("Customers by current lifecycle state")
    axes[0, 0].set_xlabel("Customers")

    axes[0, 1].bar(
        lifecycle_summary["Lifecycle"],
        lifecycle_summary["Revenue Share (%)"],
        color=[navy, red, gold, "#7A7A7A"],
    )
    axes[0, 1].set_title("Historical revenue share by lifecycle state")
    axes[0, 1].set_ylabel("Revenue share (%)")
    axes[0, 1].tick_params(axis="x", rotation=20)

    axes[1, 0].plot(
        retention_kpis["Month"],
        retention_kpis["Weighted Retention Rate"] * 100,
        marker="o",
        linewidth=2.5,
        color=navy,
    )
    axes[1, 0].set_title("Weighted cohort retention")
    axes[1, 0].set_xlabel("Months after first purchase")
    axes[1, 0].set_ylabel("Retention (%)")
    axes[1, 0].set_xticks(retention_kpis["Month"])

    top_priorities = priority_summary.sort_values("Customers", ascending=True)
    axes[1, 1].barh(top_priorities["CRM Priority"], top_priorities["Customers"], color=gold)
    axes[1, 1].set_title("CRM action queue")
    axes[1, 1].set_xlabel("Customers")

    fig.suptitle(
        f"Customer Lifecycle & Retention Decision View  |  "
        f"Repeat customers {repeat_rate:.1%}  |  90-day repeat {repeat_90_rate:.1%}",
        fontsize=15,
        fontweight="bold",
        color=navy,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(FIGURE_DIR / "customer_lifecycle_decision_dashboard.png", dpi=180)
    plt.close(fig)


def save_cohort_heatmap(retention: pd.DataFrame) -> None:
    """Save a readable heatmap for the first 12 months after acquisition."""
    display = retention.iloc[:, :13].copy()
    fig, ax = plt.subplots(figsize=(14, 10))
    image = ax.imshow(display.to_numpy() * 100, aspect="auto", cmap="Blues", vmin=0, vmax=50)
    ax.set_title("Monthly Cohort Retention (% of acquisition cohort)", fontweight="bold")
    ax.set_xlabel("Months since first purchase")
    ax.set_ylabel("Acquisition cohort")
    ax.set_xticks(range(display.shape[1]), labels=display.columns)
    ax.set_yticks(range(display.shape[0]), labels=[str(x) for x in display.index])
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Retention (%)")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "cohort_retention_heatmap.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    FIGURE_DIR.mkdir(exist_ok=True)
    MEMO_DIR.mkdir(exist_ok=True)

    raw = pd.read_csv(DATA_PATH, low_memory=False)
    required_columns = {
        "Invoice",
        "StockCode",
        "Quantity",
        "InvoiceDate",
        "Price",
        "Customer ID",
    }
    missing_columns = required_columns.difference(raw.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    quality_before = {
        "Raw rows": len(raw),
        "Missing customer IDs": int(raw["Customer ID"].isna().sum()),
        "Cancelled invoice rows": int(raw["Invoice"].astype(str).str.startswith("C").sum()),
        "Non-positive quantity rows": int((raw["Quantity"] <= 0).sum()),
        "Non-positive price rows": int((raw["Price"] <= 0).sum()),
        "Duplicate rows": int(raw.duplicated().sum()),
    }

    clean = raw.dropna(subset=["Customer ID"]).copy()
    clean["Customer ID"] = clean["Customer ID"].astype(int)
    clean = clean[~clean["Invoice"].astype(str).str.startswith("C")]
    clean = clean[(clean["Quantity"] > 0) & (clean["Price"] > 0)].drop_duplicates()
    clean["InvoiceDate"] = pd.to_datetime(clean["InvoiceDate"], errors="raise")
    clean["Revenue"] = clean["Quantity"] * clean["Price"]

    orders = (
        clean.groupby(["Customer ID", "Invoice"], as_index=False)
        .agg(OrderDate=("InvoiceDate", "min"), OrderRevenue=("Revenue", "sum"))
        .sort_values(["Customer ID", "OrderDate", "Invoice"])
    )
    snapshot_date = clean["InvoiceDate"].max() + pd.Timedelta(days=1)

    customers = (
        orders.groupby("Customer ID", as_index=False)
        .agg(
            FirstPurchase=("OrderDate", "min"),
            LastPurchase=("OrderDate", "max"),
            Orders=("Invoice", "nunique"),
            Monetary=("OrderRevenue", "sum"),
        )
    )
    customers["AverageOrderValue"] = customers["Monetary"] / customers["Orders"]
    customers["RecencyDays"] = (snapshot_date - customers["LastPurchase"]).dt.days
    customers["CustomerAgeDays"] = (snapshot_date - customers["FirstPurchase"]).dt.days
    customers["RepeatCustomer"] = customers["Orders"] >= 2

    second_purchase = (
        orders.assign(OrderNumber=orders.groupby("Customer ID").cumcount() + 1)
        .query("OrderNumber == 2")[["Customer ID", "OrderDate"]]
        .rename(columns={"OrderDate": "SecondPurchase"})
    )
    customers = customers.merge(second_purchase, on="Customer ID", how="left")
    customers["DaysToSecondPurchase"] = (
        customers["SecondPurchase"] - customers["FirstPurchase"]
    ).dt.days
    customers["EligibleFor90DayRepeat"] = customers["CustomerAgeDays"] >= 90
    customers["RepeatWithin90Days"] = (
        customers["EligibleFor90DayRepeat"]
        & customers["DaysToSecondPurchase"].le(90)
    )

    customers["R_Score"] = pd.qcut(
        customers["RecencyDays"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]
    ).astype(int)
    customers["F_Score"] = pd.qcut(
        customers["Orders"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)
    customers["M_Score"] = pd.qcut(
        customers["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)
    customers["RFM_Score"] = customers[["R_Score", "F_Score", "M_Score"]].sum(axis=1)
    customers["RFM Segment"] = customers.apply(assign_rfm_segment, axis=1)
    customers["Lifecycle"] = customers.apply(lifecycle_status, axis=1)
    high_value_cutoff = float(customers["Monetary"].quantile(0.75))
    customers["CRM Priority"] = customers.apply(
        crm_action, axis=1, high_value_cutoff=high_value_cutoff
    )

    segment_summary = (
        customers.groupby("RFM Segment", as_index=False)
        .agg(
            Customers=("Customer ID", "size"),
            TotalRevenue=("Monetary", "sum"),
            AverageRevenue=("Monetary", "mean"),
            AverageRecencyDays=("RecencyDays", "mean"),
            AverageOrders=("Orders", "mean"),
        )
        .sort_values("TotalRevenue", ascending=False)
    )
    segment_summary["Customer Share (%)"] = (
        segment_summary["Customers"] / segment_summary["Customers"].sum() * 100
    )
    segment_summary["Revenue Share (%)"] = (
        segment_summary["TotalRevenue"] / segment_summary["TotalRevenue"].sum() * 100
    )

    lifecycle_summary = (
        customers.groupby("Lifecycle", as_index=False)
        .agg(
            Customers=("Customer ID", "size"),
            Revenue=("Monetary", "sum"),
            AverageRecencyDays=("RecencyDays", "mean"),
            AverageOrders=("Orders", "mean"),
        )
    )
    lifecycle_order = ["Active repeat", "At risk", "New", "Dormant"]
    lifecycle_summary["Lifecycle"] = pd.Categorical(
        lifecycle_summary["Lifecycle"], categories=lifecycle_order, ordered=True
    )
    lifecycle_summary = lifecycle_summary.sort_values("Lifecycle").reset_index(drop=True)
    lifecycle_summary["Customer Share (%)"] = (
        lifecycle_summary["Customers"] / lifecycle_summary["Customers"].sum() * 100
    )
    lifecycle_summary["Revenue Share (%)"] = (
        lifecycle_summary["Revenue"] / lifecycle_summary["Revenue"].sum() * 100
    )

    priority_summary = (
        customers.groupby("CRM Priority", as_index=False)
        .agg(
            Customers=("Customer ID", "size"),
            Revenue=("Monetary", "sum"),
            AverageRecencyDays=("RecencyDays", "mean"),
        )
        .sort_values("Revenue", ascending=False)
    )
    priority_summary["Revenue Share (%)"] = (
        priority_summary["Revenue"] / priority_summary["Revenue"].sum() * 100
    )

    orders["OrderMonth"] = orders["OrderDate"].dt.to_period("M")
    first_month = orders.groupby("Customer ID")["OrderMonth"].min().rename("CohortMonth")
    orders = orders.join(first_month, on="Customer ID")
    orders["CohortIndex"] = orders["OrderMonth"].astype(int) - orders["CohortMonth"].astype(int)
    cohort_counts = (
        orders.groupby(["CohortMonth", "CohortIndex"])["Customer ID"]
        .nunique()
        .unstack(fill_value=0)
        .sort_index()
    )
    cohort_retention = cohort_counts.div(cohort_counts[0], axis=0)

    # The source ends on 9 December 2011, so November 2011 is the last complete month.
    last_complete_month = clean["InvoiceDate"].max().to_period("M") - 1
    retention_rows = []
    for month in (1, 3, 6, 12):
        eligible = cohort_counts.loc[
            cohort_counts.index.astype(int) + month <= last_complete_month.ordinal
        ]
        rate = float(eligible[month].sum() / eligible[0].sum())
        retention_rows.append(
            {
                "Month": month,
                "Eligible Cohorts": len(eligible),
                "Eligible Customers": int(eligible[0].sum()),
                "Retained Customers": int(eligible[month].sum()),
                "Weighted Retention Rate": rate,
            }
        )
    retention_kpis = pd.DataFrame(retention_rows)

    repeat_rate = float(customers["RepeatCustomer"].mean())
    eligible_90 = customers["EligibleFor90DayRepeat"]
    repeat_90_rate = float(customers.loc[eligible_90, "RepeatWithin90Days"].mean())
    median_days_to_second = float(
        customers.loc[customers["RepeatCustomer"], "DaysToSecondPurchase"].median()
    )

    overview = pd.DataFrame(
        {
            "Metric": [
                "Clean rows",
                "Orders",
                "Customers",
                "Revenue",
                "Repeat customer rate",
                "90-day repeat rate",
                "Median days to second purchase",
                "Observation start",
                "Observation end",
            ],
            "Value": [
                len(clean),
                orders["Invoice"].nunique(),
                customers["Customer ID"].nunique(),
                clean["Revenue"].sum(),
                repeat_rate,
                repeat_90_rate,
                median_days_to_second,
                clean["InvoiceDate"].min().date(),
                clean["InvoiceDate"].max().date(),
            ],
        }
    )
    quality_summary = pd.DataFrame(
        {"Check": list(quality_before.keys()), "Count": list(quality_before.values())}
    )

    # Reconciliation and range gates: any failure stops publication.
    assert customers["Customer ID"].is_unique
    assert not clean[["Invoice", "Customer ID", "InvoiceDate", "Revenue"]].isna().any().any()
    assert np.isclose(customers["Monetary"].sum(), clean["Revenue"].sum())
    assert np.isclose(lifecycle_summary["Revenue"].sum(), clean["Revenue"].sum())
    assert cohort_retention.to_numpy().min() >= 0
    assert cohort_retention.to_numpy().max() <= 1
    assert 0 <= repeat_rate <= 1 and 0 <= repeat_90_rate <= 1

    overview.to_csv(OUTPUT_DIR / "business_overview.csv", index=False)
    quality_summary.to_csv(OUTPUT_DIR / "data_quality_summary.csv", index=False)
    customers.to_csv(OUTPUT_DIR / "customer_lifecycle_table.csv", index=False)
    segment_summary.round(4).to_csv(OUTPUT_DIR / "rfm_segment_summary.csv", index=False)
    lifecycle_summary.round(4).to_csv(OUTPUT_DIR / "lifecycle_summary.csv", index=False)
    priority_summary.round(4).to_csv(OUTPUT_DIR / "crm_priority_summary.csv", index=False)
    retention_kpis.round(6).to_csv(OUTPUT_DIR / "retention_kpis.csv", index=False)
    cohort_counts.rename_axis(index="CohortMonth").to_csv(OUTPUT_DIR / "cohort_counts.csv")
    cohort_retention.rename_axis(index="CohortMonth").round(6).to_csv(
        OUTPUT_DIR / "cohort_retention.csv"
    )

    save_dashboard(
        lifecycle_summary, retention_kpis, priority_summary, repeat_rate, repeat_90_rate
    )
    save_cohort_heatmap(cohort_retention)

    active = lifecycle_summary.set_index("Lifecycle").loc["Active repeat"]
    at_risk = lifecycle_summary.set_index("Lifecycle").loc["At risk"]
    m1 = retention_kpis.set_index("Month").loc[1, "Weighted Retention Rate"]
    m3 = retention_kpis.set_index("Month").loc[3, "Weighted Retention Rate"]
    memo = f"""# Customer Lifecycle & Retention — Decision Memo

## Decision

Protect high-value active customers first, run a measured win-back test for high-value at-risk customers, and use a second-purchase journey for new customers. Do not send the same offer to every inactive customer.

## Evidence

- **{repeat_rate:.1%}** of {len(customers):,} customers made at least two orders.
- Among customers observed for at least 90 days, **{repeat_90_rate:.1%}** made a second purchase within 90 days; the median time to second purchase among repeat customers was **{median_days_to_second:.0f} days**.
- Weighted cohort retention was **{m1:.1%}** in month 1 and **{m3:.1%}** in month 3. Only cohorts with a complete observation window are used in these headline rates.
- **{int(active['Customers']):,} active repeat customers generated {active['Revenue Share (%)']:.1f}% of historical revenue.**
- **{int(at_risk['Customers']):,} at-risk customers generated {at_risk['Revenue Share (%)']:.1f}% of historical revenue and form the most defensible win-back pool.**

## Recommended test plan

1. Protect high-value active customers with loyalty and early-access treatment; track repeat rate, revenue per customer, and unsubscribe rate.
2. Randomise high-value at-risk customers into holdout and win-back groups; measure incremental reactivation and margin, not raw redemption alone.
3. Trigger a second-purchase journey before day 55 for eligible new customers; measure 90-day second-purchase rate.
4. Restrict dormant low-value customers to low-cost channels unless an experiment shows positive incremental ROI.

## Limits

This is historical observational data. RFM and lifecycle rules describe customer behaviour but do not prove that a campaign will cause retention. The 90/180-day inactivity thresholds are transparent business rules, not universal constants. December 2011 is incomplete, so mature-cohort metrics exclude incomplete observation windows. Campaign impact requires a randomised holdout test.
"""
    (MEMO_DIR / "business_memo.md").write_text(memo, encoding="utf-8")

    print("PASS — customer lifecycle analysis completed")
    print(f"Customers: {len(customers):,}")
    print(f"Repeat customer rate: {repeat_rate:.2%}")
    print(f"90-day repeat rate: {repeat_90_rate:.2%}")
    print(f"Month-1 weighted retention: {m1:.2%}")
    print(f"Month-3 weighted retention: {m3:.2%}")


if __name__ == "__main__":
    main()
