from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]
data = root / "data"

sessions = pd.read_csv(data / "fact_sessions.csv")
orders = pd.read_csv(data / "fact_orders.csv")
items = pd.read_csv(data / "fact_order_items.csv")

checks = {
    "sessions": sessions["session_id"].nunique(),
    "users": sessions["user_id"].nunique(),
    "transactions": orders["order_id"].nunique(),
    "revenue_orders": round(orders["total_revenue"].sum(), 2),
    "revenue_items": round(items["item_revenue"].sum(), 2),
    "purchase_sessions": int(sessions["purchase"].sum()),
}

print(checks)

assert checks["sessions"] == 75237
assert checks["users"] == 32000
assert checks["transactions"] == 4737
assert abs(checks["revenue_orders"] - 217478.50) < 0.01
assert abs(checks["revenue_items"] - 217478.50) < 0.01
assert checks["purchase_sessions"] == 4737

print("All QA checks passed.")
