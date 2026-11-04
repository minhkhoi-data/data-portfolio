"""Optional full row/field comparison with a separately downloaded UCI workbook.

Usage: python analysis/verify_official_source.py --workbook /path/to/online_retail_II.xlsx
Requires openpyxl (verification-only dependency). Does not download anything.
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'Price', 'Customer ID', 'Country']
NUMERIC = {3, 5, 6}
TOLERANCE = 1e-10


def text(value):
    if value is None or value == '':
        return ''
    if isinstance(value, (int, float)) and float(value).is_integer():
        return str(int(value))
    return str(value)


def equal(actual, expected, column):
    if column in NUMERIC:
        if actual in ('', None) or expected in ('', None):
            return actual in ('', None) and expected in ('', None)
        return math.isclose(float(actual), float(expected), abs_tol=TOLERANCE, rel_tol=0)
    if column == 4:
        if actual in ('', None) or expected in ('', None):
            return actual in ('', None) and expected in ('', None)
        return datetime.fromisoformat(actual) == expected
    return text(actual) == text(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook', required=True, type=Path)
    args = parser.parse_args()
    source = ROOT/'data/online_retail_II.csv.gz'
    workbook = openpyxl.load_workbook(args.workbook, read_only=True, data_only=True)
    mismatches = dict.fromkeys(COLUMNS, 0)
    examples = []
    rows = 0
    numeric_descriptions = []
    sheets = []
    with gzip.open(source, 'rt', newline='', encoding='utf-8') as stream:
        reader = csv.reader(stream)
        if next(reader) != COLUMNS:
            raise ValueError('Bundled CSV schema differs from the audited contract')
        for sheet in workbook:
            sheets.append(sheet.title)
            iterator = sheet.iter_rows(values_only=True)
            if list(next(iterator)) != COLUMNS:
                raise ValueError('Official workbook schema differs from the audited contract')
            for expected in iterator:
                actual = next(reader, None)
                if actual is None:
                    raise ValueError('CSV ended before official workbook')
                rows += 1
                if isinstance(expected[2], (int, float)):
                    numeric_descriptions.append(rows - 1)
                for index, name in enumerate(COLUMNS):
                    if not equal(actual[index], expected[index], index):
                        mismatches[name] += 1
                        if len(examples) < 8:
                            examples.append({'zero_based_row': rows-1, 'field': name,
                                             'csv': str(actual[index]), 'workbook': str(expected[index])})
                if rows % 100000 == 0:
                    print(f'Compared {rows:,} rows; mismatches={sum(mismatches.values())}', flush=True)
        if next(reader, None) is not None:
            raise ValueError('CSV contains rows after official workbook ends')
    workbook.close()
    report = {
        'status': 'PASS' if not sum(mismatches.values()) else 'FAIL',
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'official_url': 'https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip',
        'xlsx_sha256': hashlib.sha256(args.workbook.read_bytes()).hexdigest(),
        'csv_gzip_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_sheets': sheets, 'rows_compared': rows, 'all_eight_fields_compared': True,
        'mismatches_after_documented_normalization': mismatches,
        'examples': examples, 'numeric_description_rows_normalized_as_text': numeric_descriptions,
        'numeric_tolerance': TOLERANCE,
        'normalization': 'Blank=None/empty; identifiers and descriptions as text; numeric labels rendered without .0; ISO timestamps; numeric fields absolute tolerance 1e-10.',
        'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }
    (ROOT/'audit/takeover_source_verification.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({k: report[k] for k in ['status','rows_compared','mismatches_after_documented_normalization']}, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
