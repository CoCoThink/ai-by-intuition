#!/usr/bin/env python3
"""Recompute the opening chapters from one dataset, including stability boundaries."""
from fractions import Fraction as F
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
DATA = ((-1, -1), (0, 1), (1, 3))


def loss(w, b):
    return sum((w*x+b-y)**2 for x, y in DATA) / 3


def gradient(w, b):
    return (sum(2*x*(w*x+b-y) for x, y in DATA)/3,
            sum(2*(w*x+b-y) for x, y in DATA)/3)


def check_relu_fit():
    data=((-1,1),(0,0),(1,1))
    source=(ROOT/'book/chapters/07-functions-relu.tex').read_text()
    for w in (F(-2),F(0),F(1,3)):
        for b in (F(0),F(2,3),F(2)):
            mse=sum((w*x+b-y)**2 for x,y in data)/3
            assert mse==F(2,3)*w*w+(b-F(2,3))**2+F(2,9)
    assert all(max(x,0)+max(-x,0)==y for x,y in data)
    a=c=F(0)
    def tex(value):
        return '0' if value==0 else f'${value}$'
    for step in range(5):
        mse=sum((a*max(x,0)+c*max(-x,0)-y)**2 for x,y in data)/3
        assert a==c==1-F(1,2)**step and mse==F(2,3)*F(1,4)**step
        row=f'{step} & {tex(a)} & {tex(c)} & {tex(mse)}'
        assert row in source, ('Published ReLU training row differs',row)
        # Derivatives from individual sample residuals, independently of the formula.
        ga=sum(2*max(x,0)*(a*max(x,0)+c*max(-x,0)-y) for x,y in data)/3
        gc=sum(2*max(-x,0)*(a*max(x,0)+c*max(-x,0)-y) for x,y in data)/3
        a,c=a-F(3,4)*ga,c-F(3,4)*gc
    assert F(1,6)<F(2,9)
    print('ReLU fit QA: affine lower bound 2/9, exact two-unit fit and five printed SGD rows passed')


def run_checks():
    check_relu_fit()
    source = (ROOT/'book/chapters/16-loss-gradient.tex').read_text()
    w, b = F(1), F(0)
    for step in range(11):
        assert loss(w, b) == F(2, 3)*(w-2)**2+(b-1)**2
        assert w == 2-F(3, 5)**step and b == 1-F(2, 5)**step
        if step <= 5 or step == 10:
            row = f'{step} & {float(w):.6f} & {float(b):.6f} & {float(loss(w,b)):.6f}'
            assert row in source, ('Published iteration table differs', row)
            print(row)
        gw, gb = gradient(w, b)
        w, b = w-F(3,10)*gw, b-F(3,10)*gb
    for rate in (F(3,10), F(3,4), F(1), F(6,5), F(3,2), F(8,5)):
        rw, rb = 1-F(4,3)*rate, 1-2*rate
        w, b = F(1), F(0)
        for step in range(8):
            assert w-2 == -rw**step and b-1 == -rb**step
            gw, gb = gradient(w, b)
            w, b = w-rate*gw, b-rate*gb
        assert (abs(rw)<1 and abs(rb)<1) == (0<rate<1)
    # Independent finite differences of the sample-wise MSE.
    for w, b in ((1., 0.), (1.4, .6), (2., 1.)):
        gw, gb = gradient(w, b); eps=1e-5
        assert math.isclose((loss(w+eps,b)-loss(w-eps,b))/(2*eps),gw,abs_tol=1e-9)
        assert math.isclose((loss(w,b+eps)-loss(w,b-eps))/(2*eps),gb,abs_tol=1e-9)
    assert loss(2,1)==0 and loss(F(1),F(0))==F(5,3)
    assert '只比较斜率的微小变化' not in source
    print('Opening training QA: sample MSE, joint solution, printed 0–10 steps, gradients and stability boundaries passed')


if __name__ == '__main__':
    run_checks()
