#!/usr/bin/env python3
"""Regress concrete reading-order failures and the examples readers can verify.

Called by check_book_contract, including its negative-fixture self-tests. These
checks guard specific prerequisites and worked calculations, not prose quality.
"""
from __future__ import annotations
import math
import re
import numpy as np
from check_section_navigation import reading_ranges
from teaching_reference import parameters, softmax


def ordered_content_errors(body, steps):
    """Match actual examples/formulas: a surviving label alone is insufficient."""
    positions=[]
    for name,pattern in steps:
        match=re.search(pattern,body,re.S)
        if match is None:
            return [f'Missing worked step: {name}']
        positions.append(match.start())
    return [] if positions==sorted(set(positions)) else [
        'Teach worked steps in this order: '+', '.join(name for name,_ in steps)]


def bpe_comparison_errors(body):
    """Keep the four-way tokenizer tradeoff table present and complete."""
    table=re.search(r'\\begin\{tabularx\}\{\\linewidth\}.*?\\end\{tabularx\}',body,re.S)
    if table is None:
        return ['Missing BPE tokenizer comparison table']
    return ordered_content_errors(table[0],[
        ('table header',r'切分单位 & 词表大小 & 序列长度 & 遇到没见过的词'),
        ('character row',r'逐字 & 较小 & 较长 & 未收录字符需要未知符号或其他回退方式'),
        ('byte row',r'逐字节 & 256 个基础字节 & 较长 & 覆盖全部字节时'),
        ('whole-word row',r'整词 & 极大 & 短 & 未收录词需要未知符号或其他回退方式'),
        ('subword row',r'子词（BPE） & 基础表加合并项 & 居中 & 退回已覆盖的基础片段；覆盖取决于基础表'),
    ])


def token_task_errors(body):
    """Keep training's parallel rows distinct from generation's final row."""
    return ordered_content_errors(body,[
        ('generation uses final row',
         r'生成时只取\\textbf\{提示末尾对应的最后一行\}'),
        ('training row 1 predicts ID 4',
         r'1 & 春天（\$\[2\]\$） & 花（ID \$4\$）'),
        ('training row 2 predicts ID 5',
         r'2 & 春天、花（\$\[2,4\]\$） & 开了（ID \$5\$）'),
        ('training row 3 predicts ID 3 after ID 5',
         r'3 & 春天、花、开了（\$\[2,4,5\]\$） & 。\\quad（ID \$3\$）'),
        ('paired input and target IDs',
         r'\\underbrace\{\[2,\\ 4,\\ 5\]\}.*?\\underbrace\{\[4,\\ 5,\\ 3\]\}'),
        ('three-position score matrix',r'3\\times5'),
        ('causal mask limits each row to its prefix',
         r'因果遮罩让第~1 行只读第~1 个位置，第~2 行读前两个位置，第~3 行读全部三个位置'),
    ])


def route_prerequisite_errors(main, sources, dependencies):
    """Use source spans, not PDF pages: skipped chapters may share a page."""
    positions={};ends={};offset=0
    for name in re.findall(r'\\input\{chapters/([^}]+)\}',main):
        body=sources[name]
        for match in re.finditer(r'\\label\{([^}]+)\}',body):
            positions[match[1]]=offset+match.start()
            ends[match[1]]=offset+len(body.rstrip())
        offset+=len(body)+1
    errors=[]
    for route,pairs in reading_ranges(sources['front-reading-routes']).items():
        if any(label not in positions for pair in pairs for label in pair):
            errors.append(f'{route}: missing reading-range destination')
            continue
        spans=[(positions[start],positions[end]) for start,end in pairs]
        def selected(label):
            # A route may start at an alias after the chapter's intro label.
            # Any selected content in that chapter still needs its prerequisites.
            return label in positions and any(a<ends[label] and positions[label]<b
                                              for a,b in spans)
        for prerequisite,consumer in dependencies:
            if selected(consumer) and not (prerequisite in positions and any(
                    a<=positions[prerequisite] and ends[prerequisite]<=b for a,b in spans)):
                errors.append(f'{route}: {consumer} requires the full {prerequisite} chapter')
    return errors


