#!/usr/bin/env python3
"""Inventory source metadata without printing source contents. Hashes support safe resume."""
import argparse, hashlib, os
from common import *
DEFAULT_EXCLUDES=['.git','node_modules','vendor','dist','build','Library','Temp','__pycache__','.venv','venv','.next','coverage']
SECRET_NAMES={'.env','.npmrc','.pypirc','.netrc','credentials','credentials.json','secrets.json','id_rsa','id_ed25519'}
def secret(path):
 n=path.name.lower()
 return n in SECRET_NAMES or n.startswith('.env.') or n.endswith(('.pem','.key','.p12','.pfx','.keystore','.sqlite','.db','.csv','.sql')) or any(x in n for x in ('credentials','secret','customer-data'))
def config(repo):
 yamlpath=repo/'feature-map.config.yaml';jsonpath=repo/'feature-map.config.json'
 if yamlpath.is_symlink() or jsonpath.is_symlink():raise ValueError('Config symlinks are not allowed')
 if yamlpath.exists():
  import yaml
  c=yaml.safe_load(yamlpath.read_text(encoding='utf-8')) or {}
 elif jsonpath.exists():c=read(jsonpath)
 else:c={}
 if c.get('analysis',{}).get('mode','single-agent')!='single-agent':raise ValueError('Only single-agent analysis is supported')
 if c.get('analysis',{}).get('strategy','breadth-first-then-deep')!='breadth-first-then-deep':raise ValueError('Only breadth-first-then-deep strategy is supported')
 opts=c.get('output',{})
 for key in ['selfContainedHtml','popup','markdownForComplexFeatures']:
  if opts.get(key,True) is not True:raise ValueError(key+' must remain true in V1')
 if opts.get('language','vi')!='vi':raise ValueError('V1 end-user output language is vi')
 return c

def classify(path):
 s=str(path).lower();name=path.name.lower()
 if name in ['package.json','composer.json','pyproject.toml','cargo.toml','go.mod','manifest.json','projectversion.txt']:return 'manifest'
 for keys,kind in [(('test','spec'),'test'),(('route','urls.py'),'routing'),(('menu','navigation','sidebar'),'navigation'),(('auth','permission','policy','role'),'authorization'),(('readme','docs/','.md'),'documentation'),(('controller','service','domain','model'),'domain'),(('view','screen','page','.tsx','.vue'),'ui')]:
  if any(k in s for k in keys):return kind
 return 'source'

def detect_stack(repo):
 markers={'unity':['ProjectSettings/ProjectVersion.txt'],'node':['package.json'],'php':['composer.json'],'python':['pyproject.toml','requirements.txt'],'rust':['Cargo.toml'],'go':['go.mod']}
 return [stack for stack,paths in markers.items() if any((repo/path).is_file() for path in paths)]

def scan(repo,workspace='.feature-map-workspace',verify_only=False,output_override=None):
 repo=Path(repo).resolve();cfg=config(repo);ws=inside(repo,workspace);out=inside(repo,output_override or cfg.get('output',{}).get('directory','docs/feature-map'))
 stacks=detect_stack(repo)
 defaults=[x for x in DEFAULT_EXCLUDES if x not in ('Library','Temp') or 'unity' in stacks]
 ex=set(cfg.get('exclude',defaults));limit=cfg.get('analysis',{}).get('maxSourceFileBytes',250000);records=[];gaps=[];excluded={}
 def walk_error(e):gaps.append({'path':str(e.filename).replace(str(repo)+'/',''),'reason':'inaccessible directory'})
 for base,dirs,files in os.walk(repo,followlinks=False,onerror=walk_error):
  keep=[]
  for name in sorted(dirs):
   path=Path(base)/name;relative=path.relative_to(repo).as_posix()
   if path.is_symlink() or name in ex or relative in ex or path==ws or path==out or name=='.agents':excluded[name]=excluded.get(name,0)+1
   else:keep.append(name)
  dirs[:]=keep
  for name in sorted(files):
   path=Path(base)/name;rel=path.relative_to(repo).as_posix()
   if path.is_symlink() or secret(path):gaps.append({'path':rel,'reason':'sensitive or symlink: not read'});continue
   try:
    size=path.stat().st_size;r={'path':rel,'bytes':size,'classification':classify(path.relative_to(repo))}
    if size>limit:r['metadataOnly']=True;gaps.append({'path':rel,'reason':'exceeds maxSourceFileBytes'})
    else:
     raw=path.read_bytes()
     try:text=raw.decode('utf-8');binary='\x00' in text
     except UnicodeError:binary=True
     r['metadataOnly']=binary
     if not binary:r['sha256']=hashlib.sha256(raw).hexdigest();r['lines']=len(text.splitlines())
     else:gaps.append({'path':rel,'reason':'binary: metadata only'})
    records.append(r)
   except OSError:gaps.append({'path':rel,'reason':'inaccessible file'})
 old=read(inside(ws,'build-manifest.json')) if (ws/'build-manifest.json').exists() else {}; hashes={r['path']:r.get('sha256','metadata:'+str(r['bytes'])) for r in records};changed=sorted(k for k in old.get('sourceHashes',{}) .keys()|hashes.keys() if old.get('sourceHashes',{}).get(k)!=hashes.get(k))
 if (ws/'discovery-progress.json').exists():
  progress=read(inside(ws,'discovery-progress.json'))
  if changed or (not verify_only and cfg.get('analysis',{}).get('resume',True) is False):
   # Conservative invalidation: correctness over speculative dependency inference.
   for entry in progress['nodes'].values():entry.update(state='pending',analysisComplete=False,reason='Source inventory changed; review required')
   progress['phase']='discovery';progress['changedSources']=changed;write(ws/'discovery-progress.json',progress)
 else:write(ws/'discovery-progress.json',{'phase':'overview','nodes':{},'coverageGaps':gaps})
 write(ws/'source-inventory.json',{'files':records,'excluded':excluded,'gaps':gaps,'config':cfg,'detectedStacks':stacks})
 write(ws/'build-manifest.json',{'schemaVersion':'1.0.0','sourceHashes':hashes,'changedSources':changed,'resumeAvailable':bool(old)})
 print(f'INVENTORY: {len(records)} files; {len(gaps)} gaps; {len(changed)} new/changed/deleted paths; workspace={ws}')
 return ws

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True);p.add_argument('--workspace',default='.feature-map-workspace');a=p.parse_args();scan(a.repo,a.workspace)
if __name__=='__main__':run(main)
