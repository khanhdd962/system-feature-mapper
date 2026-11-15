"""Actual Chromium integration tests with self-contained artifact served by interception. No application runtime is started."""
import importlib.util, tempfile, unittest, sys, copy, os, shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import *
spec=importlib.util.spec_from_file_location('builder',PACKAGE/'scripts/build-mindmap.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
from playwright.sync_api import sync_playwright, expect
class ViewerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name);cls.data=read(PACKAGE/'examples/example-feature-map.json');builder.build(cls.root,cls.data)
  cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome'),headless=True,args=['--no-sandbox']);cls.page=cls.browser.new_page(viewport={'width':1440,'height':1000});cls.errors=[];cls.network=[];cls.page.on('pageerror',lambda e:cls.errors.append(str(e)));cls.page.on('request',lambda r:cls.network.append(r.url) if r.resource_type!='document' and r.url.startswith(('http:','https:')) else None);cls.page.route('http://feature-map.test/**',lambda route:route.fulfill(path=str(cls.root/route.request.url.split('feature-map.test/')[1])))
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.tmp.cleanup()
 def setUp(self):self.page.goto('http://feature-map.test/docs/feature-map/index.html')
 def test_interactions(self):
  p=self.page;self.assertEqual(p.locator('[data-node-id]').count(),4)
  p.locator('.toggle[aria-label="Mở Mua sắm"]').click();self.assertEqual(p.locator('[data-node-id]').count(),5)
  p.locator('[data-node-id="shop.purchase"]').click();self.assertTrue(p.locator('dialog').is_visible());self.assertEqual(p.locator('#detail-title').inner_text(),'Mua sản phẩm')
  p.get_by_role('tab',name='Tình huống',exact=True).click();self.assertIn('thiếu sản phẩm',p.locator('#tab-content').inner_text())
  p.get_by_role('button',name='Đọc tại đây',exact=True).click();self.assertTrue(p.locator('pre.markdown').is_visible())
  p.get_by_role('tab',name='Liên quan',exact=True).click();p.locator('#tab-content button').click();self.assertEqual(p.locator('#detail-title').inner_text(),'Xem lịch sử')
  p.keyboard.press('Escape');self.assertFalse(p.locator('dialog').is_visible());expect(p.locator('[data-node-id="orders.history"]')).to_be_focused()
  p.locator('#search').fill('dang nhap');self.assertEqual(p.locator('#result-count').inner_text(),'1 kết quả');p.locator('#results').select_option('account.login');self.assertEqual(p.locator('#detail-title').inner_text(),'Đăng nhập')
  p.keyboard.press('Escape');p.locator('#expand-all').click();self.assertEqual(p.locator('[data-node-id]').count(),7);p.locator('#collapse-all').click();self.assertEqual(p.locator('[data-node-id]').count(),4)
  before=p.locator('#viewport').get_attribute('transform');p.locator('#zoom-in').click();self.assertNotEqual(before,p.locator('#viewport').get_attribute('transform'))
  p.locator('#map').hover(position={'x':1000,'y':500});p.mouse.wheel(0,200);p.wait_for_timeout(100)
  before=p.locator('#viewport').get_attribute('transform');p.mouse.move(1100,550);p.mouse.down();p.mouse.move(1150,580);p.mouse.up();self.assertNotEqual(before,p.locator('#viewport').get_attribute('transform'));self.assertFalse(p.locator('dialog').is_visible());p.locator('#fit').click();p.locator('#reset').click()
  self.assertFalse(self.errors);self.assertFalse(self.network)
 def test_focus_and_keyboard(self):
  p=self.page;p.locator('[data-node-id="account"]').focus();p.keyboard.press('ArrowRight');self.assertEqual(p.locator('[data-node-id]').count(),5);p.keyboard.press('Enter');self.assertTrue(p.locator('dialog').is_visible());p.keyboard.press('Shift+Tab');self.assertTrue(p.evaluate('document.getElementById("detail").contains(document.activeElement)'));p.keyboard.press('Tab');self.assertEqual(p.evaluate('document.activeElement.id'),'close-dialog');p.keyboard.press('Escape');expect(p.locator('[data-node-id="account"]')).to_be_focused()
 def test_large_tree_and_injection(self):
  d=copy.deepcopy(self.data);base=d['features'][-1]
  for i in range(350):
   f=copy.deepcopy(base);f.update(id=f'large-{i}',parentId='shop',name=f'Chức năng {i}');d['features'].append(f)
  d['features'][0]['name']='</script><script>window.PWNED=1</script>日本語'
  builder.build(self.root,d,output='large');p=self.page;p.goto('http://feature-map.test/large/index.html');self.assertEqual(p.locator('[data-node-id]').count(),4);self.assertIsNone(p.evaluate('window.PWNED'));p.locator('#expand-all').click();self.assertEqual(p.locator('[data-node-id]').count(),357);p.screenshot(path=str(self.root/'viewer-screenshot.png'),full_page=True);self.assertFalse(self.errors)
