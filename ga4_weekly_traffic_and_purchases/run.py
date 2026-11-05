"""Load the supplied CSVs, execute the SQL, and write both weekly reports."""
import argparse
import csv
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parent


def load_csv(connection, input_file, insert_statement, columns):
    with input_file.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        connection.executemany(
            insert_statement,
            (tuple(row[column] for column in columns) for row in reader),
        )


def run_query(connection, filename):
    result = connection.execute((ROOT / "sql" / filename).read_text(encoding="utf-8"))
    return [column[0] for column in result.description], result.fetchall()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "data_dir", nargs="?", type=Path, default=ROOT / "data" / "audited",
        help="Folder with the three GA4 CSV inputs (default: bundled data/audited)",
    )
    args = parser.parse_args()

    with sqlite3.connect(":memory:") as connection:
        connection.row_factory = sqlite3.Row
        connection.executescript("""
            CREATE TABLE fact_sessions (
                session_id TEXT PRIMARY KEY NOT NULL CHECK (session_id <> ''),
                session_date TEXT NOT NULL CHECK (session_date <> ''),
                purchase INTEGER NOT NULL CHECK (purchase IN (0, 1))
            );
            CREATE TABLE dim_date (
                date TEXT PRIMARY KEY NOT NULL CHECK (date <> ''),
                week_start TEXT NOT NULL CHECK (week_start <> '')
            );
            CREATE TABLE fact_purchases (
                session_id TEXT NOT NULL CHECK (session_id <> '')
            );
        """)
        load_csv(connection, args.data_dir / "fact_sessions.csv",
                 "INSERT INTO fact_sessions VALUES (?, ?, ?)",
                 ("session_id", "session_date", "purchase"))
        load_csv(connection, args.data_dir / "dim_date.csv",
                 "INSERT INTO dim_date VALUES (?, ?)", ("date", "week_start"))
        load_csv(connection, args.data_dir / "fact_purchases.csv",
                 "INSERT INTO fact_purchases VALUES (?)", ("session_id",))

        checks = connection.execute((ROOT / "sql/checks.sql").read_text()).fetchone()
        print(dict(checks))
        if (not checks["input_sessions"]
                or checks["input_sessions"] != checks["sessions_checked"]
                or checks["missing_calendar_dates"]
                or checks["purchase_flag_mismatches"]
                or checks["input_purchase_events"] != checks["matched_purchase_events"]):
            raise SystemExit("Data checks failed. The report was not updated.")

        columns, rows = run_query(connection, "weekly_report.sql")
        if (sum(row["total_sessions"] for row in rows) != checks["input_sessions"]
                or sum(row["sessions_with_purchase"] for row in rows)
                != checks["sessions_flagged_with_purchase"]):
            raise SystemExit("Weekly totals do not reconcile. The report was not updated.")

        comparison_columns, comparison_rows = run_query(connection, "weekly_comparison.sql")

    for filename, headings, records in (
        ("weekly_kpis.csv", columns, rows),
        ("weekly_comparison.csv", comparison_columns, comparison_rows),
    ):
        output = ROOT / "results" / filename
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headings)
            writer.writerows(records)
        print(f"Wrote {len(records)} weekly rows to {output}")


if __name__ == "__main__":
    main()
