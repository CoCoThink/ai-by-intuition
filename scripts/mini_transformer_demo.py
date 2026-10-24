#!/usr/bin/env python3
"""Two-dimensional rational-parameter attention/FFN forward and reverse pass.

A deliberately simplified Block: no Norm, fixed X=I2, one causal head with key
width 1, Value width 2; loss only at the final position, target class 2.
All derivatives are rational at this point, loss is ln(2). Finite differences
check every parameter rather than repeating the hand-derived expressions.
"""
from __future__ import annotations
import numpy as np


def parameters():
    return dict(Wq=np.array([[0.], [1.]]), Wk=np.zeros((2, 1)),
                Wv=np.eye(2), Wo=np.eye(2), Wup=np.eye(2), Wdown=np.eye(2),
                Wout=np.array([[1., -1.], [-1/3, 1/3]]))


def forward(w):
    x = np.eye(2); q=x@w['Wq']; k=x@w['Wk']; v=x@w['Wv']
    s=q@k.T; s[0,1]=-np.inf
    a=np.exp(s-s.max(axis=1,keepdims=True)); a/=a.sum(axis=1,keepdims=True)
    o=a@v; r=x+o@w['Wo']; u=r@w['Wup']; f=np.maximum(u,0)
    h=r+f@w['Wdown']; z=h[-1]@w['Wout']
    logp=z-z.max(); logp-=np.log(np.exp(logp).sum())
    p=np.exp(logp); loss=-logp[1]
    return locals()


def backward(w, c):
    gz=c['p'].copy(); gz[1]-=1
    g={'Wout':np.outer(c['h'][-1],gz)}
    gh=np.zeros((2,2)); gh[-1]=gz@w['Wout'].T
    g['Wdown']=c['f'].T@gh
    gu=(gh@w['Wdown'].T)*(c['u']>0)
    g['Wup']=c['r'].T@gu
    gr=gh+gu@w['Wup'].T
    g['Wo']=c['o'].T@gr
    go=gr@w['Wo'].T
    g['Wv']=c['x'].T@(c['a'].T@go)
    ga=go@c['v'].T
    gs=c['a']*(ga-(c['a']*ga).sum(axis=1,keepdims=True))
    gs[0,1]=0
    g['Wq']=c['x'].T@(gs@c['k'])
    g['Wk']=c['x'].T@(gs.T@c['q'])
    return g


def run_checks():
    w=parameters(); c=forward(w); g=backward(w,c)
    assert np.allclose(c['a'], [[1,0],[.5,.5]])
    assert np.allclose(c['r'][-1], [.5,1.5])
    assert np.allclose(c['h'][-1], [1,3])
    assert np.allclose(c['z'], [0,0]) and abs(c['loss']-np.log(2))<1e-12
    expected=dict(Wout=[[.5,-.5],[1.5,-1.5]], Wdown=[[.5,-1/6],[1.5,-.5]],
                  Wup=[[.5,-1/6],[1.5,-.5]], Wo=[[1,-1/3],[1,-1/3]],
                  Wv=[[1,-1/3],[1,-1/3]], Wk=[[2/3],[-2/3]], Wq=[[0],[0]])
    # Every parameter gradient is checked against loss differences, including
    # nonzero score->Key gradients and the zero Query gradient at K=0.
    maximum=0.
    for key, value in w.items():
        assert np.allclose(g[key], expected[key]), key
        for index in np.ndindex(value.shape):
            old=value[index]; eps=1e-6
            value[index]=old+eps; hi=forward(w)['loss']
            value[index]=old-eps; lo=forward(w)['loss']
            value[index]=old
            maximum=max(maximum,abs((hi-lo)/(2*eps)-g[key][index]))
    assert maximum<1e-8, maximum
    updated={key:value-.01*g[key] for key,value in w.items()}
    assert forward(updated)['loss']<c['loss']
    print(f'Rational mini Block: loss=ln(2); all 24 parameter derivatives checked; max error={maximum:.2g}')
    return c,g


if __name__=='__main__':
    run_checks()
