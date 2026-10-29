#!/usr/bin/env python3
"""Independent row-vector memory numeric regression, no external dependencies."""
from math import isclose, sqrt


def mul(row, matrix):
    assert len(row) == len(matrix)
    return tuple(sum(row[i] * matrix[i][j] for i in range(len(row)))
                 for j in range(len(matrix[0])))


def outer(k, v):
    return tuple(tuple(a * b for b in v) for a in k)


def plus(a, b):
    return tuple(tuple(x + y for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


def close(actual, expected):
    assert all(isclose(a, b, abs_tol=1e-12) for a, b in zip(actual, expected))


def main():
    k_a, v_a = (1, 0), (1, 0)
    k_b, v_b = (0.6, 0.8), (0, 1)
    state = plus(outer(k_a, v_a), outer(k_b, v_b))
    assert state == ((1.0, 0.6), (0.0, 0.8))
    close(mul(k_a, state), (1, 0.6))
    close(mul(k_b, state), (0.6, 1))  # Modern-architecture chapter: additive crosstalk on B.
    better = ((1, 0), (-0.75, 1.25))
    close(mul(k_a, better), v_a)
    close(mul(k_b, better), v_b)
    # Two sequential Delta writes: B correct, but the previously learned A degrades.
    eta = 1.0
    delta_state = outer(k_a, v_a)
    residual_b = tuple(v - r for v, r in zip(v_b, mul(k_b, delta_state)))
    close(residual_b, (-0.6, 1.0))
    delta_state = plus(delta_state, outer(k_b, residual_b))
    close(delta_state[0], (0.64, 0.6))
    close(delta_state[1], (-0.48, 0.8))
    close(mul(k_b, delta_state), v_b)
    close(mul(k_a, delta_state), (0.64, 0.6))
    assert isclose(sqrt(0.36**2 + 0.6**2), 0.6997142273814361)
    # Check the gradient interpretation independently with finite differences.
    key, target = k_b, v_b
    old = ((1., 0.), (0., 0.))
    residual = tuple(v - r for v, r in zip(target, mul(key, old)))
    expected_gradient = outer(key, tuple(-r for r in residual))
    def objective(matrix):
        return sum((r - v)**2 for r, v in zip(mul(key, matrix), target)) / 2
    for i in range(2):
        for j in range(2):
            hi, lo = [list(row) for row in old], [list(row) for row in old]
            hi[i][j] += 1e-6
            lo[i][j] -= 1e-6
            assert isclose((objective(hi) - objective(lo)) / 2e-6,
                           expected_gradient[i][j], abs_tol=1e-9)
    # Recompute the actual printed full-cycle table, including its sampling time.
    from pathlib import Path
    import re
    source = (Path(__file__).resolve().parents[1] /
              'book/chapters/06-better-linear-memory.tex').read_text()
    printed = {int(n): (float(a), float(b)) for n, a, b in
               re.findall(r'^(\d+) & ([0-9.]+) & ([0-9.]+)\\\\', source, re.M)}
    assert set(printed) == {1, 2, 3, 5}
    delta_state = ((0., 0.), (0., 0.))
    for cycle in range(1, 92):
        for key, value in ((k_a, v_a), (k_b, v_b)):
            residual = tuple(v - r for v, r in zip(value, mul(key, delta_state)))
            delta_state = plus(delta_state, outer(key, residual))
        if cycle in printed:
            errors = tuple(sqrt(sum((r-v)**2 for r, v in zip(mul(k, delta_state), val)))
                           for k, val in ((k_a, v_a), (k_b, v_b)))
            assert all(abs(got - want) < 5.1e-7
                       for got, want in zip(errors, printed[cycle])), (cycle, errors)
            print(f'Delta A→B cycle {cycle}: A error={errors[0]:.6f}, B error={errors[1]:.6f}')
    close(mul(k_a, delta_state), v_a)
    close(mul(k_b, delta_state), v_b)
    for got, want in zip(delta_state, better):
        close(got, want)

    q, keys, values = (1, -1), ((1, 0), (0.6, 0.8)), ((2, 1), (0, 3))
    scores = tuple(sum(a * b for a, b in zip(q, k)) for k in keys)
    close(scores, (1, -0.2))
    close(mul(scores, values), (2, 0.4))
    close(mul(tuple(max(0, v) for v in scores), values), (2, 1))
    prefix = plus(outer((1, 0), (2, 0)), outer((0, 1), (0, 3)))
    close(mul((1, 1), prefix), (2, 3))
    close(mul((.5, .5), ((2, 0), (0, 3))), (1, 1.5))
    print("Row-vector associative-memory QA passed")


if __name__ == "__main__":
    main()