def matrix_after(body, marker):
    """Read the displayed numeric matrix, not a second hard-coded answer."""
    tail=body.split(marker,1)[1]
    match=re.search(r'\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}',tail,re.S)
    if match is None:
        raise ValueError(f'Missing numeric matrix after {marker}')
    return np.array([[float(cell.strip()) for cell in row.split('&')]
                     for row in re.split(r'\\\\',match[1].strip())])


def position_example_errors(body):
    try:
        weights=parameters()
        x=weights['E'][[1,3]]
        for key,marker in [('Wq','W_Q='),('Wk','W_K='),('Wv','W_V=')]:
            np.testing.assert_allclose(matrix_after(body,marker),weights[key],atol=0,rtol=0)
        pos=matrix_after(body,r'{P_{\rm pos}}_{1:2}=')
        np.testing.assert_allclose(pos,weights['P'][:2],atol=0,rtol=0)
        def read(value):
            return softmax((value@weights['Wq'])@(value@weights['Wk']).T/math.sqrt(3))@(value@weights['Wv'])
        np.testing.assert_allclose(read(x[::-1]),read(x)[::-1],atol=1e-14,rtol=0)
        assert not np.allclose(read(x[::-1]+pos),read(x+pos)[::-1])
        for marker,value in [('O(X)=',x),('O(X_+)\\approx',x+pos),("O(X'_+)\\approx",x[::-1]+pos)]:
            np.testing.assert_allclose(matrix_after(body,marker),read(value),atol=5.01e-5,rtol=0)
    except (AssertionError,ValueError,IndexError,TypeError) as error:
        return [f'Position swap example disagrees with canonical parameters or rounding: {error}']
    return []


def scaling_example_errors(body):
    try:
        example=body.split(r'\subsection{缩放分数会怎样改变读取？}',1)[1].split(r'\subsection',1)[0]
        pairs=re.findall(r'\$\(([\d.]+),([\d.]+)\)\$',example)
        raw,scaled=(np.array(pair,dtype=float) for pair in pairs)
        dim,divisor=re.search(r'\\sqrt\{(\d+)\}=([\d.]+)',example).groups()
        assert math.isclose(float(divisor),math.sqrt(int(dim)))
        np.testing.assert_allclose(raw/float(divisor),scaled,atol=0,rtol=0)
        printed=[float(value) for value in re.findall(r'\$([01]\.\d+)\$',example)]
        for probability,value in zip(printed,[raw,scaled],strict=True):
            digits=len(str(probability).split('.')[1])
            assert abs(probability-softmax(value)[0])<=.501*10**(-digits)
    except (AssertionError,ValueError,IndexError,AttributeError) as error:
        return [f'Scaling example scores, dimension and displayed probabilities disagree: {error}']
    return []


def validate_pedagogy(main, sources):
    errors=route_prerequisite_errors(main,sources,[
        ('intro:language-model-task','intro:classification-loss'),
        ('intro:context-gap','intro:attention-qkv')])
    errors.extend(f'09-tokenization: {error}'
                  for error in bpe_comparison_errors(sources['09-tokenization']))
    errors.extend(f'10-language-model-task: {error}'
                  for error in token_task_errors(sources['10-language-model-task']))
    sequences={
        '09-tokenization': [
            ('merge example',r'\[\\text\{今天\},\\text\{天气\},\\text\{好\}\]'),
            ('BPE definition',r'\\textbf\{BPE（'),
            ('vocabulary/sequence tradeoff',r'\\textbf\{词表大小与序列长度\}')],
        '11-classification-loss': [
            ('probability comparison',r'预测 A & \$0\.30\$'),
            ('logits definition',r'\\label\{concept:logits\}'),
            ('Softmax formula',r'\\boxed\{p_j=\\frac\{e\^\{z_j\}'),
            ('cross-entropy formula',r'L=-\\sum_\{j=1\}\^\{C\}y_j\\ln p_j')],
        '15-self-attention': [
            ('scaling example',r'\$\(8,0\)\$'),
            ('general attention formula',r'\\operatorname\{Attention\}\(Q,K,V\)')],
        '25-rag': [
            ('retrieval and evidence example',r'100,120,132'),
            ('Prompt and Context definitions',r'\\label\{concept:prompt\}')],
        '26-tool-use-and-agents': [
            ('message trace',r'回合 & 消息角色'),
            ('loop diagram',r'\\label\{fig:agent-loop\}'),
            ('loop pseudocode',r'for step in range\(MAX_STEPS\)')],
    }
    for name,steps in sequences.items():
        errors.extend(f'{name}: {error}' for error in ordered_content_errors(sources[name],steps))
    errors+=position_example_errors(sources['16-position-and-multihead'])
    errors+=scaling_example_errors(sources['15-self-attention'])
    return errors


