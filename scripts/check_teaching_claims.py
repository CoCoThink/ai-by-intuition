#!/usr/bin/env python3
"""Recompute published teaching claims and compare them with canonical prose.

This is the numerical counterpart to check_book_contract.py. Keep it after the
NumPy install in CI; source gates deliberately require only the standard library.
"""
from __future__ import annotations
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
import re
import numpy as np
from cache_budget_demo import kv_bytes,run_checks as check_cache
from context_contrast_demo import run_checks as check_context
from attention_selection_demo import run_checks as check_selection
from beginner_training_demo import run_checks as check_beginner
from claude_function_call_demo import run_checks as check_function_call
from icl_policy_demo import run_checks as check_icl_policy
from chinese_tokenizer_demo import run_checks as check_tokenizer
from mini_transformer_demo import run_checks as check_mini
from pretraining_data_demo import run_checks as check_data
from teaching_reference import parameters,forward,backward,LR
from check_agent_loop import run_checks as check_agent_loop

ROOT=Path(__file__).resolve().parents[1]


def check_new_supplements():
    pair_probability=np.exp(2)/(np.exp(2)+1)
    pair_loss=-np.log(pair_probability)
    swapped_loss=-np.log(1-pair_probability)
    vision=(ROOT/'book/chapters/19b-vit.tex').read_text()
    for number in (pair_probability,pair_loss,swapped_loss):
        assert f'{number:.3f}' in vision, number
    assert abs(swapped_loss-pair_loss-2)<1e-12
    calibration=(ROOT/'book/chapters/23d-agent-systems.tex').read_text()
    assert '6/10=0.6' in calibration and abs(.8-6/10-.2)<1e-12
    print('Supplement QA: paired/incorrect CLIP toy losses and confidence-bin calibration arithmetic match prose')


def check_dropout():
    source=(ROOT/'book/chapters/18-generalization.tex').read_text()
    figure=(ROOT/'book/figures/dropout-training-evaluation.tex').read_text()
    values=(2,1,3,4);keep=Fraction(1,2)
    def tex_tuple(row):return '('+','.join(str(int(value)) for value in row)+')'
    assert tex_tuple(values) in source and tex_tuple(values) in figure
    for mask in ((1,0,1,0),(0,1,0,1)):
        masked=tuple(x*m for x,m in zip(values,mask))
        scaled=tuple(x/keep for x in masked)
        assert tex_tuple(masked) in figure and tex_tuple(scaled) in figure
        if mask==(1,0,1,0):
            assert tex_tuple(masked) in source and tex_tuple(scaled) in source
    # All sixteen independent masks are equiprobable, including zero/four kept entries.
    masks=list(product((0,1),repeat=len(values)))
    assert {sum(mask) for mask in masks}==set(range(5))
    means=tuple(sum(Fraction(x)*mask[j]/keep for mask in masks)/len(masks)
                for j,x in enumerate(values))
    assert means==values
    assert '0.5\\times2+0.5\\times0=1' in source
    assert '0.5\\times4+0.5\\times0=2' in source
    print('Dropout QA: both printed masks/scaled outputs, unscaled mean and exact mean over all sixteen masks passed')


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
    check_agent_loop()
    data=json.loads((ROOT/'book/exercises.json').read_text())
    by_legacy={r['legacy_id']:r for r in data if r['legacy_id']}
    byte_answer=kv_bytes(2,2,8,10,2)
    assert re.search(r'\\answerresult\{'+str(byte_answer)+r'\}',by_legacy['C4-41']['solution'])
    cache=check_cache()
    modern=(ROOT/'book/chapters/22d-modern-transformers.tex').read_text().replace('{,}', '')
    assert all(str(value) in modern for value in cache), 'Printed real KV budget differs from pinned configuration'
    c,gradients=check_mini();check_printed_mini(c,gradients)
    check_new_supplements();check_dropout();check_beginner();check_function_call();check_data();check_simplified_gradient(by_legacy['C2-13'])
    local,context=check_context()
    training=(ROOT/'book/chapters/22c-language-training.tex').read_text()
    assert f'{local:.6f}' in training and f'{context:.6f}' in training
    uniform, learned, restored = check_selection()
    selection = training.split(r'\label{experiment:attention-selection}', 1)[1]
    figure = (ROOT/'book/figures/learned-attention-selection.tex').read_text()
    for state in (uniform, learned, restored):
        assert f'{state["loss"]:.6f}' in selection
        assert f'{state["correct_probs"][0]:.6f}' in selection
    for value in learned['weights'][0]:
        assert f'{value:.6f}' in selection, 'Printed selection weight differs from trained Q/K'
        assert f'{value:.6f}' in figure or f'{value:.6f}'.lstrip('0') in figure
    _,_,icl_p,_,_,policy_p=check_icl_policy()
    icl=(ROOT/'book/chapters/23aa-pretraining-icl.tex').read_text()
    post=(ROOT/'book/chapters/23c-post-training.tex').read_text()
    assert f'{icl_p[0]:.6f}' in icl and f'{policy_p[0]:.6f}' in post
    check_tokenizer()
    trained=parameters();a0=forward(trained)['a']
    for _ in range(20):
        st=forward(trained);gr=backward(trained,st)
        for name in trained:trained[name]-=LR*gr[name]
    a20=forward(trained)['a']
    attention_table=training.split('训练前后，Attention 究竟怎样变化？',1)[1].split(r'\subsection{',1)[0]
    for array in (a0,a20):
        for value in array[1:,:][array[1:,:]>0]:assert f'{value:.6f}' in attention_table
    # Attribution of A[3,2]: frozen/only-Q/K and frozen-E/P ablations printed in prose.
    from teaching_trace import NAMES,train,greedy_generate
    for trainable in (tuple(n for n in NAMES if n not in ('Wq','Wk')),('Wq','Wk'),
                      tuple(n for n in NAMES if n not in ('E','P'))):
        value=forward(train(trainable=trainable))['a'][2,1]
        assert f'{value:.6f}' in attention_table,('A32 ablation',trainable,value)
    # Greedy generation with the 20-step weights, KV-cache row and context window.
    generation=(ROOT/'book/chapters/23-llm-systems.tex').read_text()
    ids,trace=greedy_generate(train())
    assert ids==[2,4,5,3] and len(ids)>trained['P'].shape[0]
    for item in trace:
        assert f"{item['prob']:.4f}" in generation,('generation prob',item['prob'])
        assert np.allclose(item['k'][0],trace[0]['k'][0])
    assert all(f'{v:.4f}' in generation for v in trace[-1]['attention'])
    assert all(f'{v:.4f}' in generation for v in trace[0]['k'][0])
    assert np.allclose(trace[-1]['attention'],a20[2])
    w=parameters();state=forward(w);g=backward(w,state)
    updated=forward({k:v-LR*g[k] for k,v in w.items()})
    assert f"{state['loss']:.6f}" in training
    assert f"{updated['loss']:.6f}" in training
    assert abs(g['Wout'][0,3]+.8595)<.00005
    assert abs(state['probs'][0,3]-.2617)<.00005
    print('Published numeric claims passed: byte units, rational reverse pass, context ablation, 3D baseline unchanged')


if __name__=='__main__':main()
