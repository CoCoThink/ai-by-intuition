#!/usr/bin/env python3
"""Learn to select a relevant record when uniform averaging loses its binding.

The four training cases pair opposite values with two named records, and ask
about each record in turn. Inputs have five fixed features: two key-role flags,
two query-role flags, and a scalar value. Only the final query is supervised.
The two 2x2 projection blocks and a scalar binary head are trained with SGD.
Value extraction, embeddings and the causal mask stay fixed. No learned FFN or
positional shortcut can recover a binding before the attention readout.
"""
from __future__ import annotations

from itertools import product
import numpy as np

STEPS = 2000
LR = 1.


def examples(*, complete=False):
    values = product((-1., 1.), repeat=2) if complete else ((1., -1.), (-1., 1.))
    inputs, targets = [], []
    for first, second in values:
        for query in range(2):
            x = np.zeros((3, 5))
            x[:2, :2] = np.eye(2)  # Named records: flower and window.
            x[:2, -1] = first, second
            x[2, 2 + query] = 1.  # Query has no answer/value feature.
            inputs.append(x)
            targets.append((first, second)[query])
    return np.array(inputs), np.array(targets)


def initial_parameters():
    # K=0 starts both arms at exactly uniform attention. A nonzero Q avoids the
    # zero-product stationary point that would occur if BOTH Q and K were zero.
    return {'Wq': .1 * np.eye(2), 'Wk': np.zeros((2, 2)),
            'head': np.array([1., 0.])}  # z = head[0] * context + head[1]


def forward(parameters, x, target, *, uniform=False):
    q = x[:, 2, 2:4] @ parameters['Wq']
    k = x[:, :, :2] @ parameters['Wk']
    v = x[:, :, -1]
    scores = np.einsum('bd,btd->bt', q, k) / np.sqrt(2.)
    if uniform:
        scores = np.zeros_like(scores)
    exp = np.exp(scores - scores.max(axis=1, keepdims=True))
    weights = exp / exp.sum(axis=1, keepdims=True)
    context = (weights * v).sum(axis=1)
    logits = parameters['head'][0] * context + parameters['head'][1]
    loss = np.logaddexp(0., -target * logits).mean()
    return dict(q=q, k=k, v=v, weights=weights, context=context, logits=logits,
                loss=float(loss), correct_probs=np.exp(-np.logaddexp(0., -target * logits)))


def backward(parameters, x, target, state, *, uniform=False):
    gz = -target * np.exp(-np.logaddexp(0., target * state['logits'])) / len(x)
    gc = gz * parameters['head'][0]
    gs = state['weights'] * gc[:, None] * (state['v'] - state['context'][:, None])
    gq = np.einsum('bt,btd->bd', gs, state['k']) / np.sqrt(2.)
    gk = gs[:, :, None] * state['q'][:, None, :] / np.sqrt(2.)
    return {
        'Wq': np.zeros((2, 2)) if uniform else x[:, 2, 2:4].T @ gq,
        'Wk': np.zeros((2, 2)) if uniform else np.einsum('bti,btd->id', x[:, :, :2], gk),
        'head': np.array([(gz * state['context']).sum(), gz.sum()]),
    }


def train(*, uniform=False, steps=STEPS):
    x, target = examples()
    parameters = initial_parameters()
    for _ in range(steps):
        state = forward(parameters, x, target, uniform=uniform)
        gradient = backward(parameters, x, target, state, uniform=uniform)
        parameters = {name: value - LR * gradient[name] for name, value in parameters.items()}
    return parameters, forward(parameters, x, target, uniform=uniform)


def check_gradients():
    x, target = examples()
    probe = {'Wq': np.array([[.3, -.2], [.1, .4]]),
             'Wk': np.array([[.2, .1], [-.3, .5]]), 'head': np.array([.7, .2])}
    state = forward(probe, x, target)
    gradient = backward(probe, x, target, state)
    largest = 0.
    for name, array in probe.items():
        for index in np.ndindex(array.shape):
            old = array[index]
            array[index] = old + 1e-6
            high = forward(probe, x, target)['loss']
            array[index] = old - 1e-6
            low = forward(probe, x, target)['loss']
            array[index] = old
            largest = max(largest, abs((high - low) / 2e-6 - gradient[name][index]))
    assert largest < 1e-8, largest
    return largest


def run_checks():
    x, target = examples()
    initial = initial_parameters()
    uniform_parameters, uniform = train(uniform=True)
    learned_parameters, learned = train()
    # Each same-query pair has an identical mean even of the FULL input vector.
    assert np.array_equal(x[0].mean(axis=0), x[2].mean(axis=0))
    assert np.array_equal(x[1].mean(axis=0), x[3].mean(axis=0))
    assert np.array_equal(x[0, 2], x[2, 2]) and target[0] != target[2]
    assert np.allclose(uniform['weights'], 1/3) and np.all(uniform['context'] == 0)
    assert abs(uniform['loss'] - np.log(2)) < 1e-12
    assert learned['loss'] < .001 and np.all(learned['correct_probs'] > .999)
    # Q responds to the asked-for record; K matches its name, not its position.
    assert learned['weights'][0, 0] > .98 and learned['weights'][1, 1] > .98
    assert learned['weights'][0, 1] < .001 and learned['weights'][1, 0] < .001
    for name in ('Wq', 'Wk'):
        assert not np.allclose(initial[name], learned_parameters[name]), name
        assert np.array_equal(initial[name], uniform_parameters[name]), name
    # Intervene AFTER training: restoring equal weights destroys the fitted rule.
    restored = forward(learned_parameters, x, target, uniform=True)
    assert abs(restored['loss'] - np.log(2)) < 1e-12
    for name in ('Wq', 'Wk'):
        zeroed = {key: value.copy() for key, value in learned_parameters.items()}
        zeroed[name][:] = 0.
        assert abs(forward(zeroed, x, target)['loss'] - np.log(2)) < 1e-12
    # Test unseen same-sign values and swapped source order; this blocks a
    # fixed-slot shortcut and checks the learned query/key binding itself.
    test_x, test_target = examples(complete=True)
    test = forward(learned_parameters, test_x, test_target)
    swapped = forward(learned_parameters, test_x[:, [1, 0, 2]], test_target)
    assert np.allclose(swapped['logits'], test['logits'])
    assert np.all(test_target * test['logits'] > 0)
    assert np.all(test['correct_probs'] > .999)
    error = check_gradients()
    print(f'selection/uniform: loss={uniform["loss"]:.6f}')
    print(f'selection/learned QK: loss={learned["loss"]:.6f}, '
          f'min correct probability={learned["correct_probs"].min():.6f}')
    print('query flower weights:', np.round(learned['weights'][0], 6))
    print('query window weights:', np.round(learned['weights'][1], 6))
    print(f'restore uniform: loss={restored["loss"]:.6f}; '
          f'10 parameter gradients checked, max error={error:.2e}; 8/8 test bindings correct')
    return uniform, learned, restored


if __name__ == '__main__':
    run_checks()
