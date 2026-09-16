from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PBIP = ROOT / "powerbi" / "EcommerceGrowth_PBIP"
MODEL = PBIP / "EcommerceGrowth.SemanticModel" / "definition"
REPORT = PBIP / "EcommerceGrowth.Report" / "definition"

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(condition), detail))


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv")


def validate_data() -> None:
    tables = {path.stem: pd.read_csv(path) for path in DATA.glob("*.csv")}
    sessions = tables["fact_sessions"]
    orders = tables["fact_orders"]
    items = tables["fact_order_items"]

    check("Session grain is unique", sessions["session_id"].is_unique, f"{len(sessions):,} rows")
    check("Order grain is unique", orders["order_id"].is_unique, f"{len(orders):,} rows")
    check("Order lines have no duplicate rows", not items.duplicated().any(), f"{len(items):,} rows")

    for table_name, key in [
        ("dim_date", "date"),
        ("dim_channel", "channel_id"),
        ("dim_device", "device_id"),
        ("dim_geo", "geo_id"),
        ("dim_product", "product_key"),
    ]:
        frame = tables[table_name]
        check(f"{table_name} key is unique", frame[key].is_unique and frame[key].notna().all())

    references = [
        ("fact_sessions", "session_date", "dim_date", "date"),
        ("fact_sessions", "channel_id", "dim_channel", "channel_id"),
        ("fact_sessions", "device_id", "dim_device", "device_id"),
        ("fact_sessions", "geo_id", "dim_geo", "geo_id"),
        ("fact_orders", "order_date", "dim_date", "date"),
        ("fact_orders", "channel_id", "dim_channel", "channel_id"),
        ("fact_orders", "device_id", "dim_device", "device_id"),
        ("fact_orders", "geo_id", "dim_geo", "geo_id"),
        ("fact_order_items", "order_date", "dim_date", "date"),
        ("fact_order_items", "product_key", "dim_product", "product_key"),
        ("fact_order_items", "channel_id", "dim_channel", "channel_id"),
        ("fact_order_items", "device_id", "dim_device", "device_id"),
        ("fact_order_items", "geo_id", "dim_geo", "geo_id"),
    ]
    for fact, foreign_key, dimension, dimension_key in references:
        missing = set(tables[fact][foreign_key].dropna()) - set(tables[dimension][dimension_key].dropna())
        check(f"{fact}.{foreign_key} resolves to {dimension}", not missing, f"{len(missing)} missing keys")

    flags = ["is_new_user", "engaged_session", "view_item", "add_to_cart", "begin_checkout", "purchase"]
    check("Session flags are binary", all(set(sessions[column].dropna().unique()) <= {0, 1} for column in flags))
    sequential = (
        (sessions["view_item"] >= sessions["add_to_cart"])
        & (sessions["add_to_cart"] >= sessions["begin_checkout"])
        & (sessions["begin_checkout"] >= sessions["purchase"])
    )
    check("Funnel flags are sequential per session", sequential.all())

    purchase_rows = sessions[sessions["purchase"] == 1]
    nonpurchase_rows = sessions[sessions["purchase"] == 0]
    check("Purchase sessions have order IDs", purchase_rows["order_id"].notna().all())
    check("Non-purchase sessions have no order IDs", nonpurchase_rows["order_id"].isna().all())
    check("Every order resolves to a purchase session", set(orders["session_id"]) == set(purchase_rows["session_id"]))
    check("Every item resolves to an order", set(items["order_id"]) <= set(orders["order_id"]))

    order_session = orders.merge(
        purchase_rows[
            ["session_id", "user_id", "session_date", "channel_id", "device_id", "geo_id", "order_id", "session_revenue"]
        ],
        on="session_id",
        suffixes=("_order", "_session"),
    )
    same_attributes = (
        (order_session["user_id_order"] == order_session["user_id_session"])
        & (order_session["order_date"] == order_session["session_date"])
        & (order_session["channel_id_order"] == order_session["channel_id_session"])
        & (order_session["device_id_order"] == order_session["device_id_session"])
        & (order_session["geo_id_order"] == order_session["geo_id_session"])
        & (order_session["order_id_order"] == order_session["order_id_session"])
        & np.isclose(order_session["total_revenue"], order_session["session_revenue"], atol=0.01)
    )
    check("Order attributes reconcile to purchase sessions", same_attributes.all())

    item_rollup = items.groupby("order_id", as_index=False).agg(
        item_revenue=("item_revenue", "sum"),
        item_quantity=("quantity", "sum"),
        item_products=("product_key", "nunique"),
    )
    order_rollup = orders.merge(item_rollup, on="order_id")
    check(
        "Order revenue reconciles to items",
        np.isclose(order_rollup["total_revenue"], order_rollup["item_revenue"], atol=0.01).all(),
        f"${orders['total_revenue'].sum():,.2f}",
    )
    check("Order quantity reconciles to items", (order_rollup["total_quantity"] == order_rollup["item_quantity"]).all())
    check(
        "Distinct products reconcile to items",
        (order_rollup["distinct_products"] == order_rollup["item_products"]).all(),
    )
    check("Revenue and quantity are non-negative", (orders["total_revenue"] >= 0).all() and (items["quantity"] > 0).all())

    expected = {
        "Sessions": sessions["session_id"].nunique() == 75237,
        "Users": sessions["user_id"].nunique() == 32000,
        "Transactions": orders["order_id"].nunique() == 4737,
        "Revenue": np.isclose(orders["total_revenue"].sum(), 217478.50, atol=0.01),
        "Product view sessions": sessions["view_item"].sum() == 51592,
        "Add-to-cart sessions": sessions["add_to_cart"].sum() == 15090,
        "Checkout sessions": sessions["begin_checkout"].sum() == 8111,
        "Purchase sessions": sessions["purchase"].sum() == 4737,
        "Purchasers": orders["user_id"].nunique() == 4428,
        "Repeat purchasers": (orders.groupby("user_id")["order_id"].nunique() > 1).sum() == 293,
    }
    for metric, matches in expected.items():
        check(f"Expected total: {metric}", matches)


