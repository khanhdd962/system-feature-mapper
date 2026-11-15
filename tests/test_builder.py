import copy,importlib.util,tempfile,sys,unittest,hashlib,json,subprocess,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import *
def module(name):
 spec=importlib.util.spec_from_file_location(name,PACKAGE/'scripts'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
builder=module('build-mindmap');verifier=module('verify-output')
class BuilderTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.data=read(PACKAGE/'examples/example-feature-map.json')
 def tearDown(self):self.tmp.cleanup()
 def test_determinism_unicode_and_markdown(self):
  self.data['features'][0]['name']='Tiếng Việt 日本語 " </script><script>alert(1)</script>'
  out=builder.build(self.root,self.data);before={p.name:p.read_bytes() for p in out.rglob('*') if p.is_file()};verifier.verify(self.root);builder.build(self.root,self.data);self.assertEqual(before,{p.name:p.read_bytes() for p in out.rglob('*') if p.is_file()});self.assertNotIn('</script><script>alert(1)',(out/'index.html').read_text());self.assertTrue((out/'details/shop.purchase.md').is_file())
 def test_redaction(self):
  self.data['features'][0]['purpose']='api_key=sk-123456789012345678901234 email user@example.com'
  out=builder.build(self.root,self.data)
  for p in out.rglob('*'):
   if p.is_file():self.assertNotIn('sk-123456789012345678901234',p.read_text());self.assertNotIn('user@example.com',p.read_text())
 def test_missing_evidence(self):
  self.data['features'][0]['verification']['evidence']=[{'path':'missing.py','type':'domain','summary':'missing'}]
  with self.assertRaisesRegex(ValueError,'missing evidence'):builder.build(self.root,self.data)
 def test_partial_and_symlink(self):
  ws=self.root/'workspace';ws.mkdir();write(ws/'feature-tree.json',{'nodes':[]});write(ws/'project-overview.json',{});write(ws/'discovery-progress.json',{'nodes':{'system':{'state':'in_progress'}}})
  with self.assertRaisesRegex(ValueError,'Unreviewed'):builder.merge(ws)
  with tempfile.TemporaryDirectory() as other:
   out=self.root/'docs/feature-map';out.mkdir(parents=True);(out/'index.html').symlink_to(Path(other)/'index.html')
   with self.assertRaisesRegex(ValueError,'escapes'):builder.build(self.root,self.data)
   self.assertFalse((Path(other)/'index.html').exists())
 def test_broken_document_detected(self):
  out=builder.build(self.root,self.data);(out/'details/shop.purchase.md').unlink()
  with self.assertRaisesRegex(ValueError,'Missing documentation'):verifier.verify(self.root)
 def test_cli_failure(self):
  f=self.root/'invalid.json';write(f,{})
  result=subprocess.run([sys.executable,str(PACKAGE/'scripts/validate-features.py'),str(f)],capture_output=True,text=True);self.assertNotEqual(result.returncode,0);self.assertIn('ERROR',result.stderr)
 def test_fixture_end_to_end_and_install_twice(self):
  # One unchanged installed package, two unrelated source trees; no global-home mutation.
  installed=self.root/'skills/system-feature-mapper';shutil.copytree(PACKAGE,installed,ignore=shutil.ignore_patterns('__pycache__','.git','docs','.feature-map-workspace'))
  source=PACKAGE/'tests/fixtures/sample-shop';repo=self.root/'shop';shutil.copytree(source,repo)
  def cli(name,*args):
   r=subprocess.run([sys.executable,str(installed/'scripts'/name),*map(str,args)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);return r.stdout
  before={p.relative_to(repo).as_posix():p.read_bytes() for p in [repo/'domain.py',repo/'routes.py',repo/'ui/navigation.html']}
  cli('build-mindmap.py','--repo',repo,'--workspace','.feature-map-workspace','--case-limit','2');cli('verify-output.py','--repo',repo)
  self.assertEqual(before,{name:(repo/name).read_bytes() for name in before})
  other=self.root/'notes';other.mkdir();(other/'README.md').write_text('# Personal Notes\nAn unrelated documentation repository.')
  d=copy.deepcopy(self.data);d['project']={'id':'notes','name':'Ghi chú','description':'Ví dụ repository thứ hai; dữ liệu minh họa.'};f=copy.deepcopy(d['features'][0]);f['name']='Ghi chú';d['features']=[f];write(other/'map.json',d)
  cli('scan-project.py','--repo',other);cli('build-mindmap.py','--repo',other,'--input',other/'map.json');cli('verify-output.py','--repo',other)
  self.assertTrue((installed/'SKILL.md').read_text().startswith('---\nname: system-feature-mapper\n'))
 def test_source_change_blocks_resume_build(self):
  source=PACKAGE/'tests/fixtures/sample-shop';repo=self.root/'repo';shutil.copytree(source,repo)
  with (repo/'domain.py').open('a') as f:f.write('\n# changed source\n')
  result=subprocess.run([sys.executable,str(PACKAGE/'scripts/build-mindmap.py'),'--repo',str(repo),'--workspace','.feature-map-workspace'],capture_output=True,text=True)
  self.assertNotEqual(result.returncode,0);self.assertIn('Unreviewed discovery nodes',result.stderr)
