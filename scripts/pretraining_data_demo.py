#!/usr/bin/env python3
"""Reproduce the book's tiny exact/near-duplicate corpus, using only stdlib."""
from hashlib import sha256
import unicodedata

TEXTS = ('春天花开了', '春天 花 开了。', '春天的花开了', '春天花谢了')


def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', text) if c.isalnum())


def fingerprint(text):
    return sha256(normalize(text).encode('utf-8')).hexdigest()


def bigrams(text):
    text = normalize(text)
    return {text[i:i+2] for i in range(len(text)-1)}


def jaccard(left, right):
    a, b = bigrams(left), bigrams(right)
    return len(a & b) / len(a | b) if a | b else 1.0


def run_checks():
    assert fingerprint(TEXTS[0]) == fingerprint(TEXTS[1])
    assert fingerprint(TEXTS[0]) != fingerprint(TEXTS[2])
    assert jaccard(TEXTS[0], TEXTS[2]) == 0.5
    assert abs(jaccard(TEXTS[0], TEXTS[3]) - 1/3) < 1e-12
    # Similarity only proposes candidates. Human review preserves changed facts.
    for label, text in zip('ABCD', TEXTS):
        print(label, normalize(text), fingerprint(text)[:8])
    print('J(A,C)=0.500; J(A,D)=0.333; near duplicates require content review')


if __name__ == '__main__':
    run_checks()
