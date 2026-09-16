from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"


def load(name: str, date_columns: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv", parse_dates=date_columns or [])


def write(frame: pd.DataFrame, name: str, precision: dict[str, int] | None = None) -> None:
    cleaned = frame.copy()
    if precision:
        for column, decimals in precision.items():
            cleaned[column] = cleaned[column].round(decimals)
    cleaned.to_csv(OUTPUTS / name, index=False)


def main() -> None:
    OUTPUTS.mkdir(exist_ok=True)

    sessions = load("fact_sessions", ["session_date"])
    orders = load("fact_orders", ["order_date"])
    items = load("fact_order_items", ["order_date"])
    channels = load("dim_channel")
    devices = load("dim_device")
    products = load("dim_product")

    session_channel = sessions.groupby("channel_id", as_index=False).agg(
        sessions=("session_id", "nunique"),
        users=("user_id", "nunique"),
    )
    order_channel = orders.groupby("channel_id", as_index=False).agg(
        transactions=("order_id", "nunique"),
        revenue=("total_revenue", "sum"),
    )
    channel = (
        channels.merge(session_channel, on="channel_id")
        .merge(order_channel, on="channel_id", how="left")
        .fillna({"transactions": 0, "revenue": 0})
    )
    channel["transactions"] = channel["transactions"].astype(int)
    channel["conversion_rate"] = channel["transactions"] / channel["sessions"]
    channel["revenue_per_session"] = channel["revenue"] / channel["sessions"]
    channel["aov"] = channel["revenue"] / channel["transactions"]
    channel = channel.sort_values("revenue", ascending=False)[
        ["channel", "sessions", "users", "transactions", "conversion_rate", "revenue", "revenue_per_session", "aov"]
    ]
    write(
        channel,
        "channel_performance.csv",
        {"conversion_rate": 6, "revenue": 2, "revenue_per_session": 2, "aov": 2},
    )

    session_device = sessions.groupby("device_id", as_index=False).agg(
        sessions=("session_id", "nunique"),
        users=("user_id", "nunique"),
    )
    order_device = orders.groupby("device_id", as_index=False).agg(
        transactions=("order_id", "nunique"),
        revenue=("total_revenue", "sum"),
    )
    device = devices.merge(session_device, on="device_id").merge(order_device, on="device_id", how="left")
    device["conversion_rate"] = device["transactions"] / device["sessions"]
    device["revenue_per_session"] = device["revenue"] / device["sessions"]
    device = device.sort_values("revenue", ascending=False)[
        ["device_category", "sessions", "users", "transactions", "conversion_rate", "revenue", "revenue_per_session"]
    ]
    write(device, "device_performance.csv", {"conversion_rate": 6, "revenue": 2, "revenue_per_session": 2})

    funnel_counts = [
        ("Sessions", sessions["session_id"].nunique()),
        ("Product View Sessions", int(sessions["view_item"].sum())),
        ("Add to Cart Sessions", int(sessions["add_to_cart"].sum())),
        ("Checkout Sessions", int(sessions["begin_checkout"].sum())),
        ("Purchase Sessions", int(sessions["purchase"].sum())),
    ]
    funnel = pd.DataFrame(funnel_counts, columns=["stage", "sessions"])
    funnel["rate_from_previous"] = funnel["sessions"] / funnel["sessions"].shift(1)
    funnel.loc[0, "rate_from_previous"] = 1.0
    write(funnel, "funnel_performance.csv", {"rate_from_previous": 6})

    purchaser_orders = orders.groupby("user_id")["order_id"].nunique()
    purchasers = int(purchaser_orders.size)
    repeat_purchasers = int((purchaser_orders > 1).sum())
    kpis = pd.DataFrame(
        [
            ("Sessions", sessions["session_id"].nunique()),
            ("Users", sessions["user_id"].nunique()),
            ("Transactions", orders["order_id"].nunique()),
            ("Revenue", orders["total_revenue"].sum()),
            ("Session Conversion Rate", sessions["purchase"].sum() / sessions["session_id"].nunique()),
            ("Average Order Value", orders["total_revenue"].sum() / orders["order_id"].nunique()),
            ("Engagement Rate", sessions["engaged_session"].sum() / sessions["session_id"].nunique()),
            ("Purchasers", purchasers),
            ("Repeat Purchasers", repeat_purchasers),
            ("Repeat Purchase Rate", repeat_purchasers / purchasers),
        ],
        columns=["metric", "value"],
    )
    write(kpis, "kpi_summary.csv", {"value": 6})

    session_month = sessions.assign(year_month=sessions["session_date"].dt.strftime("%Y-%m")).groupby(
        "year_month", as_index=False
    ).agg(sessions=("session_id", "nunique"), purchase_sessions=("purchase", "sum"))
    order_month = orders.assign(year_month=orders["order_date"].dt.strftime("%Y-%m")).groupby(
        "year_month", as_index=False
    ).agg(revenue=("total_revenue", "sum"), transactions=("order_id", "nunique"))
    monthly = order_month.merge(session_month, on="year_month")
    monthly["conversion_rate"] = monthly["purchase_sessions"] / monthly["sessions"]
    monthly["aov"] = monthly["revenue"] / monthly["transactions"]
    monthly = monthly[
        ["year_month", "revenue", "transactions", "sessions", "purchase_sessions", "conversion_rate", "aov"]
    ]
    write(monthly, "monthly_performance.csv", {"revenue": 2, "conversion_rate": 6, "aov": 2})

    new_returning = sessions.assign(
        session_type=sessions["is_new_user"].map({1: "New-user session", 0: "Returning-user session"})
    ).groupby("session_type", as_index=False).agg(
        sessions=("session_id", "nunique"), purchase_sessions=("purchase", "sum")
    )
    new_returning["conversion_rate"] = new_returning["purchase_sessions"] / new_returning["sessions"]
    new_returning["sort_order"] = new_returning["session_type"].map(
        {"Returning-user session": 0, "New-user session": 1}
    )
    new_returning = new_returning.sort_values("sort_order").drop(columns="sort_order")
    write(new_returning, "new_vs_returning.csv", {"conversion_rate": 6})

    product = items.merge(products[["product_key", "product_name", "category", "subcategory"]], on="product_key")
    product = product.groupby(["product_name", "category", "subcategory"], as_index=False).agg(
        units=("quantity", "sum"),
        orders=("order_id", "nunique"),
        revenue=("item_revenue", "sum"),
    )
    product["avg_selling_price"] = product["revenue"] / product["units"]
    product = product.sort_values("revenue", ascending=False)
    write(product, "product_performance.csv", {"revenue": 2, "avg_selling_price": 2})

    print(f"Rebuilt 7 output files in {OUTPUTS}")


if __name__ == "__main__":
    main()
