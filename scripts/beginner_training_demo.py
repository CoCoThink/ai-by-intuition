#!/usr/bin/env python3
"""Recompute the opening chapters from one dataset, including stability boundaries."""
from fractions import Fraction as F
from pathlib import Path
import ast
import math
import operator
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ((-1, -1), (0, 2), (1, 2))


def loss(w, b):
    return sum((w*x+b-y)**2 for x, y in DATA) / 3


def gradient(w, b):
    return (sum(2*x*(w*x+b-y) for x, y in DATA)/3,
            sum(2*(w*x+b-y) for x, y in DATA)/3)


def sample_gradient(w, b, x, y):
    residual=w*x+b-y
    return 2*x*residual,2*residual


def plotted_value(expression, x):
    """Evaluate the arithmetic actually drawn by pgfplots, without executing code."""
    operators={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,
               ast.Div:operator.truediv,ast.Pow:operator.pow}
    def value(node):
        if isinstance(node,ast.Constant):return F(str(node.value))
        if isinstance(node,ast.Name) and node.id=='x':return x
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):
            return -value(node.operand) if isinstance(node.op,ast.USub) else value(node.operand)
        if isinstance(node,ast.BinOp) and type(node.op) in operators:
            return operators[type(node.op)](value(node.left),value(node.right))
        raise AssertionError(('Unsupported plot arithmetic',expression))
    return value(ast.parse(expression.replace('^','**'),mode='eval').body)


def check_optimization_figures():
    """Recompute plotted curves, predictions, residuals and all trajectory points."""
    figures=ROOT/'book/figures'
    def source(name):return (figures/f'{name}.tex').read_text()
    def points(body):
        return [tuple(map(float,pair)) for pair in re.findall(r'\(([-+.0-9]+),([-+.0-9]+)\)',body)]
    def coordinate_plots(body):
        return [points(block) for block in re.findall(
            r'\\addplot\[[^\]]*\]\s*coordinates\s*\{([^}]+)\};',body,re.S)]
    def curves(body):
        return re.findall(r'\\addplot\[[^\]]*\]\s*\{([^{}]+)\};',body,re.S)
    def equal_points(actual,expected,tolerance=1e-9):
        assert len(actual)==len(expected),('Wrong number of plotted points',actual,expected)
        for row,wanted in zip(actual,expected):
            assert len(row)==len(wanted),('Wrong plotted coordinate dimensions',row,wanted)
            assert all(math.isclose(a,float(b),rel_tol=0,abs_tol=tolerance)
                       for a,b in zip(row,wanted)),('Plotted point differs',row,wanted)
    probes=(F(9,10),F(1),F(11,10))
    local=source('loss-descent')
    equal_points(coordinate_plots(local)[0],[(w,loss(w,F(0))) for w in probes],1e-6)
    gw,gb=gradient(F(1),F(0))
    local_curves=curves(local)
    partial_curves=curves(source('gradient-partial-slices'))
    assert len(local_curves)==2 and len(partial_curves)==4
    for w in probes:
        for expression in (local_curves[0],partial_curves[0]):
            assert plotted_value(expression,w)==loss(w,F(0))
        for expression in (local_curves[1],partial_curves[1]):
            assert plotted_value(expression,w)==loss(F(1),F(0))+gw*(w-1)
    for b in (F(-1,10),F(0),F(1,10)):
        assert plotted_value(partial_curves[2],b)==loss(F(1),b)
        assert plotted_value(partial_curves[3],b)==loss(F(1),F(0))+gb*b
    fits=((source('gradient-prediction-update'),((F(1),F(0)),(F(6,5),F(3,5)))),
          (source('loss-two-parameter-contours'),((F(3,2),F(1)),)))
    for body,parameters in fits:
        predictions=coordinate_plots(body);expressions=curves(body)
        assert len(predictions)==2*len(parameters) and len(expressions)==len(parameters)
        segments=[tuple(map(float,row)) for row in re.findall(
            r'\\draw\[residualcolor,thick\] \(axis cs:([-+.0-9]+),([-+.0-9]+)\)--'
            r'\(axis cs:([-+.0-9]+),([-+.0-9]+)\);',body)]
        assert len(segments)==3*len(parameters)
        for i,(w,b) in enumerate(parameters):
            equal_points(predictions[2*i],[(x,w*x+b) for x,_ in DATA])
            equal_points(predictions[2*i+1],DATA)
            for j,(x,y) in enumerate(DATA):
                assert plotted_value(expressions[i],F(x))==w*x+b
                equal_points([segments[3*i+j]],[(x,y,x,w*x+b)])
    trajectory=[];losses=[];w,b=F(1),F(0)
    for t in range(11):
        trajectory.append((w,b));losses.append((t,loss(w,b)))
        gw,gb=gradient(w,b);w,b=w-F(3,10)*gw,b-F(3,10)*gb
    iterations=source('gradient-iteration-path');plots=coordinate_plots(iterations)
    assert len(plots)==4
    equal_points(plots[0],trajectory)
    equal_points(plots[1],[trajectory[t] for t in (0,1,2,5,10)])
    equal_points(plots[2],losses)
    equal_points(plots[3],[losses[t] for t in (0,1,2,5,10)])
    assert curves(iterations)==['2/3']
    contours=source('loss-two-parameter-contours')
    path=re.search(r'\\draw\[flowcolor,very thick\] plot coordinates\s*\{([^}]+)\};',contours)
    assert path, 'Missing actual trajectory on loss contours'
    equal_points(points(path[1]),trajectory)
    # The contour radii depend on loss above 1/2 and the actual TikZ axis units.
    units=re.search(r'\\begin\{tikzpicture\}\[x=([0-9.]+)mm,y=([0-9.]+)mm',contours)
    assert units and units[1]==units[2], 'Use equal parameter-axis units for the loss contours'
    unit=float(units[1])
    radii=re.findall(r'x radius=([0-9.]+)mm,y radius=([0-9.]+)mm',contours)
    assert len(radii)==2
    for (rx,ry),level in zip(radii,(F(5,3),F(18,25))):
        above_min=float(level-F(1,2))
        assert math.isclose(float(rx),unit*math.sqrt(above_min/(2/3)),abs_tol=.001)
        assert math.isclose(float(ry),unit*math.sqrt(above_min),abs_tol=.001)
    print('Optimization figure QA: probe points, partial slopes, fitted lines, residual segments, both 0–10 trajectories and contour radii passed')


