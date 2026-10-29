#!/usr/bin/env python3
"""Finite-difference regression for the book's three-score attention example.

Uses only Python's standard library. It checks the actual local derivatives,
not just whether the formulas are printed.
"""
from math import exp, sqrt

SQRT2 = sqrt(2.0)
Q = [SQRT2, 0.0]
K = [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]
V = [1.0, 0.0, -1.0]


def forward(q, keys):
    scores = [sum(x * z for x, z in zip(q, key)) / SQRT2
              for key in keys]
    unnormalized = [exp(z - max(scores)) for z in scores]
    zsum = sum(unnormalized)
    weights = [w / zsum for w in unnormalized]
    output = sum(w * val for w, val in zip(weights, V))
    return (output - 1) ** 2 / 2, weights, output


def derivative(f, value, h=1e-6):
    return (f(value + h) - f(value - h)) / (2 * h)


def layernorm(x):
    mean = sum(x) / 3
    centered = [z - mean for z in x]
    var = sum(z * z for z in centered) / 3
    return [z / sqrt(var) for z in centered]


def main():
    loss, a, y = forward(Q, K)
    g_y = y - 1
    # Raise only s1: Q[0]/sqrt(2) is s1 for these printed keys.
    # Check each weight separately, including the two falling weights.
    local = [a[0] * (1 - a[0]), -a[1] * a[0], -a[2] * a[0]]
    for i, expected in enumerate(local):
        def varying_score(value):
            return forward([value * SQRT2, 0.0], K)[1][i]
        assert abs(derivative(varying_score, 1.0) - expected) < 1e-7
    g_scores = [g_y * a[i] * (V[i] - y) for i in range(3)]
    g_q = [sum(g_scores[i] * K[i][j] for i in range(3)) / SQRT2
           for j in range(2)]
    for got, expected in zip(g_scores, (-0.2329, 0.0491, 0.1838)):
        assert abs(got - expected) < 8e-5, (got, expected)
    for got, expected in zip(g_q, (-0.1647, 0.0347)):
        assert abs(got - expected) < 5e-5, (got, expected)
    assert abs(sum(g_scores)) < 1e-12

    for j in range(2):
        q = Q.copy()
        def varying(value):
            q[j] = value
            return forward(q, K)[0]
        assert abs(derivative(varying, Q[j]) - g_q[j]) < 1e-7
    for i in range(3):
        for j in range(2):
            keys = [row.copy() for row in K]
            def varying(value):
                keys[i][j] = value
                return forward(Q, keys)[0]
            target = g_scores[i] * Q[j] / SQRT2
            assert abs(derivative(varying, K[i][j]) - target) < 1e-7

    x = [1.0, 2.0, 3.0]
    expected = [1 / 6 / sqrt(2 / 3), -1 / 3 / sqrt(2 / 3),
                1 / 6 / sqrt(2 / 3)]
    for j in range(3):
        inputs = x.copy()
        def varying(value):
            inputs[j] = value
            return layernorm(inputs)[0]
        assert abs(derivative(varying, x[j]) - expected[j]) < 1e-7
    print("Attention backprop QA passed: Softmax, Q/K and LayerNorm finite differences")


if __name__ == "__main__":
    main()
