import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('publisher',ROOT/'scripts/publish_research.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PlayerGuidesTest(unittest.TestCase):
 def test_published_records_are_explanations_not_internal_reports(self):
  feed=m.build(ROOT);self.assertGreaterEqual(len(feed['records']),20)
  for r in feed['records']:
   self.assertEqual(r['player']['version'],1);self.assertIn('Why it matters',r['text']);self.assertIn('How to use it',r['text']);self.assertIn('What to watch for',r['text']);self.assertFalse(r['text'].lstrip().startswith('{'));self.assertNotIn('runtime_verified',r['text']);self.assertNotIn('measured_pve',r['text']);self.assertNotEqual(r['evidence'],'software')
 def test_raw_data_cannot_become_player_guides_by_default(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();(root/'data/raw.json').write_text('{"records":[{"id":"software"}]}')
   with self.assertRaises(FileNotFoundError):m.build(root)
 def test_missing_practical_explanation_fails_publication(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();(root/'data/player_discoveries.json').write_text(json.dumps({'records':[{'player':{'version':1}}]}))
   with self.assertRaises(ValueError):m.build(root)
 def test_duplicate_cards_fail_publication(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();v=json.loads((ROOT/'data/player_discoveries.json').read_text())['records'][0];(root/'data/player_discoveries.json').write_text(json.dumps({'records':[v,v]}))
   with self.assertRaises(ValueError):m.build(root)
 def test_player_labels_and_title_are_required(self):
  base=json.loads((ROOT/'data/player_discoveries.json').read_text())['records'][0]
  for field in ('title','category','activity','guardian'):
   with self.subTest(field=field),tempfile.TemporaryDirectory() as folder:
    root=Path(folder);(root/'data').mkdir();v=json.loads(json.dumps(base))
    if field=='title':v['title']='  '
    else:v['player'][field]='  '
    (root/'data/player_discoveries.json').write_text(json.dumps({'records':[v]}))
    with self.assertRaises(ValueError):m.build(root)
 def test_provenance_rejects_invalid_urls_and_dates(self):
  base=json.loads((ROOT/'data/player_discoveries.json').read_text())['records'][0]
  for field,value in [('source_url','https://'),('source_url','https://user:pass@example.org/a'),('source_url','http://example.org/a'),('reviewed_at','2026-02-30'),('source_published_at','not-a-date'),('reviewed_at','2020-01-01')]:
   with self.subTest(field=field,value=value),tempfile.TemporaryDirectory() as folder:
    root=Path(folder);(root/'data').mkdir();v=json.loads(json.dumps(base));v[field]=value
    (root/'data/player_discoveries.json').write_text(json.dumps({'records':[v]}))
    with self.assertRaises(ValueError):m.build(root)
if __name__=='__main__':unittest.main()
