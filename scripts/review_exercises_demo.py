#!/usr/bin/env python3
"""Independent numeric checks for the five added B1/B2 review exercises.

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
    # B1-15. A different input X still has a symmetric Gram score matrix.
    x = [[1, 1], [1, -1]]
    gram = matmul(x, transpose(x))
    assert gram == [[2, 0], [0, 2]]

    # B1-16. Recompute pair frequency before a single BPE merge.
    corpus = [["a", "a", "b"], ["a", "b"]]
    pairs = bpe_pairs(corpus)
    assert pairs == Counter({("a", "a"): 1, ("a", "b"): 2})
    assert bpe_merge(corpus, ("a", "b")) == [["a", "ab"], ["ab"]]

    # B2-17. Changed RAG query: Q1 is excluded by top-2.
    q = [[0.2, 1.0]]
    documents = [[1, 0], [0, 1], [0.8, 0.8]]
    scores = matmul(q, transpose(documents))[0]
    for got, wanted in zip(scores, (0.2, 1, 0.96)):
        close(got, wanted)
    rank = sorted(range(3), key=lambda i: (-scores[i], i))
    assert rank == [1, 2, 0]   # Q2, Q3, Q1

    # B2-18. A five-token causal window of width two has nine visible pairs.
    mask = sliding_mask(5, 2)
    assert mask == [[1, 0, 0, 0, 0],
                    [1, 1, 0, 0, 0],
                    [0, 1, 1, 0, 0],
                    [0, 0, 1, 1, 0],
                    [0, 0, 0, 1, 1]]
    assert sum(map(sum, mask)) == 9

    # B2-19. Cross-entropy of an exactly uniform thousand-word vocabulary.
    close(-log(1 / 1000), log(1000))
    close(log(1000), 6.907755278982137)

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

    print("Review exercises QA passed: B1-15/16, B2-17/18/19, asymmetric Q/K")


if __name__ == "__main__":
    main()
