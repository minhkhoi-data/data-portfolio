"""Project exact source columns from the downloaded Kaggle ZIP, retaining every row.

No generated outcomes, sampling, imputation, order or item fabrication.
The portable CSV projection is enough to reproduce every included analysis.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse, csv, gzip, hashlib, io, json, zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = 'https://www.kaggle.com/datasets/hashiromer/ga4-merchandise-store-flattened-bigquery'
GOOGLE_URL = 'https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset'
COLUMNS = ['event_date','event_timestamp','event_name','event_bundle_sequence_id',
 'user_pseudo_id','device_category','geo_country','geo_continent','geo_region',
 'traffic_source','traffic_medium','traffic_name','ga_session_id','ga_session_number',
 'session_engaged','engagement_time_msec','ecommerce_transaction_id',
 'ecommerce_purchase_revenue_in_usd','ecommerce_total_item_quantity','ecommerce_unique_items',
 'ecommerce_tax_value_in_usd','ecommerce_shipping_value_in_usd','ecommerce_refund_value_in_usd',
 'currency','event_id']

def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''): digest.update(block)
    return digest.hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--zip',type=Path,required=True)
    args=parser.parse_args(); out=ROOT/'data/source/ga4_events.csv.gz'
    raw_hash=hashlib.sha256();rows=0
    with zipfile.ZipFile(args.zip) as archive:
        csvs=[i for i in archive.infolist() if i.filename.endswith('.csv')]
        if len(csvs)!=1: raise ValueError('Expected exactly one source CSV')
        entry=csvs[0]
        # Hash original uncompressed bytes independently of the projection.
        with archive.open(entry) as raw:
            for block in iter(lambda:raw.read(1024*1024),b''):raw_hash.update(block)
        with archive.open(entry) as raw, out.open('wb') as target:
            with gzip.GzipFile(filename='',fileobj=target,mode='wb',compresslevel=6,mtime=0) as compressed:
                with io.TextIOWrapper(compressed,encoding='utf-8',newline='') as output:
                    reader=csv.DictReader(io.TextIOWrapper(raw,encoding='utf-8-sig',newline=''))
                    if not set(COLUMNS).issubset(reader.fieldnames or []):raise ValueError('Missing source columns')
                    all_columns=reader.fieldnames
                    writer=csv.DictWriter(output,fieldnames=COLUMNS,lineterminator='\n');writer.writeheader()
                    for row in reader:
                        if None in row or any(v is None for v in row.values()):raise ValueError(f'Malformed source row {rows+2}')
                        writer.writerow({key:row[key] for key in COLUMNS});rows+=1
                        if rows%1000000==0:print(f'Projected {rows:,} source events',flush=True)
    metadata={'source_page':SOURCE_URL,'google_source_documentation':GOOGLE_URL,
      'download_url':'https://www.kaggle.com/api/v1/datasets/download/hashiromer/ga4-merchandise-store-flattened-bigquery',
      'downloaded_on':None,'projection_created_utc':datetime.now(timezone.utc).isoformat(),'download_date_note':'Archive acquisition date was not supplied to this importer; no date is inferred.','source_zip_bytes':args.zip.stat().st_size,'source_zip_sha256':sha256(args.zip),
      'source_csv_filename':entry.filename,'source_csv_bytes':entry.file_size,'source_csv_sha256':raw_hash.hexdigest(),
      'source_rows':rows,'original_columns':all_columns,'retained_columns':COLUMNS,
      'projection_sha256':sha256(out),'projection_bytes':out.stat().st_size,
      'transform':'Exact column projection of all source rows; strings/IDs/blank values retained; gzip only.',
      'not_bundled':'Original 438 MB ZIP is retrievable from the source URL; its reproducible analytical projection is bundled.',
      'license_note':'Kaggle uploader labels the mirror MIT; this does not establish additional rights over Google source data. See upstream terms.',
      'missing_capabilities':['items/product rows','experiment assignments','verified order accounting'],
      'independent_control':'bigquery_source_profile.csv uploaded by user; selected-event counts and USD purchase-event sums reconciled separately.'}
    (ROOT/'data/source/provenance.json').write_text(json.dumps(metadata,indent=2))
    print(f'PASS: {rows:,} rows preserved in {out.stat().st_size:,} compressed bytes',flush=True)

if __name__=='__main__':main()
