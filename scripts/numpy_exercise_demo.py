#!/usr/bin/env python3
"""Execute the NumPy programs printed in the exercise answers and audit them.

The canonical implementations live in book/exercises.json. Checks use finite
differences, interventions on future inputs, and the closed-form Delta update.
No model download, paid API, or automatic differentiation is needed.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def check_pdf_only_parameters(exercises):
    """Copy the printed literal and answers into files outside the checkout."""
    appendix = (ROOT / 'book/chapters/appendix-b-transformer-intermediates.tex').read_text()
    section = appendix.split(r'\label{app:parameter-literal}', 1)[1]
    literal = re.search(r'\\begin\{verbatim\}\n(.*?)\\end\{verbatim\}', section, re.S)[1]
    namespace = {}
    exec(compile(literal, 'appendix:parameter-literal', 'exec'), namespace)
    from scripts.teaching_reference import parameters
    printed, expected = namespace['parameters'](), parameters()
    assert printed.keys() == expected.keys()
    assert sum(value.size for value in printed.values()) == 99
    for key in expected:
        assert np.array_equal(printed[key], expected[key]), key
    printed['E'][0, 0] = 99
    assert namespace['parameters']()['E'][0, 0] == 0, 'calls must return fresh arrays'
    for key in ('embedding-input-change', 'causal-input-change'):
        body = exercises[key]['solution']
        code = re.search(r'\\begin\{verbatim\}\n(.*?)\\end\{verbatim\}', body, re.S)[1]
        # The exercise implementation may import NumPy and initial parameters,
        # but must compute the lookup/Block itself rather than import forward.
        for node in ast.walk(ast.parse(code)):
            if isinstance(node, ast.ImportFrom):
                assert node.module == 'scripts.teaching_reference'
                assert [(alias.name, alias.asname) for alias in node.names] == [('parameters', None)]
            elif isinstance(node, ast.Import):
                assert [alias.name for alias in node.names] == ['numpy']
        marker = 'from scripts.teaching_reference import parameters\n'
        assert code.count(marker) == 1
        code = code.replace(marker, literal + '\n', 1)
        if key == 'embedding-input-change':
            code += '\nassert np.array_equal(gradient[4], [4, 0, 0])\n'
            code += 'assert np.array_equal(output, table[[4, 3, 4]])\n'
        else:
            code += '\nassert after[2][2].argmax() == 3\n'
            code += 'assert np.isclose(after[2][2, 3], .7212, atol=5e-5)\n'
            code += 'assert all(np.allclose(a[:2], b[:2]) for a, b in zip(before, after))\n'
        with tempfile.TemporaryDirectory(prefix='pdf-only-exercise-') as directory:
            script = Path(directory) / 'answer.py'
            script.write_text(code)
            subprocess.run([sys.executable, '-I', str(script)], cwd=directory, check=True)
    print('PDF-only exercise QA: all 99 printed parameters match; C-049/C-076 run in isolated files without repository imports')


def check_extended_programs(exercises):
    """Audit printed programs using derivatives, shape controls and interventions."""
    def program(key):
        return printed_program(exercises, key)

    batch = program('mini-batch-gradient-average')
    fn, theta, x, y = (batch[k] for k in ('batch_loss_grad', 'theta', 'x', 'y'))
    assert np.allclose(batch['updated'], [1.1, .1])
    for i in range(2):
        delta = np.eye(2)[i] * 1e-5
        numerical = (fn(theta+delta, x, y)[0]-fn(theta-delta, x, y)[0])/2e-5
        assert np.isclose(numerical, batch['gradient'][i])
    assert np.allclose(fn(theta, np.tile(x, 2), np.tile(y, 2))[1], batch['gradient'])

    matrix = program('matrix-batch-calculation')
    multiply = matrix['multiply']
    assert np.array_equal(matrix['y'], [[-2, 2], [5, 4]])
    assert np.array_equal(multiply(np.ones((2, 3)), np.arange(3.)[:, None]), [[3], [3]])
    changed = matrix['x'].copy(); changed[0] = 0
    assert np.array_equal(multiply(changed, matrix['w'])[1], matrix['y'][1])
    try:
        multiply(np.zeros((2, 3)), np.zeros((2, 1)))
    except ValueError:
        pass
    else:
        raise AssertionError('incompatible dimensions accepted')

    mlp = program('mlp-linear-composition')
    objective, x, w1, w2 = (mlp[k] for k in ('mlp_loss_grad', 'x', 'w1', 'w2'))
    assert mlp['loss'] == 8.5
    assert np.array_equal(mlp['g1'], [[16, 2, 0], [8, 1, 0]])
    assert np.array_equal(mlp['g2'], [[8, 2], [4, 1], [0, 0]])
    for parameter, analytical in ((w1, mlp['g1']), (w2, mlp['g2'])):
        for index in np.ndindex(parameter.shape):
            old = parameter[index]
            parameter[index] = old + 1e-5
            plus = objective(x, w1, w2)[0]
            parameter[index] = old - 1e-5
            minus = objective(x, w1, w2)[0]
            parameter[index] = old
            assert abs((plus-minus)/2e-5-analytical[index]) < 1e-7
    assert np.allclose(np.maximum(-x @ w1, 0) @ w2, [1, 1])

    embedding = program('embedding-input-change')
    gradient = embedding['gradient']
    assert np.array_equal(gradient[3], [0, 2, 0])
    assert np.array_equal(gradient[4], [4, 0, 0])
    assert not np.any(gradient[:3])
    table = embedding['table']; saved = table.copy()
    assert np.array_equal(embedding['output'], table[[4, 3, 4]])
    embedding['lookup_and_grad'](table, [5, 4, 5], embedding['upstream'])
    assert np.array_equal(table, saved)

    block = program('causal-input-change')
    from scripts.teaching_reference import forward
    for ids, name in (([2, 4, 5], 'before'), ([2, 4, 4], 'after')):
        reference = forward(block['p'], ids, targets=None)
        for actual, key in zip(block[name], ('a', 'h', 'probs')):
            assert np.allclose(actual, reference[key])
    for before, after in zip(block['before'], block['after']):
        assert np.allclose(before[:2], after[:2])
    assert block['after'][2][2].argmax()+1 == 4
    assert np.isclose(block['after'][2][2, 3], .7212, atol=5e-5)
    try:
        block['block']([2, 4, 5, 3], block['p'])
    except ValueError:
        pass
    else:
        raise AssertionError('missing fourth position accepted')

    icl = program('icl-query-transfer')
    keys, values, head = (icl[k] for k in ('keys', 'values', 'head'))
    originals = [a.copy() for a in (keys, values, head)]
    for query, weights, probabilities in ((icl['qc'], icl['wc'], icl['pc']),
                                         (icl['qa'], icl['wa'], icl['pa'])):
        new_w, new_p = icl['distribution'](query, keys, values[::-1], head)
        assert np.allclose(new_w, weights) and np.allclose(new_p, probabilities[::-1])
    assert np.isclose(icl['pc'][1], .982014, atol=5e-7)
    assert np.isclose(icl['pa'][0], .924142, atol=5e-7)
    assert all(np.array_equal(a,b) for a,b in zip((keys,values,head), originals))

    conv = program('convolution-shared-kernel')
    assert np.array_equal(conv['before'], [[0, -1], [-1, 0]])
    assert np.array_equal(conv['delta'], [[-1, 0], [0, 1]])

    memory = program('memory-outer-shape')
    keys, values, write = (memory[k] for k in ('keys', 'values', 'outer_memory'))
    assert memory['memory'].shape == (2, 3)
    assert np.array_equal(memory['memory'], keys.T @ values)
    assert np.array_equal(memory['readout'], [1, 2, 3])
    assert np.array_equal(write(keys[::-1], values[::-1]), memory['memory'])
    assert np.array_equal(np.array([1, 0]) @ write(keys, values[::-1]), [4, 5, 6])
    print('8 further printed NumPy programs: finite differences, repeated IDs, '
          'canonical Block, ICL, pixel interventions and rectangular memory passed')


def printed_program(exercises, key):
    solution = exercises[key]['solution']
    blocks = re.findall(r'\\begin\{verbatim\}\n(.*?)\\end\{verbatim\}', solution, re.S)
    assert len(blocks) == 1, key
    namespace = {}
    exec(compile(blocks[0], f'exercise:{key}', 'exec'), namespace)
    return namespace


def run_checks():
    exercises = {r['key']: r for r in json.loads((ROOT / 'book/exercises.json').read_text())}
    check_pdf_only_parameters(exercises)
    check_extended_programs(exercises)
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
