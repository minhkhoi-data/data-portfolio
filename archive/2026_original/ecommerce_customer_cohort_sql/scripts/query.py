"""Run a SELECT query file against the supplied database, in read-only mode."""
from pathlib import Path
import argparse
import csv
import sys
import threading
import duckdb

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('query',type=Path,help='For example: sql/03_overall_windows.sql')
args=parser.parse_args()
query=args.query if args.query.is_absolute() else ROOT/args.query
con=duckdb.connect(str(ROOT/'database/ga4_cohorts.duckdb'),read_only=True)
con.execute("SET memory_limit='256MB';SET threads=1")
timer=threading.Timer(90,con.interrupt)
timer.daemon=True
timer.start()
try:
    result=con.execute(query.read_text(encoding='utf-8'))
    writer=csv.writer(sys.stdout,lineterminator='\n')
    writer.writerow([d[0] for d in result.description])
    while True:
        batch=result.fetchmany(1000)
        if not batch:break
        writer.writerows(batch)
finally:
    timer.cancel()
    con.close()
