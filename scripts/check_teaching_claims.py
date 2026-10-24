#!/usr/bin/env python3
"""Recompute published teaching claims and compare them with canonical prose.

This is the numerical counterpart to check_book_contract.py. Keep it after the
NumPy install in CI; source gates deliberately require only the standard library.
"""
from __future__ import annotations
import json
from fractions import Fraction
from pathlib import Path
import re
import numpy as np
from cache_budget_demo import kv_bytes,run_checks as check_cache
from context_contrast_demo import run_checks as check_context
from mini_transformer_demo import run_checks as check_mini
from pretraining_data_demo import run_checks as check_data
from teaching_reference import parameters,forward,backward,LR

ROOT=Path(__file__).resolve().parents[1]


def check_simplified_gradient(item):
    a=np.array([.330,.670]);x=np.array([0.,1.]);wv=np.eye(2);wd=.5*np.eye(2)
    gh=np.array([.09716,.72516])
    def objective():
        r=x+a@wv;h=r+np.maximum(r,0)@wd
        return float(h@gh)
    gr=gh@(np.eye(2)+wd.T)
    expected={'Wdown':np.outer(x+a@wv,gh),'Wv':np.outer(a,gr)}
    for name,array in [('Wdown',wd),('Wv',wv)]:
        gradient=expected[name]
        for index in np.ndindex(array.shape):
            old=array[index];eps=1e-6
            array[index]=old+eps;hi=objective()
            array[index]=old-eps;lo=objective()
            array[index]=old
            assert abs((hi-lo)/(2*eps)-gradient[index])<1e-8,(name,index)
        for number in gradient.flat:
            assert f'{number:.5f}' in item['solution'],(name,number)
    print('Former C2-13: explicit simplified Block, all 8 parameter derivatives match published matrices')


def check_printed_mini(c, gradients):
    text=(ROOT/'book/chapters/00f-transformer-intermediates.tex').read_text()
    text=text.split(r'\label{app:rational-mini}',1)[1].split(r'\subsection{',1)[0]
    printed=[]
    for body in re.findall(r'\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}',text,re.S):
        printed.append(np.array([[float(Fraction(cell.strip())) for cell in row.split('&')]
                                 for row in body.split(r'\\')]))
    expected=[c['w']['Wq'],c['w']['Wk'],c['w']['Wout'],
              gradients['Wout'],gradients['Wdown'],gradients['Wo']]
    assert len(printed)==len(expected), 'Mini example printed matrix inventory changed'
    for published,computed in zip(printed,expected):
        assert published.shape==computed.shape and np.allclose(published,computed), (published,computed)
    print('Rational mini Block: all six printed parameter/gradient matrices match the computation')


def main():
    data=json.loads((ROOT/'book/exercises.json').read_text())
    by_legacy={r['legacy_id']:r for r in data if r['legacy_id']}
    byte_answer=kv_bytes(2,2,8,10,2)
    assert re.search(r'\\answerresult\{'+str(byte_answer)+r'\}',by_legacy['C4-41']['solution'])
    cache=check_cache()
    modern=(ROOT/'book/chapters/22d-modern-transformers.tex').read_text().replace('{,}', '')
    assert all(str(value) in modern for value in cache), 'Printed real KV budget differs from pinned configuration'
    c,gradients=check_mini();check_printed_mini(c,gradients)
    check_data();check_simplified_gradient(by_legacy['C2-13'])
    local,context=check_context()
    training=(ROOT/'book/chapters/22c-language-training.tex').read_text()
    assert f'{local:.6f}' in training and f'{context:.6f}' in training
    w=parameters();state=forward(w);g=backward(w,state)
    updated=forward({k:v-LR*g[k] for k,v in w.items()})
    assert f"{state['loss']:.6f}" in training
    assert f"{updated['loss']:.6f}" in training
    assert abs(g['Wout'][0,3]+.8595)<.00005
    assert abs(state['probs'][0,3]-.2617)<.00005
    print('Published numeric claims passed: byte units, rational reverse pass, context ablation, 3D baseline unchanged')


if __name__=='__main__':main()
