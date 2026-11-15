#!/usr/bin/env python3
"""Deterministic offline builder; source interpretation belongs to the Codex Skill."""
import argparse, hashlib, json, re
from common import *

def scrub(value):
 if isinstance(value,dict): return {k:scrub(v) for k,v in value.items()}
 if isinstance(value,list): return [scrub(v) for v in value]
 if isinstance(value,str):
  value=re.sub(r'-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----','[REDACTED PRIVATE KEY]',value,flags=re.S)
  value=re.sub(r'(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*["\']?[^\s,"\';]+',r'\1=[REDACTED]',value)
  value=re.sub(r'\b(?:sk-[A-Za-z0-9_-]{16,}|AKIA[A-Z0-9]{16}|ghp_[A-Za-z0-9]{20,})\b','[REDACTED TOKEN]',value)
  value=re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b','[REDACTED EMAIL]',value)
 return value

def md_safe(text):
 return text.replace('<','&lt;').replace('>','&gt;').replace('[','\\[').replace(']','\\]')

def details(f):
 lines=['# '+f['name'],'',f['purpose'],'']
 for key,label in [('actors','Người dùng'),('preconditions','Điều kiện'),('usageSteps','Cách sử dụng'),('inputs','Đầu vào'),('outputs','Kết quả'),('mainFlow','Luồng chính'),('alternativeFlows','Luồng thay thế'),('exceptionCases','Ngoại lệ')]:
  lines+=['## '+label,'']+(['- '+s for s in f[key]] or [f.get('unknowns',{}).get(key,'Chưa đủ bằng chứng.')])+['']
 lines+=['## Xác minh','',f['verification']['status'],f['verification']['notes']]
 # Rendered only as text in the viewer; neutralize active markup in supplementary files too.
 return md_safe('\n'.join(lines))+'\n'

def merge(workspace):
 tree=read(inside(workspace,'feature-tree.json')); overview=read(inside(workspace,'project-overview.json')); progress=read(inside(workspace,'discovery-progress.json'))
 pending=[id for id,s in progress['nodes'].items() if s['state'] not in ('complete','blocked')]
 if pending: raise ValueError('Unreviewed discovery nodes: '+', '.join(pending))
 features=[]
 ids={node['id'] for node in tree['nodes']}
 if set(progress['nodes'])!=ids:raise ValueError('Progress/tree node set mismatch')
 for surface in progress.get('coverageSurfaces',[]):
  for id in surface.get('mappedIds',[]):
   if id not in ids:raise ValueError('Coverage surface refers to missing node: '+id)
 for node in tree['nodes']:
  f=read(inside(workspace,'features/'+node['id']+'.json'))
  for k in ('id','parentId','kind','name'):
   if f[k]!=node[k]: raise ValueError(f'Tree/detail mismatch: {node["id"]}/{k}')
  if node['id'] not in progress['nodes']: raise ValueError('Missing progress entry: '+node['id'])
  entry=progress['nodes'][node['id']]
  if entry['state']=='blocked' and not entry.get('reason'): raise ValueError('Blocked node needs reason')
  if not entry.get('analysisComplete'): raise ValueError('Deep analysis not completed: '+node['id'])
  features.append(f)
 return dict(schemaVersion='1.0.0',project=overview['project'],generatedAt=overview['generatedAt'],rootId=tree['rootId'],features=features)

