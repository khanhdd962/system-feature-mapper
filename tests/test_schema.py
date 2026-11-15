import copy, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import *
class SchemaTests(unittest.TestCase):
 def setUp(self): self.data=read(PACKAGE/'examples/example-feature-map.json')
 def test_valid(self): validate(self.data)
 def test_invalid(self):
  mutations=[lambda d:d['features'].append(copy.deepcopy(d['features'][0])),lambda d:d['features'][1].update(parentId='missing'),lambda d:d['features'][1].update(parentId='account.login'),lambda d:d['features'][1].update(relatedFeatureIds=['missing']),lambda d:d['features'][1].update(documentationPath='../secret.md'),lambda d:d['features'][1].pop('purpose'),lambda d:d['features'][1].update(kind='action'),lambda d:d['features'][1]['verification'].update(status='source_confirmed')]
  for mutate in mutations:
   with self.subTest(mutate=mutate):
    d=copy.deepcopy(self.data); mutate(d)
    with self.assertRaises(ValueError): validate(d)
 def test_paths(self):
  for p in ['../x','/x','C:/x','a\\b','details/%2e%2e/x','a//b','./x','https://x']:
   self.assertFalse(safe_relative(p),p)
 def test_id_stability(self): self.assertEqual(stable_id('route:/buy'),stable_id('route:/buy'))
 def test_unknowns_and_claim_evidence(self):
  d=copy.deepcopy(self.data);d['features'][0].pop('unknowns')
  with self.assertRaisesRegex(ValueError,'unknown reason'):validate(d)
  d=copy.deepcopy(self.data);v=d['features'][0]['verification'];v['status']='source_confirmed';v['evidence']=[{'path':'README.md','type':'docs','summary':'purpose'}]
  with self.assertRaisesRegex(ValueError,'claim evidence mapping'):validate(d)
 def test_arbitrary_depth(self):
  d=copy.deepcopy(self.data);base=copy.deepcopy(d['features'][0]);d['features']=[base];parent=base['id']
  for i in range(400):
   f=copy.deepcopy(base);f.update(id=f'depth-{i}',parentId=parent,kind='feature');d['features'].append(f);parent=f['id']
  validate(d)
