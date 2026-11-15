"""Unit tests of the self-authored synthetic fixture; no application server execution."""
import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('domain',Path(__file__).parent/'fixtures/sample-shop/domain.py');domain=importlib.util.module_from_spec(spec);spec.loader.exec_module(domain)
class FixtureDomainTests(unittest.TestCase):
 def setUp(self):self.shop=domain.Shop()
 def test_purchase_history_cancel(self):
  s=self.shop;s.login('demo','demo');id=s.purchase('book',1);self.assertEqual(s.stock['book'],1);self.assertEqual(s.history()[0]['id'],id);s.cancel(id);self.assertEqual(s.stock['book'],2);self.assertEqual(s.history()[0]['status'],'cancelled');s.logout();self.assertFalse(s.signed_in)
 def test_evidenced_errors(self):
  s=self.shop
  for action,error in [(lambda:s.login('',''),ValueError),(lambda:s.login('wrong','wrong'),PermissionError),(lambda:s.purchase('book',1),PermissionError),(lambda:s.history(),PermissionError),(lambda:s.cancel(1),PermissionError)]:
   with self.assertRaises(error):action()
  s.login('demo','demo')
  for product,qty in [('book',0),('book',True),('missing',1),('book',99)]:
   with self.assertRaises(ValueError):s.purchase(product,qty)
  with self.assertRaises(ValueError):s.cancel(42)
  id=s.purchase('book',1);s.cancel(id)
  with self.assertRaises(ValueError):s.cancel(id)