def self_test():
    assert not ordered_content_errors('example formula',[('example','example'),('formula','formula')])
    assert ordered_content_errors('formula example',[('example','example'),('formula','formula')])
    assert ordered_content_errors(r'\label{example} formula',[('example','worked example'),('formula','formula')])
    main=''.join(r'\input{chapters/'+name+'}' for name in ('prereq','consumer','front-reading-routes'))
    sources={'prereq':r'\label{pre} actual explanation',
             'consumer':r'\label{use} depends on explanation \label{end}',
             'front-reading-routes':r'\setroutebudget{hands}{pre/end}'}
    assert not route_prerequisite_errors(main,sources,[('pre','use')])
    # All destinations still exist, yet the prerequisite was skipped.
    sources['front-reading-routes']=r'\setroutebudget{hands}{use/end}'
    assert route_prerequisite_errors(main,sources,[('pre','use')])
    sources['consumer']=r'\label{use}\label{alias} depends on explanation \label{end}'
    sources['front-reading-routes']=r'\setroutebudget{hands}{alias/end}'
    assert route_prerequisite_errors(main,sources,[('pre','use')])
    sources['prereq']=r'\label{pre}\label{cut} explanation after cut'
    sources['front-reading-routes']=r'\setroutebudget{hands}{pre/cut,use/end}'
    assert route_prerequisite_errors(main,sources,[('pre','use')])
    bpe_table=r'''\begin{tabularx}{\linewidth}{X}
切分单位 & 词表大小 & 序列长度 & 遇到没见过的词\\
逐字 & 较小 & 较长 & 未收录字符需要未知符号或其他回退方式\\
逐字节 & 256 个基础字节 & 较长 & 覆盖全部字节时\\
整词 & 极大 & 短 & 未收录词需要未知符号或其他回退方式\\
子词（BPE） & 基础表加合并项 & 居中 & 退回已覆盖的基础片段；覆盖取决于基础表\\
\end{tabularx}'''
    assert not bpe_comparison_errors(bpe_table)
    assert bpe_comparison_errors(bpe_table.replace('逐字节 & 256 个基础字节','逐字节 & 128 个基础字节'))
    # Break the printed result while keeping all labels and prose intact.
    from pathlib import Path
    chapters=Path(__file__).resolve().parents[1]/'book/chapters'
    task=(chapters/'10-language-model-task.tex').read_text()
    assert not token_task_errors(task)
    assert token_task_errors(task.replace(
        r'生成时只取\textbf{提示末尾对应的最后一行}',r'生成时使用三行'))
    positions=(chapters/'16-position-and-multihead.tex').read_text()
    assert not position_example_errors(positions)
    assert position_example_errors(positions.replace('0.2812&0.7145','0.2324&0.6726'))
    scale=(chapters/'15-self-attention.tex').read_text()
    assert not scaling_example_errors(scale)
    assert scaling_example_errors(scale.replace('0.9997','0.7310'))
    assert scaling_example_errors(scale.replace(r'\sqrt{64}=8',r'\sqrt{64}=4'))


if __name__=='__main__':
    from check_book_contract import read_sources
    self_test()
    errors=validate_pedagogy(*read_sources())
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Pedagogy regressions passed: source prerequisites, worked-step order, scaling and position calculations')
