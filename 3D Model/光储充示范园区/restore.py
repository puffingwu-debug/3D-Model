#!/usr/bin/env python3
"""Check and restore the complete project using Python 3 standard libraries."""
from pathlib import Path
import hashlib,json,sys,zipfile
BASE=Path(__file__).resolve().parent
manifest=json.loads((BASE/'MANIFEST.json').read_text(encoding='utf-8'))
target=BASE/manifest['archive']
if target.exists():
 if hashlib.sha256(target.read_bytes()).hexdigest()!=manifest['sha256']:
  raise SystemExit('Existing ZIP has a different checksum; move it aside before restoring.')
else:
 for part in manifest['parts']:
  p=BASE/part['file']
  if not p.is_file() or p.stat().st_size!=part['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=part['sha256']:
   raise SystemExit('Missing or damaged part: '+part['file'])
 temp=target.with_suffix('.assembling')
 with temp.open('wb') as out:
  for part in manifest['parts']:
   with (BASE/part['file']).open('rb') as source:
    while block:=source.read(1024*1024):out.write(block)
 if hashlib.sha256(temp.read_bytes()).hexdigest()!=manifest['sha256']:raise SystemExit('Archive checksum mismatch.')
 temp.rename(target)
with zipfile.ZipFile(target) as z:
 if z.testzip() is not None:raise SystemExit('ZIP CRC check failed.')
 if '--verify-only' not in sys.argv:
  folder=BASE/manifest['root']
  if folder.exists():raise SystemExit('Project directory already exists. ZIP verified; existing files were preserved.')
  for name in z.namelist():
   if not (BASE/name).resolve().is_relative_to(BASE):raise SystemExit('Unsafe archive path.')
  z.extractall(BASE)
  (folder/'启动预览.command').chmod(0o755)
print('SHA-256 and ZIP verification passed.' if '--verify-only' in sys.argv else 'Project restored: '+str(folder))
