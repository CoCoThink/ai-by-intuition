#!/usr/bin/env python3
"""Enumerate the book's 17 + 25 Best-of-N example; no network or dependencies."""
from itertools import product
from math import ceil, isclose, log

CANDIDATES = (41, 42, 43, 50)  # Uniform teaching distribution, p(correct) = 1/4.


def verify(answer):
    return answer == 17 + 25


def select(answers, verifier=verify):
    return next((answer for answer in answers if verifier(answer)), None)


def enumerate_success(n, *, copied=False, verifier=verify):
    streams = product(CANDIDATES, repeat=1 if copied else n)
    total = correct = 0
    for stream in streams:
        answers = stream * n if copied else stream
        correct += select(answers, verifier) == 42
        total += 1
    return correct / total


def main():
    print('N   independent/perfect   copied/perfect   independent/faulty')
    for n in (1, 2, 4, 8):
        independent = enumerate_success(n)
        copied = enumerate_success(n, copied=True)
        # Faulty verifier accepts 41 and 43 as well; choose first passing answer.
        faulty = enumerate_success(n, verifier=lambda answer: abs(answer - 42) <= 1)
        assert isclose(independent, 1 - .75 ** n)
        assert copied == .25
        assert isclose(faulty, (1 - .25 ** n) / 3)
        print(f'{n:<3} {independent:>18.6f} {copied:>16.6f} {faulty:>21.6f}')
    minimum = ceil(log(.1) / log(.75))
    assert minimum == 9 and 1 - .75 ** 8 < .9 <= 1 - .75 ** minimum
    assert isclose(1 - .75 ** 16, .9899774042423815)
    print(f'90% target: N >= {minimum}; N=8 costs 8 * 128 = {8 * 128} output tokens')


if __name__ == '__main__':
    main()