def check_sample_gradients():
    source=(ROOT/'book/chapters/18c-training-engineering.tex').read_text()
    rows=[sample_gradient(F(1),F(0),x,y) for x,y in DATA]
    for (x,y),(gw,gb) in zip(DATA,rows):
        row=f'只有样本 $({x},{y})$ & $({gw},{gb})$'
        assert row in source, ('Published sample gradient differs',row)
    mean=tuple(sum(row[j] for row in rows)/len(DATA) for j in range(2))
    assert mean==gradient(F(1),F(0))==(F(-2,3),F(-2))
    assert f'全部三个样本，梯度取平均 & $({mean[0]},{mean[1]})$' in source
    # A zero sample gradient does not imply a zero full-data gradient.
    assert rows[0]==(0,0) and mean!=(0,0)
    for w,b in ((1.,0.),(1.5,1.)):
        for x,y in DATA:
            gw,gb=sample_gradient(w,b,x,y);eps=1e-5
            def sample_loss(sw,sb):return (sw*x+sb-y)**2
            assert math.isclose((sample_loss(w+eps,b)-sample_loss(w-eps,b))/(2*eps),gw,abs_tol=1e-9)
            assert math.isclose((sample_loss(w,b+eps)-sample_loss(w,b-eps))/(2*eps),gb,abs_tol=1e-9)
    # At the full-data optimum, a sampled gradient can increase the full loss.
    w,b=F(3,2),F(1)
    optimal_rows=[sample_gradient(w,b,x,y) for x,y in DATA]
    assert tuple(sum(row[j] for row in optimal_rows)/3 for j in range(2))==(0,0)
    gw,gb=optimal_rows[1]
    assert loss(w-F(3,10)*gw,b-F(3,10)*gb)>loss(w,b)
    print('Sample-gradient QA: four printed rows, mean gradient, finite differences and stochastic full-loss increase passed')


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
    print('ReLU fit QA: affine lower bound 2/9, exact two-unit fit and five printed gradient-descent rows passed')


def run_checks():
    check_sample_gradients()
    check_relu_fit()
    check_optimization_figures()
    source = (ROOT/'book/chapters/16-loss-gradient.tex').read_text()
    # Recompute candidate scores from individual residuals, before using any optimum.
    for w, b, expected in ((1, 0, F(5, 3)), (1, 1, F(2, 3)),
                           (1, 2, F(5, 3)), (2, 1, F(2, 3))):
        assert loss(F(w), F(b)) == expected
    assert sum(x+1-y for x, y in DATA) == 0
    # Verify the completed-square identity away from the optimum, too.
    for w in (F(-1), F(0), F(1), F(3, 2), F(3)):
        for b in (F(-2), F(0), F(1), F(2)):
            assert loss(w, b) == F(2, 3)*(w-F(3, 2))**2+(b-1)**2+F(1, 2)
    w, b = F(1), F(0)
    for step in range(11):
        assert w == F(3, 2)-F(1, 2)*F(3, 5)**step and b == 1-F(2, 5)**step
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
            assert w-F(3, 2) == -F(1, 2)*rw**step and b-1 == -rb**step
            gw, gb = gradient(w, b)
            w, b = w-rate*gw, b-rate*gb
        assert (abs(rw)<1 and abs(rb)<1) == (0<rate<1)
    # Independent finite differences of the sample-wise MSE.
    for w, b in ((1., 0.), (1.2, .6), (1.5, 1.), (0., 3.)):
        gw, gb = gradient(w, b); eps=1e-5
        assert math.isclose((loss(w+eps,b)-loss(w-eps,b))/(2*eps),gw,abs_tol=1e-9)
        assert math.isclose((loss(w,b+eps)-loss(w,b-eps))/(2*eps),gb,abs_tol=1e-9)
    # C-006 uses a different initial point with the same data and update rule.
    gw, gb = gradient(F(0), F(3))
    assert (gw, gb) == (-2, 4)
    assert loss(F(0), F(3)) == 6
    assert loss(-F(3,10)*gw, 3-F(3,10)*gb) == F(42,25)
    assert loss(F(3,2), F(1)) == F(1,2)
    print('Opening training QA: candidate MSE, positive minimum, printed 0–10 steps, gradients and stability boundaries passed')


if __name__ == '__main__':
    run_checks()
