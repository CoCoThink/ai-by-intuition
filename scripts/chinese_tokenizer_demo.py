#!/usr/bin/env python3
"""Verify the archived Chinese tokenization; --real executes the pinned tokenizer."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/'scripts/fixtures/qwen25_tokenizer_trace.json'

def run_checks(real=False,tokenizer_file=None):
    r=json.loads(RECORD.read_text())
    assert len(r['revision'])==40 and r['revision'] in r['source'] and '/resolve/' in r['source']
    assert r['add_special_tokens'] is False and ''.join(r['pieces'])==r['text']
    assert len(r['ids'])==len(r['pieces']) and all(isinstance(i,int) and i>=0 for i in r['ids'])
    if real:
        from tokenizers import Tokenizer
        raw=Path(tokenizer_file).read_bytes() if tokenizer_file else urlopen(r['source'],timeout=60).read()
        assert hashlib.sha256(raw).hexdigest()==r['sha256'],'Pinned tokenizer content changed'
        t=Tokenizer.from_str(raw.decode());e=t.encode(r['text'],add_special_tokens=False)
        assert e.ids==r['ids'] and [t.decode([i]) for i in e.ids]==r['pieces']
        assert t.decode(e.ids)==r['text']
        short=t.encode(r['text'].removesuffix('。'),add_special_tokens=False)
        assert short.ids==r['ids'][:-1] and t.decode(short.ids)=='春天花开了'
    text=(ROOT/'book/chapters/20a-tokenizer.tex').read_text()
    table=text.split(r'\label{experiment:real-chinese-tokenizer}',1)[1].split(r'\end{tabular}',1)[0]
    for piece,identifier in zip(r['pieces'],r['ids']):assert f'{piece} & {identifier}' in table
    scale=(ROOT/'book/chapters/23a-from-toy-to-gpt.tex').read_text()
    assert r'\hyperref[experiment:real-chinese-tokenizer]' in scale
    notes=(ROOT/'book/chapters/29-revision-notes.tex').read_text()
    assert r['revision'] in notes
    print(('Pinned tokenizer execution' if real else 'Archived tokenization/prose')+' QA passed: '+str(r['ids']))
    return r
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--real',action='store_true');p.add_argument('--tokenizer-file');a=p.parse_args();run_checks(a.real,a.tokenizer_file)
