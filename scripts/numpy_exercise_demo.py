#!/usr/bin/env python3
"""Execute the NumPy programs printed in the exercise answers and audit them.

The canonical implementations live in book/exercises.json. Checks use finite
differences, interventions on future inputs, and the closed-form Delta update.
No model download, paid API, or automatic differentiation is needed.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def printed_program(exercises, key):
    solution = exercises[key]['solution']
    blocks = re.findall(r'\\begin\{verbatim\}\n(.*?)\\end\{verbatim\}', solution, re.S)
    assert len(blocks) == 1, key
    namespace = {}
    exec(compile(blocks[0], f'exercise:{key}', 'exec'), namespace)
    return namespace


def run_checks():
    exercises = {r['key']: r for r in json.loads((ROOT / 'book/exercises.json').read_text())}
    ce = printed_program(exercises, 'one-hot-gradient-target')
    objective, z, ids = ce['loss_grad'], ce['z'], ce['ids']
    loss, gradient = objective(z, ids)
    assert np.allclose(gradient.sum(axis=1), 0)
    assert np.isclose(loss, (np.log(2) + np.log(2 + np.e)) / 2)
    assert f'{loss:.6f}' in exercises['one-hot-gradient-target']['solution']
    shifted_loss, shifted_gradient = objective(z + 10_000, ids)
    assert np.isclose(shifted_loss, loss) and np.allclose(shifted_gradient, gradient)
    largest = 0.
    for index in np.ndindex(z.shape):
        perturbation = np.zeros_like(z)
        perturbation[index] = 1e-5
        numerical = (objective(z + perturbation, ids)[0]
                     - objective(z - perturbation, ids)[0]) / 2e-5
        largest = max(largest, abs(numerical - gradient[index]))
    assert largest < 1e-7, largest
    # A confident but wrong prediction must keep its finite logit-space loss.
    extreme_loss, extreme_gradient = objective(np.array([[1000., -1000.]]), np.array([2]))
    assert extreme_loss == 2000. and np.array_equal(extreme_gradient, [[1., -1.]])

    attention = printed_program(exercises, 'batch-softmax-recompute')
    read, scores, values = attention['read'], attention['scores'], attention['values']
    expected = np.array([[.5, .25, .25], [.2, .6, .2], [1/6, 1/6, 2/3]])
    causal = np.array([[1., 0., 0.], [.25, .75, 0.], [1/6, 1/6, 2/3]])
    assert np.allclose(attention['a'], expected)
    assert np.allclose(attention['ac'], causal)
    assert np.allclose(attention['y'], [[.75, .5], [.4, .8], [5/6, 5/6]])
    assert np.allclose(attention['yc'], [[1., 0.], [.25, .75], [5/6, 5/6]])
    # Intervene on both a future score and a future Value. Earlier outputs must
    # stay fixed, including when the masked score would dominate the Softmax.
    altered_scores, altered_values = scores.copy(), values.copy()
    altered_scores[:2, 2] += 1000
    altered_values[2] = 100., -100.
    altered_a, altered_y = read(altered_scores, altered_values, causal=True)
    assert np.allclose(altered_y[:2], attention['yc'][:2])
    assert not np.allclose(altered_y[2], attention['yc'][2])
    assert np.allclose(altered_a.sum(axis=1), 1)
    assert not np.any(altered_a[np.triu_indices(3, 1)])

    delta = printed_program(exercises, 'delta-write-order')
    keys, values, write = delta['keys'], delta['values'], delta['write']
    expected_ab = np.array([[.64, .6], [-.48, .8]])
    expected_ba = np.diag([1., .8])
    assert np.allclose(delta['ab'], expected_ab)
    assert np.allclose(delta['ba'], expected_ba)
    assert np.allclose(keys[1] @ delta['ab'], values[1])
    assert np.allclose(keys[0] @ delta['ba'], values[0])
    assert np.isclose(np.linalg.norm(keys[0] @ delta['ab'] - values[0]), np.sqrt(.4896))
    assert np.isclose(np.linalg.norm(keys[1] @ delta['ba'] - values[1]), np.sqrt(.4896))
    for order in ([0, 1], [1, 0]):
        orthogonal = np.eye(2)[order]
        state = write(orthogonal, values[order])
        assert np.allclose(np.eye(2) @ state, values)
    print(f'Printed NumPy: loss={loss:.6f}; 6 finite-difference derivatives, '
          f'max error={largest:.2e}; causal interventions and both Delta orders passed')


if __name__ == '__main__':
    run_checks()
