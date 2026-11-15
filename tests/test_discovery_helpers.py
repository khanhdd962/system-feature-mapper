import importlib.util,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import *
spec=importlib.util.spec_from_file_location('scanner',PACKAGE/'scripts/scan-project.py');scanner=importlib.util.module_from_spec(spec);spec.loader.exec_module(scanner)
class DiscoveryTests(unittest.TestCase):
 def test_inventory_and_resume(self):
  with tempfile.TemporaryDirectory() as tmp:
   r=Path(tmp);(r/'routes.py').write_text('routes=[]');(r/'.env').write_text('TOP_SECRET=123');(r/'node_modules').mkdir();(r/'node_modules/x.js').write_text('x');(r/'large.py').write_text('x'*300000)
   ws=scanner.scan(r);inv=read(ws/'source-inventory.json');self.assertEqual({x['path'] for x in inv['files']},{'routes.py','large.py'});self.assertTrue(next(x for x in inv['files'] if x['path']=='large.py')['metadataOnly']);self.assertNotIn('TOP_SECRET',json.dumps(inv))
   write(ws/'discovery-progress.json',{'phase':'review','nodes':{'system':{'state':'complete','analysisComplete':True}}});scanner.scan(r);self.assertEqual(read(ws/'discovery-progress.json')['nodes']['system']['state'],'complete')
   (r/'routes.py').write_text('routes=[1]');scanner.scan(r);self.assertEqual(read(ws/'discovery-progress.json')['nodes']['system']['state'],'pending')
 def test_symlink_escape_and_config(self):
  with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
   r=Path(tmp);(r/'escape').symlink_to(outside,target_is_directory=True)
   with self.assertRaises(ValueError):inside(r,'escape/map.html')
   (r/'feature-map.config.yaml').write_text('analysis:\n  mode: multi-agent\n')
   with self.assertRaises(ValueError):scanner.scan(r)

 def test_framework_aware_excludes(self):
  with tempfile.TemporaryDirectory() as tmp:
   r=Path(tmp);(r/'Library').mkdir();(r/'Library/domain.py').write_text('domain=True')
   ws=scanner.scan(r);self.assertIn('Library/domain.py',[x['path'] for x in read(ws/'source-inventory.json')['files']])
   (r/'ProjectSettings').mkdir();(r/'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 2022')
   scanner.scan(r);inv=read(ws/'source-inventory.json');self.assertNotIn('Library/domain.py',[x['path'] for x in inv['files']]);self.assertIn('unity',inv['detectedStacks'])