def semantic_inventory() -> tuple[dict[str, set[str]], set[tuple[str, str]], int]:
    entities: dict[str, set[str]] = {}
    measures: set[tuple[str, str]] = set()
    for path in (MODEL / "tables").glob("*.tmdl"):
        text = path.read_text(encoding="utf-8")
        table_match = re.search(r"^table\s+(.+)$", text, re.MULTILINE)
        if not table_match:
            continue
        table = table_match.group(1).strip().strip("'")
        columns = {
            value.strip().strip("'")
            for value in re.findall(r"^\s*column\s+(.+)$", text, re.MULTILINE)
        }
        entities[table] = columns
        for measure in re.findall(r"^\s*measure\s+'([^']+)'\s*=", text, re.MULTILINE):
            measures.add((table, measure))
    relationship_text = (MODEL / "relationships.tmdl").read_text(encoding="utf-8")
    relationship_count = len(re.findall(r"^relationship\s+", relationship_text, re.MULTILINE))
    return entities, measures, relationship_count


def validate_power_bi_source() -> None:
    json_paths = list(PBIP.rglob("*.json")) + list(PBIP.glob("*.pbip")) + list(PBIP.rglob("*.pbir")) + list(
        PBIP.rglob("*.pbism")
    ) + list(PBIP.rglob(".platform"))
    json_errors: list[str] = []
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - validation should report every malformed source file
            json_errors.append(f"{path.relative_to(ROOT)}: {exc}")
    check("PBIP/PBIR JSON files parse", not json_errors, f"{len(json_paths)} files")

    report_definition = json.loads((REPORT / "report.json").read_text(encoding="utf-8"))
    unsupported_settings = {"keyboardNavigationEnabled"} & set(report_definition.get("settings", {}))
    check("Report settings exclude known unsupported properties", not unsupported_settings)

    entities, measures, relationship_count = semantic_inventory()
    check("Semantic model has 31 explicit measures", len(measures) == 31, str(len(measures)))
    check("Semantic model has 13 relationships", relationship_count == 13, str(relationship_count))

    pages_root = REPORT / "pages"
    pages_config = json.loads((pages_root / "pages.json").read_text(encoding="utf-8"))
    page_paths = sorted(pages_root.glob("*/page.json"))
    page_names = {json.loads(path.read_text(encoding="utf-8"))["name"] for path in page_paths}
    configured_pages = pages_config.get("pageOrder", [])
    check("Report has five configured pages", len(page_paths) == 5 and len(configured_pages) == 5)
    check("Configured page folders exist", set(configured_pages) == page_names)
    check("Active page exists", pages_config.get("activePageName") in page_names)

    binding_errors: list[str] = []
    bounds_errors: list[str] = []
    untitled_visuals: list[str] = []
    visual_count = 0
    for page_path in page_paths:
        page = json.loads(page_path.read_text(encoding="utf-8"))
        page_dir = page_path.parent
        width, height = page["width"], page["height"]
        for visual_path in sorted(page_dir.glob("visuals/*/visual.json")):
            visual_count += 1
            data = json.loads(visual_path.read_text(encoding="utf-8"))
            position = data.get("position", {})
            if (
                position.get("x", 0) < 0
                or position.get("y", 0) < 0
                or position.get("x", 0) + position.get("width", 0) > width
                or position.get("y", 0) + position.get("height", 0) > height
            ):
                bounds_errors.append(str(visual_path.relative_to(ROOT)))

            visual = data.get("visual", {})
            if not visual.get("visualContainerObjects", {}).get("title"):
                untitled_visuals.append(str(visual_path.relative_to(ROOT)))
            query_states = visual.get("query", {}).get("queryState", {})
            for state in query_states.values():
                for projection in state.get("projections", []):
                    field = projection.get("field", {})
                    if "Measure" in field:
                        definition = field["Measure"]
                        entity = definition["Expression"]["SourceRef"]["Entity"]
                        prop = definition["Property"]
                        if (entity, prop) not in measures:
                            binding_errors.append(f"missing measure {entity}.{prop}")
                    elif "Column" in field:
                        definition = field["Column"]
                        entity = definition["Expression"]["SourceRef"]["Entity"]
                        prop = definition["Property"]
                        if entity not in entities or prop not in entities[entity]:
                            binding_errors.append(f"missing column {entity}.{prop}")

    check("Report has 45 visual definitions", visual_count == 45, str(visual_count))
    check("Visuals fit within their page canvases", not bounds_errors, f"{len(bounds_errors)} out of bounds")
    check("Visual bindings resolve to the semantic model", not binding_errors, f"{len(binding_errors)} errors")
    check("All data visuals have titles", not untitled_visuals, f"{len(untitled_visuals)} untitled")


def validate_outputs() -> None:
    expected = {
        "channel_performance.csv",
        "device_performance.csv",
        "funnel_performance.csv",
        "kpi_summary.csv",
        "monthly_performance.csv",
        "new_vs_returning.csv",
        "product_performance.csv",
    }
    existing = {path.name for path in (ROOT / "outputs").glob("*.csv")}
    check("All seven summary outputs exist", expected == existing, f"{len(existing)} files")


def main() -> int:
    validate_data()
    validate_power_bi_source()
    validate_outputs()

    for name, passed, detail in RESULTS:
        status = "PASS" if passed else "FAIL"
        suffix = f" — {detail}" if detail else ""
        print(f"[{status}] {name}{suffix}")

    passed_count = sum(passed for _, passed, _ in RESULTS)
    total = len(RESULTS)
    print(f"\nStatic source validation: {passed_count}/{total} checks passed.")
    print("Power BI Desktop open, refresh, interaction, and render checks are outside this script.")
    return 0 if passed_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
