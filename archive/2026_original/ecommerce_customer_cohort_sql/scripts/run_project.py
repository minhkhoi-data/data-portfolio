"""Run the SQL project with bounded resources. All business transformations live in sql/."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
import threading
import time

import duckdb

ROOT = Path(__file__).resolve().parents[1]
QUERY_NAMES = {
    '02_quality_controls': 'quality_controls',
    '03_overall_windows': 'overall_windows',
    '04_monthly_cohorts': 'monthly_cohorts',
    '05_channel_sensitivity': 'channel_sensitivity',
    '06_purchase_timing': 'purchase_timing',
    '07_return_gaps': 'return_gaps',
    '08_fixed_population': 'fixed_population',
    '09_device_cohorts': 'device_cohorts',
    '10_daily_cohorts': 'daily_cohorts',
    '11_monthly_fixed_population': 'monthly_fixed_population',
}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def execute_bounded(con, sql, seconds=90):
    timer = threading.Timer(seconds, con.interrupt)
    timer.daemon = True
    timer.start()
    try:
        return con.execute(sql)
    finally:
        timer.cancel()


def export_query(con, sql, destination):
    # COPY keeps export inside the same interruptible SQL operation.
    quoted = str(destination).replace("'", "''")
    execute_bounded(con, f"COPY ({sql.rstrip().rstrip(';')}) TO '{quoted}' (HEADER, DELIMITER ',')")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, default=ROOT,
                        help='Optional separate build target; inputs always come from this project.')
    args = parser.parse_args()
    out = args.output_root.resolve()
    if duckdb.__version__ != '1.4.3':
        raise RuntimeError('Use the pinned dependency: python -m pip install -r requirements.txt')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'audit').mkdir(exist_ok=True)
    (out / 'database').mkdir(exist_ok=True)
    (out / 'results').mkdir(exist_ok=True)
    os.chdir(ROOT)
    start = time.monotonic()
    log = {'status': 'RUNNING', 'started_utc': datetime.now(timezone.utc).isoformat(),
           'duckdb_version': duckdb.__version__, 'memory_limit': '512MB', 'threads': 1,
           'per_statement_timeout_seconds': 90, 'steps': []}
    try:
        manifest = json.loads((ROOT / 'audit/input_identity.json').read_text())
        for item in manifest['files']:
            p = ROOT / item['file']
            if p.stat().st_size != item['bytes'] or sha256(p) != item['sha256']:
                raise AssertionError('Audited input changed: ' + item['file'])
        log['input_files_verified'] = len(manifest['files'])
        print(f"Inputs: {len(manifest['files'])} file hashes match audited copies", flush=True)
        with tempfile.TemporaryDirectory(prefix='ga4_cohort_') as temp:
            temp = Path(temp)
            staged = temp / 'results'
            staged.mkdir()
            candidate = temp / 'ga4_cohorts.duckdb'
            con = duckdb.connect(str(candidate))
            con.execute("SET memory_limit='512MB'; SET threads=1; SET max_temp_directory_size='2GB'")
            # Each statement gets its own cancellation deadline.
            for name in ['00_load_audited', '01_build_cohorts']:
                t = time.monotonic()
                source = (ROOT / 'sql' / (name + '.sql')).read_text()
                for statement in con.extract_statements(source):
                    execute_bounded(con, statement.query)
                log['steps'].append({'step': name, 'seconds': round(time.monotonic()-t, 3)})
                print(name + ': complete', flush=True)
            for name, result_name in QUERY_NAMES.items():
                t = time.monotonic()
                sql = (ROOT / 'sql' / (name + '.sql')).read_text()
                # Persistent result views can be opened directly in any DuckDB SQL client.
                execute_bounded(con, 'CREATE OR REPLACE VIEW result_' + result_name + ' AS ' + sql)
                export_query(con, sql, staged / (result_name + '.csv'))
                log['steps'].append({'step': name, 'seconds': round(time.monotonic()-t, 3)})
                print(name + ': exported', flush=True)
            execute_bounded(con, 'CHECKPOINT')
            con.close()
            # Verify using the source CSV files and an independent standard-library oracle.
            from verify import verify
            evidence = verify(ROOT, candidate, staged)
            if evidence['status'] != 'PASS':
                raise AssertionError('Independent validation failed')
            (out / 'audit/validation.json').write_text(json.dumps(evidence, indent=2))
            # Publish a verified database and results; preserve previous files on prior-stage errors.
            shutil.copy2(candidate, out / 'database/ga4_cohorts.duckdb')
            for p in staged.glob('*.csv'):
                shutil.copy2(p, out / 'results' / p.name)
        log['status'] = 'PASS'
        log['validation_checks'] = evidence['checks_passed']
        log['elapsed_seconds'] = round(time.monotonic() - start, 3)
        print(f"PASS: {evidence['checks_passed']} validation checks; {log['elapsed_seconds']} seconds", flush=True)
    except Exception as exc:
        log.update(status='FAIL', error=str(exc), elapsed_seconds=round(time.monotonic()-start, 3))
        raise
    finally:
        (out / 'audit/run.json').write_text(json.dumps(log, indent=2))


if __name__ == '__main__':
    main()
