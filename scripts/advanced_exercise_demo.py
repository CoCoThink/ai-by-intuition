#!/usr/bin/env python3
"""Offline reference experiments for the open training/post-training exercises.

Run from the repository root: python3 scripts/advanced_exercise_demo.py
All model weights, samples and verifier rates are teaching fixtures.
"""
from __future__ import annotations

from itertools import product
import math
import numpy as np

from teaching_reference import LR, backward, forward, norm, parameters, softmax
from teaching_trace import train


def joint_training(steps=200):
    samples = (((2, 4, 5), (4, 5, 3)), ((2, 5, 4), (5, 4, 3)))
    weights = parameters()
    trace = {}
    for step in range(steps + 1):
        states = [forward(weights, ids=ids, targets=targets) for ids, targets in samples]
        trace[step] = {
            'loss': float(np.mean([state['loss'] for state in states])),
            'first_probs': states[0]['probs'][0].copy(),
            'predictions': [state['probs'].argmax(axis=1) + 1 for state in states],
        }
        assert np.array_equal(states[0]['probs'][0], states[1]['probs'][0])
        if step == steps:
            break
        gradients = [backward(weights, state) for state in states]
        # Both gradients use the same old weights, before any parameter changes.
        for name in weights:
            weights[name] -= LR * (gradients[0][name] + gradients[1][name]) / 2
    return weights, trace


def attention_interventions():
    weights = train(steps=20)
    state = forward(weights)
    results = {}
    for mode in ('original', 'remove-flower', 'uniform'):
        attention = state['a'].copy()
        if mode == 'remove-flower':
            attention[2, 1] = 0
            attention[2] /= attention[2].sum()
        elif mode == 'uniform':
            attention[2] = 1 / 3
        r = state['x'] + (attention @ state['v']) @ weights['Wo']
        h = r + np.maximum(norm(r) @ weights['Wup'], 0) @ weights['Wdown']
        probabilities = softmax(h @ weights['Wout'])
        assert np.allclose(probabilities[:2], state['probs'][:2])
        results[mode] = (float(probabilities[2, 2]), float(-np.log(probabilities[2, 2])))
    return results


def verifier_outcomes(n, true_accept, false_accept):
    """Enumerate correct acceptance, wrong acceptance and rejection per draw."""
    rates = (true_accept, false_accept, 1 - true_accept - false_accept)
    result = np.zeros(3)  # correct delivery, wrong delivery, no delivery
    for events in product(range(3), repeat=n):
        probability = math.prod(rates[event] for event in events)
        first = next((event for event in events if event != 2), 2)
        result[first] += probability
    return result


def verifier_switch_rate():
    """Match correct-delivery rates for the fixed six-vs-four budget plans."""
    target = verifier_outcomes(4, .3 * .8, 0)[0]
    low, high = 0., 1.
    while high - low > 1e-12:
        rate = (low + high) / 2
        if verifier_outcomes(6, .3, .7 * rate)[0] > target:
            low = rate
        else:
            high = rate
    return (low + high) / 2


def reward_audit():
    chosen = np.array([0, 1, 0, 2])  # answers 42, 41, 42, 50
    results = {}
    for mode, rewards in (('correct', np.array([1., 0., 1., 0.])),
                          ('buggy', np.array([0., 1., 0., 0.]))):
        advantages = (rewards - rewards.mean()) / rewards.std()
        gradient = (advantages[:, None] * (1 / 3 - np.eye(3)[chosen])).mean(axis=0)
        probabilities = softmax(-.2 * gradient)
        results[mode] = {'advantages': advantages, 'gradient': gradient,
                         'probabilities': probabilities}
    return results


def run_checks():
    weights, trace = joint_training()
    assert trace[200]['loss'] >= math.log(2) / 3
    # Independently differentiate the actual two-sequence mean loss.
    samples = (((2, 4, 5), (4, 5, 3)), ((2, 5, 4), (5, 4, 3)))
    grads = [backward(weights, forward(weights, ids=i, targets=t)) for i, t in samples]
    for name, index in (('E', (1, 0)), ('Wq', (0, 0)), ('Wout', (0, 0))):
        old, epsilon = weights[name][index], 1e-5
        values = []
        for sign in (1, -1):
            weights[name][index] = old + sign * epsilon
            values.append(np.mean([forward(weights, ids=i, targets=t)['loss'] for i, t in samples]))
        weights[name][index] = old
        numerical = (values[0] - values[1]) / (2 * epsilon)
        assert abs(numerical - (grads[0][name][index] + grads[1][name][index]) / 2) < 1e-6
    intervention = attention_interventions()
    base = forward(train(steps=20))
    assert np.isclose(intervention['original'][0], base['probs'][2, 2])
    assert intervention['remove-flower'][1] < intervention['original'][1]
    coarse = verifier_outcomes(6, .3, .7 * .2)
    strict = verifier_outcomes(4, .3 * .8, 0)
    assert np.isclose(coarse[0], .3 / .44 * (1 - .56**6))
    assert np.isclose(strict[0], 1 - .76**4)
    assert np.isclose(coarse.sum(), 1) and np.isclose(strict.sum(), 1)
    switch = verifier_switch_rate()
    rejection = .7 * (1 - switch)
    # Check the enumerated crossing against the independent geometric sum.
    assert abs(.3 * sum(rejection**k for k in range(6)) - strict[0]) < 1e-12
    assert .193 < switch < .194
    assert verifier_outcomes(6, .3, .7 * (switch - 1e-5))[0] > strict[0]
    assert verifier_outcomes(6, .3, .7 * (switch + 1e-5))[0] < strict[0]
    rewards = reward_audit()
    chosen = np.array([0, 1, 0, 2])
    for result in rewards.values():
        def loss(logits):
            return -np.mean(result['advantages'] * np.log(softmax(logits)[chosen]))
        for column in range(3):
            delta = np.eye(3)[column] * 1e-6
            numerical = (loss(delta) - loss(-delta)) / 2e-6
            assert abs(numerical - result['gradient'][column]) < 1e-9
    assert rewards['correct']['probabilities'][0] > 1 / 3
    assert rewards['buggy']['probabilities'][0] < 1 / 3
    assert rewards['buggy']['probabilities'][1] > 1 / 3
    print('Open exercise QA: joint-loss finite differences, attention interventions, '
          'enumerated verifier outcomes, switching threshold and reward audit passed')
    return trace, intervention, coarse, strict, rewards


if __name__ == '__main__':
    trace, intervention, coarse, strict, rewards = run_checks()
    for step in (0, 20, 200):
        row = trace[step]
        print(f"joint step={step}: loss={row['loss']:.6f}; first_probs={row['first_probs']}")
    for mode, (probability, loss) in intervention.items():
        print(f'attention {mode}: target_probability={probability:.6f}; position_loss={loss:.6f}')
    print('verifiers [correct, wrong, no delivery]:', coarse, strict)
    print(f'coarse false-positive switching threshold: {verifier_switch_rate():.12f}')
    for mode, result in rewards.items():
        print(f"reward {mode}: probabilities={result['probabilities']}")
