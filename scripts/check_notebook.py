#!/usr/bin/env python3
"""Exercise Notebook checkout against real local Git history, without downloads."""
import json
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    nb=json.loads((ROOT/'notebooks/pytorch_starter.ipynb').read_text())
    namespace={}
    exec(''.join(nb['cells'][1]['source']),namespace)
    prepare=namespace['prepare_checkout']
    for invalid in ('','main','not-a-sha'):
        try:prepare(invalid)
        except ValueError:pass
        else:raise AssertionError('Missing/invalid revision silently accepted')
    with tempfile.TemporaryDirectory() as folder:
        base=Path(folder);origin=base/'origin';origin.mkdir()
        def git(*args):return subprocess.check_output(['git','-C',str(origin),*args],text=True).strip()
        git('init','-q');git('config','user.name','Notebook regression');git('config','user.email','test@example.invalid')
        (origin/'marker').write_text('old teaching code');git('add','marker');git('commit','-qm','old')
        old=git('rev-parse','HEAD')
        (origin/'marker').write_text('new teaching code');git('commit','-qam','new')
        clone=base/'checkout'
        subprocess.run(['git','clone','-q','--depth','1',origin.as_uri(),str(clone)],check=True)
        result=prepare(old[:12],clone,origin.as_uri())
        actual=subprocess.check_output(['git','-C',str(result),'rev-parse','HEAD'],text=True).strip()
        assert actual==old and (result/'marker').read_text()=='old teaching code'
        (result/'marker').write_text('reader changes')
        try:prepare(old,clone,origin.as_uri())
        except ValueError:pass
        else:raise AssertionError('Reader modifications would be overwritten')
    print('Notebook QA: invalid commit rejected; shallow checkout runs selected historical SHA; reader edits preserved')
if __name__=='__main__':main()
