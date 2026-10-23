#!/usr/bin/env python3
"""Replay a minimal BPE pair-frequency merge (illustrative character tokens).

Uses two document sequences and never joins across document boundaries.
Run: python3 scripts/bpe_demo.py
"""
from __future__ import annotations
from collections import Counter

corpus = [["a", "b", "a", "b"], ["a", "b"]]
vocab = {"a", "b"}


def pair_frequencies(documents: list[list[str]]) -> Counter[tuple[str, str]]:
    return Counter(pair for tokens in documents for pair in zip(tokens, tokens[1:]))


def merge(tokens: list[str], pair: tuple[str, str]) -> list[str]:
    output: list[str] = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens) and (tokens[i], tokens[i + 1]) == pair:
            output.append("".join(pair))
            i += 2
        else:
            output.append(tokens[i])
            i += 1
    return output


def main() -> None:
    expected_pairs = [("a", "b"), ("ab", "ab")]
    for round_no, expected in enumerate(expected_pairs, 1):
        counts = pair_frequencies(corpus)
        selected = max(sorted(counts), key=lambda pair: counts[pair])
        assert selected == expected, (round_no, counts)
        vocab.add("".join(selected))
        corpus[:] = [merge(tokens, selected) for tokens in corpus]
        print(f"round {round_no}: counts={dict(counts)} choose={selected}")
        print(f"  corpus={corpus} vocab={sorted(vocab)}")

    assert corpus == [["abab"], ["ab"]]
    assert vocab == {"a", "b", "ab", "abab"}


if __name__ == "__main__":
    main()
