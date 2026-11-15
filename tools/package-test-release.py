"""Export a pinned, self-contained Pages test directory without altering production.
Example: python3 tools/package-test-release.py --version 0.15 --pr 2 --output /path/to/test-repo/v0.15
Existing output directories are never overwritten. No private references are read.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--version',required=True);parser.add_argument('--pr',type=int);parser.add_argument('--commit',default='HEAD');parser.add_argument('--output',required=True)
args=parser.parse_args();root=Path(__file__).resolve().parents[1];destination=Path(args.output)
if destination.exists():raise SystemExit('Output already exists; published test versions are preserved.')
sha=subprocess.check_output(['git','rev-parse',args.commit],cwd=root,text=True).strip()
def read(path):return subprocess.check_output(['git','show',f'{sha}:{path}'],cwd=root)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',sha],cwd=root,text=True).splitlines()
files={p:read(p)for p in paths if p.startswith(('src/','vendor/','assets/','data/'))}
for name in ['osm-3d-preview.html','character-studio.html']:
    html=read(name).decode().replace(f'· v{args.version}</span>',f'· v{args.version} · TESTVERSION</span>')
    html=html.replace('Die Ausflüge bleiben im <a href="./index.html">bisherigen Spiel</a> verfügbar.','Ausflugsmissionen sind in diesem Testabschnitt noch nicht enthalten.')
    files[name]=html.encode()
files['index.html']=files['osm-3d-preview.html']
for path,data in files.items():
    p=destination/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
manifest={'version':args.version,'source_repository':'simesimon1/sondervig-adventure-2026','source_pull_request':args.pr,'source_commit':sha,'published_path':f'/v{args.version}/','packaging_changes':['HTML index alias and test label','Standalone help text'],'files':{p:hashlib.sha256(data).hexdigest()for p,data in sorted(files.items())}}
(destination/'build-info.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'output':str(destination),'source_commit':sha,'files':len(files),'bytes':sum(len(d)for d in files.values())}))
