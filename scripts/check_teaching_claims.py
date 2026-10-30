#!/usr/bin/env python3
"""Recompute published teaching claims and compare them with canonical prose.

This is the numerical counterpart to check_book_contract.py. Install the declared
book dependencies before running either source contracts or numerical checks.
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
from memory_demo import main as check_memory

ROOT=Path(__file__).resolve().parents[1]


def check_article_matching():
    """Recompute the printed ranking, scaling counterexample and plotted projection."""
    vectors=(ROOT/'book/chapters/01-vectors.tex').read_text()
    source=(ROOT/'book/chapters/02-dot-product.tex').read_text()
    rows=re.findall(r'\$\\vect ([qabc])\^\\top\$ & \$([\d.]+)\$ & \$([\d.]+)\$',vectors)
    data={name:np.array([float(x),float(y)]) for name,x,y in rows}
    assert set(data)==set('qabc'), 'Missing article feature-table rows'
    scores={name:float(data['q']@data[name]) for name in 'abc'}
    printed=re.findall(r'^([ABC]) & \$([^$]+)\$ & \$([\d.]+)\$',source,re.M)
    assert len(printed)==3
    for name,expression,result in printed:
        expression=expression.replace(r'\times','*')
        assert re.fullmatch(r'[\d.*+]+',expression)
        evaluated=eval(expression,{'__builtins__':{}},{})
        assert np.isclose(evaluated,scores[name.lower()])
        assert np.isclose(float(result),evaluated), (name,result,evaluated)
    assert sorted(scores,key=scores.get,reverse=True)==list('acb')
    assert all(np.isclose(np.linalg.norm(row),1) for row in data.values())
    scaled=3*data['b'];raw=float(data['q']@scaled)
    cosine=raw/(np.linalg.norm(data['q'])*np.linalg.norm(scaled))
    assert raw>scores['a'] and f'={raw:g}.' in source
    assert np.isclose(cosine,scores['b'])
    def coordinates(name):
        figure=(ROOT/'book/figures'/name).read_text()
        return {key:np.array([float(x),float(y)]) for key,x,y in
                re.findall(r'\\coordinate \((\w+)\) at \(([\d.]+),([\d.]+)\)',figure)}
    plotted=coordinates('article-match-vectors.tex')
    assert set(plotted)==set(data)
    for name,row in data.items():assert np.allclose(plotted[name],row),name
    length=coordinates('dot-product-length.tex')
    for name in ('q','b'):assert np.allclose(length[name],data[name])
    assert np.allclose(length['scaled'],scaled)
    assert np.allclose(length['unitq'],data['q']/np.linalg.norm(data['q']))
    assert np.allclose(length['unitb'],scaled/np.linalg.norm(scaled))
    projection=coordinates('dot-product-projection.tex')
    for name in ('q','a'):assert np.allclose(projection[name],data[name])
    foot=(data['a']@data['q'])/(data['q']@data['q'])*data['q']
    assert np.allclose(projection['p'],foot), 'Projection foot differs from printed vectors'
    assert np.isclose(np.linalg.norm(foot),scores['a'])
    assert np.isclose((data['a']-foot)@data['q'],0)
    exercises={item['id']:item for item in json.loads((ROOT/'book/exercises.json').read_text())}
    # Check the notation at its first definition, not merely its numerical value.
    # The old row-dot-row formula was valid but differed from every later q^T k.
    figure=(ROOT/'book/figures/dot-product-projection.tex').read_text()
    for body in (source,figure,exercises['C-017']['question'],exercises['C-017']['solution'],exercises['C-018']['solution']):
        assert not re.search(r'\\vect [a-z]\^\\top\\cdot',body), 'Use the same row-column dot-product notation from its first definition'
        assert not re.search(r'\\\|[^\n]*?\^\\top[^\n]*?\\\|',body), 'Vector lengths must use the common norm notation'
    assert r'\boxed{\vect a^\top\vect b=a_1b_1+a_2b_2.}' in source
    assert r'\vect b=\begin{bmatrix}b_1\\b_2\end{bmatrix}' in source
    assert r'\boxed{\|\vect a\|=\sqrt{a_1^2+a_2^2}.}' in source
    changed=data['q'][::-1]
    assert all(f'{{{changed@data[name]:g}}}' in exercises['C-018']['solution'] for name in 'abc')
    assert f'{{{(5*data["q"])@(5*data["a"]):g}}}' in exercises['C-019']['solution']
    assert f'{{{scores["a"]:g}}}' in exercises['C-019']['solution']
    print('Article matching QA: actual table/three figures agree; ranking A,C,B, scaled score 1.8, cosine 0.6 and projection 0.96 passed')


def check_matrix_training_bridges():
    """Follow the printed article data through matrices and the complete MLP update."""
    matrix_source=(ROOT/'book/chapters/03-matrix-multiplication.tex').read_text()
    candidates,transposed=numeric_matrices(matrix_source)[:2]
    feature_source=(ROOT/'book/chapters/01-vectors.tex').read_text()
    features={name:np.array([float(x),float(y)]) for name,x,y in
              re.findall(r'\$\\vect ([qabc])\^\\top\$ & \$([\d.]+)\$ & \$([\d.]+)\$',feature_source)}
    assert np.allclose(candidates,[features[name] for name in 'abc'])
    assert np.array_equal(transposed,candidates.T)
    batch=matrix_source.split(r'\label{sec:matrix-article-batch}',1)[1].split(r'\subsection{',1)[0]
    queries,printed_scores=numeric_matrices(batch)
    assert np.allclose(queries[0],features['q'])
    assert np.allclose(printed_scores,queries@candidates.T)
    single=re.search(r'\\boxed\{\(([^()]+)\)\}',matrix_source)
    assert single and np.allclose([float(v) for v in single[1].split(',')],printed_scores[0])
    figure=(ROOT/'book/figures/row-column-intuition.tex').read_text()
    cells=[float(v) for v in re.findall(r'\\node at \([^()]+\)\{\\sffamily ([0-9.]+)\}',figure)]
    assert np.allclose(cells[:6],candidates.ravel())
    assert np.allclose(cells[6:],transposed.ravel())
    pairing=(ROOT/'book/figures/matrix-row-column-pairing.tex').read_text()
    cells=[float(v) for v in re.findall(r'\\node at \([^()]+\) \{\$([0-9.]+)\$\}',pairing)]
    assert np.allclose(cells[:4],queries.ravel())
    assert np.allclose(cells[4:10],transposed.T.ravel())  # Diagram lists whole columns.
    assert np.allclose(cells[10:],printed_scores.ravel())

    source=(ROOT/'book/chapters/10-mlp.tex').read_text()
    forward_part=source.split(r'\subsection{按行向量约定',1)[1].split(r'\subsection{',1)[0]
    w1,w2=numeric_matrices(forward_part)
    shared=(ROOT/'book/figures/batch-linear-map.tex').read_text()
    assert np.array_equal(numeric_matrices(shared)[0],w1)
    rows={name:np.array([float(value) for value in values.split(',')])
          for name,values in re.findall(r'\(([xy][123])\) at [^;]*?\{\$\(([-\d.,]+)\)\$\}',shared)}
    assert len(rows)==6
    for i in (1,2,3):assert np.allclose(rows[f'x{i}']@w1,rows[f'y{i}'])
    x=np.array([2.,-1.]);target=np.array([2.,2.])
    def objective():
        predicted=np.maximum(x@w1,0)@w2
        return np.sum((predicted-target)**2)/2
    h=np.maximum(x@w1,0);delta=h@w2-target
    gradient2=np.outer(h,delta)
    gradient1=np.outer(x,(delta@w2.T)*(x@w1>0))
    gradients=source.split(r'\label{sec:mlp-matrix-gradient}',1)[1].split(r'\subsection{',1)[0]
    printed=numeric_matrices(gradients)
    assert np.allclose(printed[1],gradient2) and np.allclose(printed[-1],gradient1)
    for weight,gradient in ((w1,gradient1),(w2,gradient2)):
        for index in np.ndindex(weight.shape):
            old=weight[index];eps=1e-6
            weight[index]=old+eps;hi=objective()
            weight[index]=old-eps;lo=objective()
            weight[index]=old
            assert abs((hi-lo)/(2*eps)-gradient[index])<1e-7
    update=source.split(r'\label{sec:mlp-update-check}',1)[1].split(r'\subsection{',1)[0]
    new1,new2=numeric_matrices(update)
    assert np.allclose(new1,w1-.1*gradient1) and np.allclose(new2,w2-.1*gradient2)
    predicted=np.maximum(x@new1,0)@new2
    assert np.allclose(predicted,[2.1,1.4]) and np.isclose(np.sum((predicted-target)**2)/2,.185)
    assert '(2.1,1.4)' in update and r'\boxed{0.185}' in update
    print('Matrix bridges QA: article table/transpose/two figures, all twelve MLP weight derivatives and updated prediction/loss passed')


def check_learning_rate_comparison():
    """Compare convergent steps on the original data, catching the faster-if-larger claim."""
    from beginner_training_demo import loss, gradient
    results=[]
    for eta in (.75,.9):
        w,b=1.,0.
        for _ in range(10):
            gw,gb=gradient(w,b);w,b=w-eta*gw,b-eta*gb
        results.append(loss(w,b))
    assert .5<results[0]<results[1]
    chapter=(ROOT/'book/chapters/16-loss-gradient.tex').read_text()
    exercise=next(row for row in json.loads((ROOT/'book/exercises.json').read_text()) if row['id']=='C-067')
    for result in results:
        assert f'{result:.6f}' in chapter and f'{result:.6f}' in exercise['solution']
    print('Learning-rate QA: both stable, eta .75 beats .9 at step 10 on the actual three-point loss')


def check_mlp_nonlinearity():
    """Recompute every row of the same-weight linear/nonlinear contrast."""
    source=(ROOT/'book/chapters/10-mlp.tex').read_text()
    forward=source.split(r'\label{sec:mlp-forward}',1)[1].split(r'\subsection{',1)[0]
    w1,w2=numeric_matrices(forward)
    contrast=source.split(r'\label{sec:mlp-nonlinearity}',1)[1].split(r'\subsection{',1)[0]
    assert np.array_equal(numeric_matrices(contrast)[0],w1@w2)
    rows=re.findall(r'^\$\(([-\d,]+)\)\$ & \$\(([-\d,]+)\)\$ & \$\(([-\d,]+)\)\$',contrast,re.M)
    assert len(rows)==3
    results=[]
    for given,linear,nonlinear in rows:
        x=np.fromstring(given,sep=',');linear=np.fromstring(linear,sep=',');nonlinear=np.fromstring(nonlinear,sep=',')
        assert np.array_equal((x@w1)@w2,linear)
        assert np.array_equal(np.maximum(x@w1,0)@w2,nonlinear)
        results.append((x,linear,nonlinear))
    assert np.array_equal(results[0][0],-results[1][0])
    assert np.array_equal(results[0][1]+results[1][1],results[2][1])
    assert not np.array_equal(results[0][2]+results[1][2],results[2][2])
    print('MLP activation QA: all three printed contrasts use original weights and disprove a single linear map')


def check_core_cache_review():
    """R-13 supplies toy inputs AND a pinned real-config transfer without an elective prerequisite."""
    from config_table import load_rows
    row=next(r for r in json.loads((ROOT/'book/exercises.json').read_text()) if r['id']=='R-13')
    toy,real=row['question'].split(r'\textbf{再读真实配置：}',1)
    layers,q_heads,kv_heads,width,batch,positions,element_bytes,mha_heads=map(int,re.findall(r'\$(\d+)\$',toy))
    assert q_heads==mha_heads and q_heads%kv_heads==0
    gqa=kv_bytes(layers,kv_heads,width,positions,element_bytes,batch)
    mha=kv_bytes(layers,mha_heads,width,positions,element_bytes,batch)
    answers=re.findall(r'\\answerresult\{([\d{},]+)\}',row['solution'])
    for requests in (1,2,5):
        assert kv_bytes(layers,mha_heads,width,positions,element_bytes,requests)/kv_bytes(layers,kv_heads,width,positions,element_bytes,requests)==mha/gqa
    snapshot=next(obj for obj,_ in load_rows() if obj['config']['model_type']=='qwen2')
    fields=('num_hidden_layers','hidden_size','num_attention_heads','num_key_value_heads')
    expected={name:snapshot['config'][name] for name in fields}
    for body in (real,row['review_prompt']):
        published={name.replace(r'\_','_'):int(value) for name,value in
                   re.findall(r'\\texttt\{([a-z\\_]+)=(\d+)\}',body)
                   + re.findall(r'\\texttt\{([a-z\\_]+)\} & \$(\d+)\$',body)}
        assert published==expected, 'R-13 must contain the four actual pinned fields in both printed questions'
    runtime=real.split(r'\end{center}',1)[1]
    assert list(map(int,re.findall(r'\$(\d+)\$',runtime)))==[positions,element_bytes]
    assert expected['hidden_size']%expected['num_attention_heads']==0
    real_width=expected['hidden_size']//expected['num_attention_heads']
    real_gqa=kv_bytes(expected['num_hidden_layers'],expected['num_key_value_heads'],real_width,positions,element_bytes,batch)
    ratio=expected['num_attention_heads']//expected['num_key_value_heads']
    assert [int(v.replace('{,}','')) for v in answers]==[gqa,mha,mha//gqa,real_width,real_gqa,ratio]
    core=(ROOT/'book/chapters/22d-modern-transformers.tex').read_text().split(r'\label{sec:modern-gqa}',1)[1].split(r'\label{route:modern-core-end}',1)[0]
    assert all(name.replace('_',r'\_') in core for name in fields), 'Field-reading prerequisites must stay on the required route'
    assert r'd_k=d_{\rm model}/H_Q' in core
    assert all(name in row['solution'] for name in (r'config\_table.py',r'cache\_budget\_demo.py'))
    print(f'Core cache review QA: toy {gqa}/{mha} bytes; supplied pinned config gives width {real_width}, {real_gqa} bytes and {ratio}x MHA')


def check_cnn_channels():
    source=(ROOT/'book/chapters/19-cnn.tex').read_text()
    kernel=numeric_matrices(source.split(r'\subsection{小区域扫描',1)[1])[1]
    channels=source.split(r'\label{sec:cnn-channel-sum}',1)[1].split(r'\subsection{',1)[0]
    windows=numeric_matrices(channels)
    responses=[float(np.sum(window*kernel)) for window in windows]
    assert responses==[1.,1.,-1.] and sum(responses)==1
    assert kernel.size*len(windows)==12 and 2*kernel.size*len(windows)==24
    assert r'\boxed{1}' in channels
    print('CNN channel QA: all three printed RGB windows, shared initial slices, response 1 and 12/24 weights passed')


def check_motivation_examples():
    """Recompute the added bridges using their actual data and matrix shapes."""
    general=(ROOT/'book/chapters/18-generalization.tex').read_text()
    x=np.array([-1.,0.,1.]);y=np.array([-1.5,2.,2.5])
    linear=np.column_stack([x,np.ones(3)])
    quadratic=np.column_stack([x*x,x,np.ones(3)])
    line=np.linalg.lstsq(linear,y,rcond=None)[0]
    curve=np.linalg.solve(quadratic,y)
    scores=[np.mean((linear@line-y)**2),
            np.mean((quadratic@curve-y)**2)+.25*curve[0]**2]
    assert np.allclose(scores,[.5,.5625]) and scores[0]<scores[1]
    assert all(f'{score:g}' in general for score in scores)
    # The original generic drawing had six unrelated points; the prose had three.
    # Compare actual plotted coordinates and functions with the fitted models.
    figure=(ROOT/'book/figures/generalization-three-fits.tex').read_text()
    point_sets=re.findall(r'\\foreach \\px/\\py in \{([^}]+)\}',figure)
    plotted=[np.array([[float(Fraction(v)) for v in pair.split('/')]
                       for pair in group.split(',')]) for group in point_sets]
    validation_x=np.array([-.5,.5]);validation_y=np.array([1/8,17/8])
    assert len(plotted)==2
    assert np.array_equal(plotted[0],np.column_stack([x,y]))
    assert np.array_equal(plotted[1],np.column_stack([validation_x,validation_y]))
    assert all(x.min()<value<x.max() for value in validation_x)
    predictions=[np.column_stack([validation_x,np.ones(2)])@line,
                 np.column_stack([validation_x**2,validation_x,np.ones(2)])@curve]
    mse=[np.mean((pred-validation_y)**2) for pred in predictions]
    assert np.allclose(mse,[1/64,1/4]) and '$1/64$' in general and '$1/4$' in general
    expressions=re.findall(r'\(\\x,\{([^}]+)\}\)',figure)
    assert len(expressions)==2
    for expression,expected in zip(expressions,predictions):
        expression=expression.replace(r'\x','x')
        assert re.fullmatch(r'[x0-9.*+ /()-]+',expression)
        assert np.allclose(eval(expression,{'__builtins__':{}},{'x':validation_x}),expected)
    post=(ROOT/'book/chapters/23c-post-training.tex').read_text()
    new=np.array([.7,.3]);reference=np.array([.5,.5])
    kl=np.sum(new*np.log(new/reference))
    assert f'{kl:.4f}' in post
    modern=(ROOT/'book/chapters/22d-modern-transformers.tex').read_text()
    vector=np.array([3.,4.])
    rms=vector/np.sqrt(np.mean(vector**2))
    assert np.allclose(rms,10*vector/np.sqrt(np.mean((10*vector)**2)))
    assert all(f'{value:.3f}' in modern for value in rms)
    assert np.allclose((vector-vector.mean())/vector.std(),[-1,1])
    assert np.allclose(np.array([2,3])*[.5,2],[1,6]) and '(1,6)' in modern
    deployment=(ROOT/'book/chapters/23b-deployment-and-ecosystem.tex').read_text()
    row=np.array([1,2]);weight=np.eye(2)
    up=np.array([[1],[0]]);down=np.array([[0,1]])
    assert up.shape==(2,1) and down.shape==(1,2)
    assert np.array_equal(row@up@down,[0,1])
    assert np.array_equal(row@(weight+up@down),[1,3]) and '(1,3)' in deployment
    assert 1000*8+8*1000==16000 and 16000/1000**2==.016
    print('Motivation examples QA: regularized candidate ranking, KL, RMS scaling, gates and additive LoRA path passed')


def numeric_matrices(source):
    return [np.array([[float(Fraction(cell.strip())) for cell in row.split('&')]
                      for row in body.split(r'\\')])
            for body in re.findall(r'\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}',source,re.S)]


def attention_maximum_errors(source):
    """Compare the printed winner sets with Softmax of the actual printed scores.

    The old checks did not inspect which positions shared a row maximum; a
    correct score matrix could therefore accompany a misleading prose claim.
    """
    x,scores=numeric_matrices(source)
    assert np.array_equal(scores,x@x.T), 'Zero-projection score matrix differs from XX^T'
    exponentials=np.exp(scores-scores.max(axis=1,keepdims=True))
    weights=exponentials/exponentials.sum(axis=1,keepdims=True)
    claims=re.findall(r'第([一二三])行对位置 \$([\d,]+)\$ 给出(并列|唯一)最大权重',source)
    if len(claims)!=len(weights):return ['Missing explicit maximum positions for each attention row']
    errors=[]
    for name,positions,kind in claims:
        index='一二三'.index(name)
        expected=(np.flatnonzero(np.isclose(weights[index],weights[index].max()))+1).tolist()
        actual=[int(value) for value in positions.split(',')]
        if actual!=expected or (kind=='唯一')!=(len(expected)==1):
            errors.append(f'Attention row {index+1}: printed {actual}/{kind}, computed {expected}')
    return errors


def check_attention_maxima():
    source=(ROOT/'book/chapters/21c-naive-attention.tex').read_text()
    assert not attention_maximum_errors(source)
    # Reproduce the misleading unique-winner reading of the former sentence.
    bad=source.replace('第一行对位置 $1,3$ 给出并列最大权重',
                       '第一行对位置 $3$ 给出唯一最大权重')
    assert attention_maximum_errors(bad), 'Maximum-position gate accepted the original confusion'
    print('Attention maximum QA: first/second rows tie at [1,3]/[2,3]; only the third has unique winner [3]')


def check_distance_reading():
    """Run the printed recurrence and a full Softmax for each printed distance."""
    rnn=(ROOT/'book/chapters/21-rnn.tex').read_text()
    coefficient=float(re.search(r'h_t=x_t\+([\d.]+)h_',rnn)[1])
    source=(ROOT/'book/chapters/21c-naive-attention.tex').read_text()
    example=source.split(r'\label{experiment:distance-reading}',1)[1].split(r'\subsection{',1)[0]
    target_score=np.log(float(re.search(r'匹配分数为 \$\\ln(\d+)\$',example)[1]))
    rows=re.findall(r'^\$(\d+)\$ & \$([\d.]+)\$ & \$([\d.]+)\$',example,re.M)
    assert [int(row[0]) for row in rows]==[1,2,4,8]
    for distance,printed_rnn,printed_attention in rows:
        distance=int(distance)
        state=1.
        for _ in range(distance):state=coefficient*state
        scores=np.zeros(distance+1);scores[0]=target_score
        weights=np.exp(scores-scores.max());weights/=weights.sum()
        values=np.zeros(distance+1);values[0]=1.
        readout=float(weights@values)
        assert f'{state:.4f}'==printed_rnn,(distance,state,printed_rnn)
        assert f'{readout:.4f}'==printed_attention,(distance,readout,printed_attention)
        assert np.isclose(readout,9/(9+distance))
    # Check the stated counterexample to universal decay: coefficient 1 preserves the signal.
    state=1.
    for _ in range(8):state=1.*state
    assert state==1. and np.isclose(coefficient**8,1/256)
    print('Distance reading QA: four recurrence/Softmax rows and coefficient-1 counterexample passed')


def check_scaling_budget():
    """Recompute the printed FLOP budget and the historical Chinchilla ratio."""
    source=(ROOT/'book/chapters/23e-tech-judgement.tex').read_text()
    example=source.split(r'\label{sec:scaling-compute-budget}',1)[1].split(r'\subsection{',1)[0]
    def scientific(pattern):
        match=re.search(pattern,example)
        assert match,pattern
        return float(match[1])*10**int(match[2])
    parameters=scientific(r'N=([\d.]+)\\times10\^(\d+)')
    budget=scientific(r'C=([\d.]+)\\times10\^\{(\d+)\}')
    tokens=scientific(r'&=([\d.]+)\\times10\^(\d+)')
    assert np.isclose(tokens,budget/(6*parameters))
    assert np.isclose(tokens/parameters,20)
    assert np.isclose(tokens/1e8,25)
    assert np.isclose(budget/(6*2*parameters)/1e8,12.5)
    assert np.isclose(6*(2*parameters)*(2*tokens)/budget,4)
    numerator,denominator=re.search(
        r'\\frac\{D\}\{N\}=\\frac\{([\d.]+)\\times10\^\{12\}\}\{([\d.]+)\\times10\^\{10\}\}',example).groups()
    assert np.isclose(float(numerator)*1e12/(float(denominator)*1e10),20)
    print('Scaling budget QA: 2.5B tokens, fixed-compute trade-off, fourfold FLOPs and Chinchilla 20:1 passed')


def check_model_comparison():
    """Recompute comparison-table dimensions and count shared GPT-2 weights once."""
    source=(ROOT/'book/chapters/23a-from-toy-to-gpt.tex').read_text()
    table=source.split(r'\label{sec:toy-real-model-comparison}',1)[1].split(r'\end{tabularx}',1)[0]
    rows={name.strip():(left,right) for name,left,right in
          re.findall(r'^([^&\n]+) & (.*?) & (.*?)\\\\',table,re.M)}
    cfg=json.loads((ROOT/'scripts/model_configs/gpt2.json').read_text())['config']
    w=parameters();width=cfg['n_embd'];layers=cfg['n_layer']
    # Each block: 12*d^2 projection weights, 9*d biases, 4*d Norm coefficients.
    # Token/position embeddings and final Norm are outside the blocks; Wout is tied.
    gpt_count=(cfg['vocab_size']+cfg['n_positions'])*width+layers*(12*width**2+13*width)+2*width
    expected={
        '可训练参数':(sum(value.size for value in w.values()),gpt_count),
        '词表大小':(w['E'].shape[0],cfg['vocab_size']),
        '隐藏宽度':(w['E'].shape[1],width),
        'Block 层数':(1,layers),
        '注意力头数':(1,cfg['n_head']),
        'FFN 中间宽度':(w['Wup'].shape[1],4*width),
        '可处理的位置数':(w['P'].shape[0],cfg['n_positions']),
    }
    for name,pair in expected.items():
        printed=tuple(int(re.search(r'\d+',cell.replace('{,}',''))[0]) for cell in rows[name])
        assert printed==pair,(name,printed,pair)
    ratio=gpt_count/expected['可训练参数'][0]
    assert round(ratio/10000)==126 and '$126$ 万倍' in source
    print(f'Model comparison QA: seven numeric rows match canonical toy/pinned GPT-2; {gpt_count:,} parameters, ratio {ratio:.3f}')


def check_published_forward():
    """Check printed parameters and real intermediate matrices, not label presence."""
    w=parameters();state=forward(w)
    position=(ROOT/'book/chapters/22a-position-multihead.tex').read_text()
    projections=numeric_matrices(position)[:5]
    for printed,expected in zip(projections,[w['E'][[1,3]],w['E'][[3,1]],w['Wq'],w['Wk'],w['Wv']]):
        assert np.array_equal(printed,expected)
    source=(ROOT/'book/chapters/22b-token-to-output.tex').read_text()
    expected=[w['Wq'],w['Wk'],w['Wv'],state['k'][:2],state['v'][:2],w['Wo'],w['Wup'],w['Wdown'],w['Wout'],
              state['x'],state['a'],state['h'],state['probs']]
    printed=numeric_matrices(source)
    assert len(printed)==len(expected)
    for actual,wanted in zip(printed,expected):
        assert actual.shape==wanted.shape and np.allclose(actual,wanted,atol=5.1e-5,rtol=0),(actual,wanted)
    # A quick-reference definition omitting nonidentity Wo silently changes the model.
    card=(ROOT/'book/chapters/00e-core-formulas.tex').read_text()
    assert r'R_{\rm raw}=AV' in card and r'X_{\rm att}=X+R_{\rm raw}W_O' in card
    assert np.allclose(state['r'],state['x']+state['a']@state['v']@printed[5])
    assert not np.allclose(state['r'],state['x']+state['a']@state['v'])
    # Verify each newly printed second-position result at its own stage.
    for key,section in [('q','第二步'),('raw','第三步'),('r','第三步'),('b','第四步'),
                        ('pre','第四步'),('h','第四步'),('logits','第五步')]:
        stage=source.split(r'\subsection{'+section,1)[1].split(r'\subsection{',1)[0]
        assert all(value==0 or f'{value:.4f}' in stage for value in state[key][1]),(key,state[key][1])
    print('Published forward QA: projection/FFN/output weights, thirteen matrices, second-position trace and Wo residual match canonical computation')


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
    check_article_matching()
    check_matrix_training_bridges()
    check_mlp_nonlinearity()
    check_core_cache_review()
    check_learning_rate_comparison()
    check_cnn_channels()
    check_memory()
    check_motivation_examples()
    check_attention_maxima()
    check_distance_reading()
    check_scaling_budget()
    check_model_comparison()
    check_published_forward()
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
