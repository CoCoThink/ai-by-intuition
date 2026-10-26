#!/usr/bin/env python3
"""Architecture hand calculations: RoPE shift, MoE Top-2, illustrative MLA cache, window."""
from __future__ import annotations
from math import cos, exp, isclose, pi, sin, sqrt
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def rope_score(m: int, n: int, theta: float) -> float:
    """Row vectors q=k=(1,0) rotated by m*theta and n*theta, then dotted."""
    q = (cos(m * theta), sin(m * theta))
    k = (cos(n * theta), sin(n * theta))
    return q[0] * k[0] + q[1] * k[1]


def check_rope_figure(prose, figure):
    """Compare the actual plotted rotations and printed coordinates with the prose."""
    denominator=int(re.search(r'角频率 \$\\theta=\\pi/(\d+)\$',prose)[1])
    theta=pi/denominator
    pairs=[tuple(map(int,row)) for row in re.findall(r'm=(\d+).*?n=(\d+)',prose,re.S)][:2]
    titles=[tuple(map(int,row)) for row in re.findall(r'位置 \$m=(\d+),\\ n=(\d+)\$',figure)]
    assert titles==pairs and len(pairs)==2, ('RoPE figure positions differ from prose',titles,pairs)
    vectors=re.findall(r'\\draw\[->,very thick,(blue|teal)\] \(0,0\)--\((\d+):([0-9.]+)\)'
                       r' node\[[^\]]+\] \{([QK]) \$\(([^$]+)\)\$\};',figure)
    assert len(vectors)==4, 'Expected two Q/K vector pairs with explicit polar coordinates'
    def tex_number(value):
        fraction=re.fullmatch(r'(-?)\\tfrac(?:\{\\sqrt(\d+)\}|(\d))(\d)',value)
        if not fraction:return float(value)
        sign,radical,numerator,divisor=fraction.groups()
        return (-1 if sign else 1)*(sqrt(int(radical)) if radical else int(numerator))/int(divisor)
    for pair,drawn in zip(pairs,(vectors[:2],vectors[2:])):
        assert [(row[0],row[3]) for row in drawn]==[('blue','Q'),('teal','K')]
        for position,(color,angle,radius,name,label) in zip(pair,drawn):
            assert isclose(float(angle)*pi/180,position*theta) and float(radius)==1
            expected=(cos(position*theta),sin(position*theta))
            actual=tuple(map(tex_number,label.split(',')))
            assert len(actual)==2 and all(isclose(a,b,abs_tol=1e-12) for a,b in zip(actual,expected)),label
        printed=re.findall(r'点积 \$(\d+)/(\d+)\$',figure)
        assert printed and all(isclose(int(a)/int(b),rope_score(*pair,theta)) for a,b in printed)
    arcs=[tuple(map(int,row)) for row in re.findall(r'arc \((\d+):(\d+):\.4\)',figure)]
    assert arcs==[tuple(int(position*180/denominator) for position in pair) for pair in pairs]
    assert f'\\theta=\\pi/{denominator}' in figure
    print('RoPE figure QA: prose positions/frequency, all four drawn vectors and coordinate labels, angle arcs and printed dot products agree')


def mask(n: int, window: int):
    assert 1 <= window <= n
    return [[int(j <= i and j >= max(0, i - window + 1))
             for j in range(n)] for i in range(n)]


def main():
    check_rope_figure((ROOT/'book/chapters/22d-modern-transformers.tex').read_text(),
                      (ROOT/'book/figures/rope-relative-rotation.tex').read_text())
    theta = pi / 3
    assert isclose(rope_score(0, 1, theta), .5) and isclose(rope_score(2, 3, theta), .5)
    assert isclose(rope_score(0, 2, theta), -.5)
    print("RoPE scores (0,1), (2,3), (0,2):",
          [round(rope_score(m, n, theta), 6) for m, n in ((0, 1), (2, 3), (0, 2))])

    scores = (2, 1, 0)
    top2 = sorted(range(3), key=lambda i: -scores[i])[:2]
    weights = [exp(scores[i]) / sum(exp(scores[j]) for j in top2) for i in top2]
    full = [exp(s) / sum(exp(t) for t in scores) for s in scores]
    renorm = [full[i] / sum(full[j] for j in top2) for i in top2]
    assert top2 == [0, 1] and all(isclose(a, b) for a, b in zip(weights, renorm))
    assert round(weights[0], 3) == .731 and round(weights[1], 3) == .269
    assert [round(p, 3) for p in full] == [.665, .245, .090] and round(full[0] + full[1], 3) == .910
    print(f"MoE Top-2 weights: {weights[0]:.3f}, {weights[1]:.3f}")

    # Hypothetical cache accounting, one layer; not a specific published MLA.
    t, heads, kv_heads, width, latent, rope = 8, 4, 2, 2, 3, 2
    mha = 2 * t * heads * width   # K and V for every head.
    gqa = 2 * t * kv_heads * width
    mla_toy = t * (latent + rope)  # Shared latent plus positional cache.
    assert (mha, gqa, mla_toy) == (128, 64, 40)
    print(f"Toy cache elements per layer: MHA={mha}, GQA={gqa}, "
          f"MLA-like={mla_toy} (hypothetical)")

    m = mask(n=5, window=3)
    assert m == [
        [1, 0, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [1, 1, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 1, 1],
    ]
    allowed = sum(map(sum, m))
    assert allowed == 12
    print("5 x 5 causal sliding-window mask (window=3):")
    for row in m:
        print(" ".join(str(value) for value in row))
    print("Allowed pairs:", allowed, "vs full causal:", 5 * 6 // 2)
    print("Architecture arithmetic QA passed.")


if __name__ == "__main__":
    main()
