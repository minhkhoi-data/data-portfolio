"""Small execution fixtures for source failures, publication and provenance."""
import csv,gzip,hashlib,json,shutil,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COLS=json.loads((ROOT/'data/source/provenance.json').read_text())['retained_columns']

class PipelineContracts(unittest.TestCase):
    def fixture(self,root):
        (root/'scripts').mkdir();(root/'data/source').mkdir(parents=True);(root/'audit/evidence').mkdir(parents=True);(root/'outputs').mkdir()
        shutil.copy2(ROOT/'scripts/pipeline.py',root/'scripts/pipeline.py')
        (root/'outputs/old.marker').write_text('previous output')
        row={c:'' for c in COLS};row.update(event_date='20201101',event_timestamp='1604188800000000',event_name='purchase',event_id='event-1',user_pseudo_id='user-1',ga_session_id='1',ga_session_number='1',session_engaged='0',traffic_source='google',traffic_medium='organic',device_category='desktop',geo_country='United Kingdom',geo_continent='Europe',ecommerce_purchase_revenue_in_usd='10',currency='USD')
        source=root/'data/source/ga4_events.csv.gz'
        with gzip.open(source,'wt',newline='') as f:
            w=csv.DictWriter(f,fieldnames=COLS);w.writeheader();w.writerow(row)
        provenance={'retained_columns':COLS,'projection_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_rows':1}
        (root/'data/source/provenance.json').write_text(json.dumps(provenance))
        (root/'data/source/bigquery_source_profile.csv').write_text('source_month,exported_events,purchase_events,refund_events,missing_user_events,missing_session_events,purchase_revenue_usd_sum\n202011,1,1,0,0,0,10\n')
        return source,provenance,row
    def run_fixture(self,root):
        return subprocess.run([sys.executable,str(root/'scripts/pipeline.py')],capture_output=True,text=True,timeout=20)
    def assert_closed(self,root,result):
        self.assertNotEqual(result.returncode,0);self.assertNotIn('Published ',result.stdout)
        self.assertFalse(json.loads((root/'audit/evidence/pipeline_status.json').read_text())['outputs_valid'])
        self.assertEqual((root/'outputs/old.marker').read_text(),'previous output')
        self.assertFalse((root/'data/fact_sessions.csv').exists())
    def test_hash_mismatch_does_not_publish(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source,prov,row=self.fixture(root);prov['projection_sha256']='0'*64;(root/'data/source/provenance.json').write_text(json.dumps(prov))
            self.assert_closed(root,self.run_fixture(root))
    def test_missing_source_does_not_publish(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source,prov,row=self.fixture(root);source.unlink();self.assert_closed(root,self.run_fixture(root))
    def test_wrong_schema_does_not_publish(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source,prov,row=self.fixture(root)
            with gzip.open(source,'wt') as f:f.write('wrong\n1\n')
            prov['projection_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();(root/'data/source/provenance.json').write_text(json.dumps(prov))
            self.assert_closed(root,self.run_fixture(root))
    def test_serialized_tables_match_known_one_purchase_fixture(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.fixture(root);result=self.run_fixture(root);self.assertEqual(result.returncode,0,result.stderr)
            with (root/'data/fact_sessions.csv').open(newline='') as f:rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),1);self.assertEqual(rows[0]['session_id'],'user-1|1');self.assertEqual(float(rows[0]['session_revenue']),10)
            self.assertTrue(json.loads((root/'audit/evidence/pipeline_status.json').read_text())['outputs_valid'])
    def test_importer_does_not_invent_archive_download_date(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);_,_,row=self.fixture(root);shutil.copy2(ROOT/'scripts/import_source.py',root/'scripts/import_source.py')
            import io
            stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=COLS);w.writeheader();w.writerow(row)
            archive=root/'fixture.zip'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('fixture.csv',stream.getvalue())
            result=subprocess.run([sys.executable,str(root/'scripts/import_source.py'),'--zip',str(archive)],capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr);record=json.loads((root/'data/source/provenance.json').read_text())
            self.assertIsNone(record['downloaded_on']);self.assertIn('projection_created_utc',record);self.assertEqual(record['source_rows'],1)

if __name__=='__main__':unittest.main(verbosity=2)
