#!/usr/bin/env python3
"""Verify generated HTML/JSON, embedded data, documentation links and source evidence."""
import argparse,json
from html.parser import HTMLParser
from common import *
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.errors=[];self.capture=False;self.payload=''
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='script' and a.get('id')=='map-data':self.capture=True
  if 'src' in a or tag=='link':self.errors.append('External resource element')
  if 'href' in a:self.links.append(a['href'])
 def handle_endtag(self,tag):
  if tag=='script':self.capture=False
 def handle_data(self,text):
  if self.capture:self.payload+=text

def verify(repo,output='docs/feature-map'):
 out=inside(repo,output);data=validate(read(out/'feature-map.json'),repo);html=(out/'index.html').read_text();parser=Parser();parser.feed(html);errors=parser.errors
 for name in ['index.html','feature-map.json','analysis-report.md']:
  if not (out/name).is_file():errors.append('Missing '+name)
 if len(parser.ids)!=len(set(parser.ids)):errors.append('Duplicate HTML IDs')
 for id in ['map','nodes','edges','detail','search','tabs','tab-content','results','viewport']:
  if id not in parser.ids:errors.append('Missing HTML control '+id)
 if '/*__' in html:errors.append('Unresolved template placeholder')
 payload=json.loads(parser.payload)
 if {f['id'] for f in payload['map']['features']}!={f['id'] for f in data['features']}:errors.append('Embedded ID mismatch')
 for f in data['features']:
  public=next(x for x in payload['map']['features'] if x['id']==f['id'])
  if public['name']!=f['name'] or public['purpose']!=f['purpose']:errors.append('Embedded content mismatch '+f['id'])
  if 'evidence' in public['verification']:errors.append('Evidence leaked into ordinary UI')
  if f['documentationPath']:
   doc=inside(out,f['documentationPath'])
   if not doc.is_file():errors.append('Missing documentation '+f['id'])
   elif payload['markdown'].get(f['id'])!=doc.read_text(encoding='utf-8'):errors.append('Markdown bundle mismatch '+f['id'])
 for link in parser.links:
  if not safe_relative(link) or not inside(out,link).is_file():errors.append('Unsafe/broken link '+link)
 if errors:raise ValueError('\n'.join(errors))
 print(f'VERIFIED: {len(data["features"])} nodes; {len(payload["markdown"])} Markdown documents; no external resource elements')
 return data

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True);p.add_argument('--output');a=p.parse_args()
 from importlib.util import spec_from_file_location,module_from_spec
 spec=spec_from_file_location('scanner',PACKAGE/'scripts/scan-project.py');m=module_from_spec(spec);spec.loader.exec_module(m)
 cfg=m.config(Path(a.repo));verify(a.repo,a.output or cfg.get('output',{}).get('directory','docs/feature-map'))
if __name__=='__main__':run(main)
