"""Shared validation and safe repository paths. Python 3.10+."""
import hashlib, json, re
from pathlib import Path, PurePosixPath
from jsonschema import Draft202012Validator, FormatChecker
PACKAGE=Path(__file__).resolve().parents[1]
FIELDS=['actors','preconditions','usageSteps','inputs','outputs','mainFlow','alternativeFlows','exceptionCases','relatedFeatureIds']
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,data):
 p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); tmp=p.with_suffix(p.suffix+'.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); tmp.replace(p)
def safe_relative(value):
 return isinstance(value,str) and bool(value) and not re.search(r'[\\:\x00-\x1f?#%]',value) and not PurePosixPath(value).is_absolute() and all(x not in ('..','.') for x in value.split('/')) and '' not in value.split('/')
def inside(root,relative):
 if not safe_relative(relative): raise ValueError('Unsafe relative path: '+str(relative))
 root=Path(root).resolve(); p=(root/relative).resolve()
 if not p.is_relative_to(root): raise ValueError('Path escapes repository: '+relative)
 return p
def stable_id(key): return 'f-'+hashlib.sha256(key.encode()).hexdigest()[:16]
def validate(data,repo=None):
 errors=[f'{"/".join(map(str,e.absolute_path))}: {e.message}' for e in Draft202012Validator(read(PACKAGE/'schemas/feature-map.schema.json'),format_checker=FormatChecker()).iter_errors(data)]
 if errors: raise ValueError('\n'.join(errors))
 fs=data['features']; by={f['id']:f for f in fs}
 if len(by)!=len(fs): errors.append('Duplicate feature IDs')
 docs=[f['documentationPath'] for f in fs if f['documentationPath']]
 if len(docs)!=len(set(docs)): errors.append('Duplicate documentation paths')
 roots=[f for f in fs if f['parentId'] is None]
 if len(roots)!=1 or roots[0]['id']!=data['rootId']: errors.append('Exactly one root matching rootId required')
 for f in fs:
  id=f['id']
  if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]*',id): errors.append(f'{id}: unsafe ID')
  if (f['kind']=='system') != (f['parentId'] is None): errors.append(f'{id}: only root can be system')
  seen={id}; parent=f['parentId']
  while parent is not None:
   if parent not in by: errors.append(f'{id}: missing parent {parent}'); break
   if parent in seen: errors.append(f'{id}: parent cycle'); break
   seen.add(parent); parent=by[parent]['parentId']
  for r in f['relatedFeatureIds']:
   if r not in by: errors.append(f'{id}: broken related reference {r}')
  doc=f['documentationPath']
  if doc and (not safe_relative(doc) or not doc.startswith('details/') or not doc.endswith('.md')): errors.append(f'{id}: unsafe documentation path')
  v=f['verification']; ev=v['evidence']
  if v['status']=='runtime_observed' and not v['runtimeObserved']: errors.append(f'{id}: runtime observation required')
  if v['runtimeObserved'] and v['status']!='runtime_observed': errors.append(f'{id}: inconsistent runtime status')
  if v['status'] in ('source_confirmed','runtime_observed'):
   if not ev: errors.append(f'{id}: confirmed claim requires evidence')
   for field in ['purpose','actors']+FIELDS:
    if field!='relatedFeatureIds' and f.get(field) and not v.get('claims',{}).get(field): errors.append(f'{id}: missing claim evidence mapping for {field}')
  for field in FIELDS:
   if field!='relatedFeatureIds' and not f[field] and not f.get('unknowns',{}).get(field): errors.append(f'{id}: empty {field} needs unknown reason')
  for field,indices in v.get('claims',{}).items():
   if field not in f or not indices or any(i>=len(ev) for i in indices): errors.append(f'{id}: invalid claim evidence {field}')
  for e in ev:
   if not safe_relative(e['path']): errors.append(f'{id}: unsafe evidence path')
   if e.get('endLine',e.get('startLine',1)) < e.get('startLine',1): errors.append(f'{id}: invalid evidence range')
   if repo:
    try:
     path=inside(repo,e['path'])
     if not path.is_file(): errors.append(f'{id}: missing evidence {e["path"]}')
     elif e.get('endLine',e.get('startLine',1))>len(path.read_text(encoding='utf-8').splitlines()): errors.append(f'{id}: evidence line out of range')
    except (ValueError,UnicodeError) as ex: errors.append(str(ex))
 if errors: raise ValueError('\n'.join(errors))
 return data

def run(fn):
 try: fn()
 except (ValueError,OSError,KeyError,TypeError) as e:
  import sys
  print('ERROR: '+str(e),file=sys.stderr); sys.exit(1)