def build(repo,data,output='docs/feature-map',word_limit=1200,case_limit=5,progress=None):
 repo=Path(repo).resolve(); out=inside(repo,output)
 data=scrub(validate(data,repo)); data['features'].sort(key=lambda f:f['id']); markdown={}
 for f in data['features']:
  text=details(f)
  complex_=len(f['alternativeFlows'])+len(f['exceptionCases'])>case_limit or len(text.split())>word_limit or len(f['usageSteps'])>12
  if complex_ and not f['documentationPath']: f['documentationPath']='details/'+f['id']+'.md'
  if f['documentationPath']:
   markdown[f['id']]=text
 validate(data,repo)
 # Evidence is maintainer-only; do not bundle paths or claim indexes in ordinary UI.
 public=json.loads(json.dumps(data))
 for f in public['features']: f['verification'].pop('evidence',None);f['verification'].pop('claims',None)
 payload=json.dumps(dict(map=public,markdown=markdown),ensure_ascii=False,sort_keys=True).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
 template=(PACKAGE/'viewer/index.template.html').read_text(); css=(PACKAGE/'viewer/styles.css').read_text(); js='\n'.join((PACKAGE/'viewer'/name).read_text() for name in ['mindmap.js','popup.js'])
 html=template.replace('/*__CSS__*/',css).replace('/*__JS__*/',js).replace('/*__DATA__*/',payload)
 # Check every destination before writing; existing symlinks must never escape the repo.
 for name in ['index.html','feature-map.json','analysis-report.md']:
  inside(repo,output+'/'+name)
 for f in data['features']:
  if f['documentationPath']: inside(repo,output+'/'+f['documentationPath'])
 out.mkdir(parents=True,exist_ok=True)
 for id,text in markdown.items():
  path=inside(out,next(f['documentationPath'] for f in data['features'] if f['id']==id));path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
 write(out/'feature-map.json',data); (out/'index.html').write_text(html,encoding='utf-8')
 statuses={s:sum(f['verification']['status']==s for f in data['features']) for s in ['source_confirmed','inferred','unknown','runtime_observed']}
 report=['# Báo cáo độ bao phủ','',f"Tổng số chức năng: {len(data['features'])}",'',*['- '+k+': '+str(v) for k,v in statuses.items()],'','Đối chiếu source không chứng minh hành vi khi chạy. Không bảo đảm phát hiện đầy đủ cấu hình động hoặc source không truy cập được.','', '## Bằng chứng và điều chưa rõ','']
 for f in data['features']:
  report+=['### '+f['id'],f['verification']['notes']]
  for e in f['verification']['evidence']:report.append(f'- `{e["path"]}`:{e.get("startLine","?")}-{e.get("endLine","?")} — {e["summary"]}')
  for k,v in f.get('unknowns',{}).items():report.append(f'- {k}: {v}')
 if progress:
  report+=['','## Tiến độ và khoảng trống',json.dumps(scrub(progress),ensure_ascii=False,indent=2)]
 (out/'analysis-report.md').write_text(md_safe('\n'.join(report))+'\n',encoding='utf-8')
 return out

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--input');g.add_argument('--workspace');p.add_argument('--output');p.add_argument('--popup-word-limit',type=int);p.add_argument('--case-limit',type=int);a=p.parse_args()
 from importlib.util import spec_from_file_location,module_from_spec
 spec=spec_from_file_location('scanner',PACKAGE/'scripts/scan-project.py');m=module_from_spec(spec);spec.loader.exec_module(m)
 config=m.config(Path(a.repo))
 opts=config.get('output',{}); output=a.output or opts.get('directory','docs/feature-map')
 progress=None
 if a.workspace:
  workspace=inside(a.repo,a.workspace)
  # Source hash comparison is mandatory, even if an agent forgot preflight on resume.
  m.scan(a.repo,a.workspace,verify_only=True,output_override=output)
  data=merge(workspace);progress=read(inside(workspace,'discovery-progress.json'))
  inventory=read(inside(workspace,'source-inventory.json'))
  progress['inventoryGaps']=inventory['gaps'];progress['inventoryExclusions']=inventory['excluded'];progress['detectedStacks']=inventory['detectedStacks']
 else:data=read(a.input)
 out=build(a.repo,data,output,a.popup_word_limit or opts.get('popupWordLimit',1200),a.case_limit if a.case_limit is not None else opts.get('caseLimit',5),progress)
 if a.workspace:
  manifest=read(workspace/'build-manifest.json') if (workspace/'build-manifest.json').exists() else {}
  manifest['outputHashes']={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file()};write(workspace/'build-manifest.json',manifest)
 print('BUILT: '+str(out/'index.html'))
if __name__=='__main__':run(main)
