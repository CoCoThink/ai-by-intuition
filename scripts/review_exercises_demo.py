#!/usr/bin/env python3
"""Independent numeric checks for the C1/C2 exercises and stable Softmax.

No model download, pip dependencies, or network. Run from any directory.
The values are intentional source-book test fixtures, not measured model outputs.
"""
from __future__ import annotations

from collections import Counter
from math import exp, isclose, log


def close(actual: float, expected: float, tol: float = 1e-12) -> None:
    if not isclose(actual, expected, rel_tol=tol, abs_tol=tol):
        raise AssertionError((actual, expected))


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    assert a and b and len(a[0]) == len(b)
    return [[sum(left * b[k][j] for k, left in enumerate(row))
             for j in range(len(b[0]))] for row in a]


def transpose(a: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*a)]


def bpe_pairs(corpus: list[list[str]]) -> Counter[tuple[str, str]]:
    # Pair counts must never cross document boundaries.
    return Counter(pair for row in corpus for pair in zip(row, row[1:]))


def bpe_merge(corpus: list[list[str]], pair: tuple[str, str]) -> list[list[str]]:
    merged = []
    for row in corpus:
        output = []
        i = 0
        while i < len(row):
            if i + 1 < len(row) and (row[i], row[i + 1]) == pair:
                output.append("".join(pair))
                i += 2
            else:
                output.append(row[i])
                i += 1
        merged.append(output)
    return merged


def sliding_mask(n: int, window: int) -> list[list[int]]:
    assert n >= 1 and 1 <= window <= n
    return [[int(max(0, i - window + 1) <= j <= i) for j in range(n)]
            for i in range(n)]


def main() -> None:
    # Same probabilities after adding a large common constant to every logit.
    for logits in ((1000, 1001), (6000, 6001)):
        maximum = max(logits)
        exponents = [exp(value - maximum) for value in logits]
        probabilities = [value / sum(exponents) for value in exponents]
        close(probabilities[0], .2689414213699951)
        close(probabilities[1], .7310585786300049)
        loss = maximum - logits[0] + log(sum(exponents))
        close(loss, 1.3132616875182228)
    # Probability underflows here, but logits-based cross-entropy remains finite.
    close(exp(-1000), 0)
    close(1000 + log(1 + exp(-1000)), 1000)

    # C1-15. Non-orthogonal rows: XX^T is symmetric, XWX^T is not for asymmetric W.
    x = [[1, 2], [0, 1], [1, -1]]
    gram = matmul(x, transpose(x))
    assert gram == [[5, 2, -1], [2, 1, -1], [-1, -1, 2]] == transpose(gram)
    w = [[1, 1], [0, 1]]
    assert matmul(x, w) == [[1, 3], [0, 1], [1, 0]]
    s = matmul(matmul(x, w), transpose(x))
    assert s == [[7, 3, -2], [2, 1, -1], [1, 0, 1]] and s != transpose(s)

    # C1-16. Recompute pair frequency before a single BPE merge.
    corpus = [["a", "a", "b"], ["a", "b"]]
    pairs = bpe_pairs(corpus)
    assert pairs == Counter({("a", "a"): 1, ("a", "b"): 2})
    assert bpe_merge(corpus, ("a", "b")) == [["a", "ab"], ["ab"]]

    # C2-17. Changed RAG query: Q1 is excluded by top-2.
    q = [[0.2, 1.0]]
    documents = [[1, 0], [0, 1], [0.8, 0.8]]
    scores = matmul(q, transpose(documents))[0]
    for got, wanted in zip(scores, (0.2, 1, 0.96)):
        close(got, wanted)
    rank = sorted(range(3), key=lambda i: (-scores[i], i))
    assert rank == [1, 2, 0]   # Q2, Q3, Q1

    # C2-18. A five-token causal window of width two has nine visible pairs.
    mask = sliding_mask(5, 2)
    assert mask == [[1, 0, 0, 0, 0],
                    [1, 1, 0, 0, 0],
                    [0, 1, 1, 0, 0],
                    [0, 0, 1, 1, 0],
                    [0, 0, 0, 1, 1]]
    assert sum(map(sum, mask)) == 9
    # C2-20 programming extension: same length, window 3 instead of 2.
    mask3 = sliding_mask(5, 3)
    assert list(map(sum, mask3)) == [1, 2, 3, 3, 3]
    assert sum(map(sum, mask3)) == 12

    # C2-19. Softmax/cross-entropy logit gradient p - y; C2-5 loss comparison.
    p, y = (0.2, 0.5, 0.3), (1, 0, 0)
    for got, wanted in zip([a - b for a, b in zip(p, y)], (-0.8, 0.5, 0.3)):
        close(got, wanted)
    close(-log(0.2) - (-log(0.8)), log(4))

    # Rewritten transfer items: FFN with a negative unit, RNN decay, clipping.
    hidden = matmul([[2, 1]], [[1, 0, 1], [0, 1, -3]])[0]
    assert hidden == [2, 1, -1]
    down = [[2, 0], [0, 1], [1, 1]]
    assert matmul([[max(0, v) for v in hidden]], down)[0] == [4, 1]
    assert matmul([hidden], down)[0] == [3, 0]
    assert min(t for t in range(1, 40) if 0.8 ** (t - 1) < 0.1) == 12
    scale = 6.5 / (5 ** 2 + 12 ** 2) ** 0.5
    close(5 * scale, 2.5); close(12 * scale, 6)
    assert min(n for n in range(1, 30) if 0.7 ** n <= 0.1) == 7
    w = 1.0
    for rate in (0.01, 0.02, 0.03):
        w -= rate * 2 * w
    close(w, 0.884352)
    close((1 - 0.1 * 0.05) * 4 - 0.1, 3.88)   # AdamW; L2-in-Adam gives 4 - 0.1
    logits = (0.5, 4.5)                        # ICL query C, W_out = 5 I
    close(exp(logits[1]) / (exp(logits[0]) + exp(logits[1])), 0.9820137900379085)
    close(1 / (1 + exp(-2.5)), 0.9241418199787566)
    assert 24 * 2 * 64 * 2 * 2 == 12288 and 2 * 12288 * 32768 == 805306368

    # Additional guard on the new asymmetric Q/K reading calculation.
    q_rows = [[1, 0], [0, 1], [1, 1]]
    k_rows = [[1, 0], [1, 1], [2, 1]]
    values = [[1, 0], [0, 1], [1, 1]]
    raw = matmul(q_rows, transpose(k_rows))
    assert raw == [[1, 1, 2], [0, 1, 1], [1, 2, 3]]
    assert raw[0][1] == 1 != raw[1][0]
    last = [exp(v - 3) for v in raw[-1]]
    last = [v / sum(last) for v in last]
    read = matmul([last], values)[0]
    close(read[0], 0.7552715289452023)
    close(read[1], 0.9099694268296196)

    print("Review exercises QA passed: C1-15/16, C2-17/18/19/20, rewritten transfer items, asymmetric Q/K, stable Softmax")


if __name__ == "__main__":
    main()
