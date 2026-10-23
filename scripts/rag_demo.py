#!/usr/bin/env python3
"""Reproducible 2D pedagogical RAG ranking and evidence-mismatch example.

No embeddings are trained; document vectors and revenues are invented fixtures.
Run from the repository root: python3 scripts/rag_demo.py
"""
from __future__ import annotations

QUERY = (1.0, 0.5)
CHUNKS = {
    "Q1": ((1.0, 0.0), 100),
    "Q2": ((0.0, 1.0), 120),
    "Q3": ((0.8, 0.8), 132),
}


def dot(a: tuple[float, float], b: tuple[float, float]) -> float:
    assert len(a) == len(b) == 2
    return sum(x * y for x, y in zip(a, b))


def main() -> None:
    scores = {name: dot(QUERY, vec) for name, (vec, _) in CHUNKS.items()}
    ranked = sorted(scores, key=lambda name: (-scores[name], name))
    assert [round(scores[name], 4) for name in ("Q1", "Q2", "Q3")] == [1, 0.5, 1.2]
    assert ranked[:2] == ["Q3", "Q1"]

    revenue = {name: amount for name, (_, amount) in CHUNKS.items()}
    incorrect = (revenue["Q3"] - revenue["Q1"]) / revenue["Q1"]
    correct = (revenue["Q3"] - revenue["Q2"]) / revenue["Q2"]
    assert round(incorrect, 6) == 0.32
    assert round(correct, 6) == 0.10

    print("query:", QUERY, "scores:", scores)
    print("top-2:", ranked[:2], "(Q2 is missing)")
    print(f"Wrong Q3 QoQ if Q1 replaces Q2: {incorrect:.0%}")
    print(f"Correct Q3 QoQ with Q2: {correct:.0%}")


if __name__ == "__main__":
    main()
