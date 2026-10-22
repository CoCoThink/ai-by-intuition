#!/usr/bin/env python3
"""Deterministic, inspectable decoder-only Transformer teaching fixture.

Run: python3 scripts/teaching_reference.py [--json]
Requires numpy. One causal head, one Pre-LN block, full 3-position loss.
Every parameter here is invented for teaching, not a pretrained model weight.
"""
from __future__ import annotations
import argparse
import json
import math
import numpy as np

IDS = (1, 3, 4)
TARGETS = (3, 4, 2)
VOCAB = ('其他', '春天', '。', '花', '开了')
EPS = 1e-5
LR = 0.04


def parameters():
    """Only authoritative source of initial toy weights and position vectors."""
    return {
        'E': np.array([[0., 0., 0.], [1.2, 0., -.2], [.2, -.4, .7],
                       [-.3, 1.1, .2], [.15, -.2, 1.25]]),
        'P': np.array([[.1, .05, -.1], [0., -.05, .12], [-.12, .1, .07]]),
        'Wq': np.array([[.8, .2, -.1], [.1, .9, .25], [-.1, .15, .8]]),
        'Wk': np.array([[.85, 0., .2], [-.1, .9, 0.], [.15, .2, .75]]),
        'Wv': np.array([[1., .2, 0.], [0., .9, .15], [.1, -.2, .85]]),
        'Wo': np.array([[.9, 0., .1], [.1, .85, 0.], [0., .15, .95]]),
        'Wup': np.array([[.4, .2, -.3, .1], [-.1, .5, .15, -.25],
                         [.2, .1, .45, .3]]),
        'Wdown': np.array([[.25, -.1, .15], [-.05, .2, .1],
                           [.1, .15, .15], [.1, -.12, .18]]),
        'Wout': np.array([[0., .2, 0., .2, -.2],
                          [0., .2, 0., 1.2, -.4],
                          [0., -.1, .4, .1, .2]]),
    }


def norm(x):
    mean = x.mean(axis=-1, keepdims=True)
    centered = x - mean
    std = np.sqrt(np.mean(centered * centered, axis=-1, keepdims=True) + EPS)
    return centered / std


def norm_backward(grad, x):
    """Exact per-token LayerNorm gradient, gamma=1 and beta=0 (frozen)."""
    mean = x.mean(axis=-1, keepdims=True)
    centered = x - mean
    std = np.sqrt(np.mean(centered * centered, axis=-1, keepdims=True) + EPS)
    y = centered / std
    return (grad - grad.mean(axis=-1, keepdims=True)
            - y * (grad * y).mean(axis=-1, keepdims=True)) / std


def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def forward(weights, ids=IDS, targets=TARGETS):
    """One decoder Block. Loss averaged over every predicted position."""
    t = len(ids)
    assert 1 <= t <= weights['P'].shape[0]
    x = weights['E'][list(ids)] + weights['P'][:t]
    u = norm(x)
    q, k, v = u @ weights['Wq'], u @ weights['Wk'], u @ weights['Wv']
    scores = (q @ k.T) / math.sqrt(q.shape[1])
    mask = np.triu(np.ones((t, t), dtype=bool), k=1)
    scores[mask] = -np.inf
    a = softmax(scores)
    raw = a @ v
    r = x + raw @ weights['Wo']
    b = norm(r)
    pre = b @ weights['Wup']
    hid = np.maximum(pre, 0.)
    h = r + hid @ weights['Wdown']
    logits = h @ weights['Wout']
    probs = softmax(logits)
    loss = None if targets is None else float(-np.log(probs[np.arange(t), list(targets)]).mean())
    return locals()


def backward(weights, state):
    """Manual reverse-mode gradients, including the attention score path."""
    t = len(state['ids'])
    g = {}
    gz = state['probs'].copy()
    gz[np.arange(t), list(state['targets'])] -= 1.
    gz /= t
    g['Wout'] = state['h'].T @ gz
    gh = gz @ weights['Wout'].T
    g['Wdown'] = state['hid'].T @ gh
    ghid = gh @ weights['Wdown'].T
    gpre = ghid * (state['pre'] > 0.)
    g['Wup'] = state['b'].T @ gpre
    gb = gpre @ weights['Wup'].T
    gr = gh + norm_backward(gb, state['r'])
    g['Wo'] = state['raw'].T @ gr
    graw = gr @ weights['Wo'].T
    gv = state['a'].T @ graw
    ga = graw @ state['v'].T
    gs = state['a'] * (ga - np.sum(ga * state['a'], axis=-1, keepdims=True))
    gq = gs @ state['k'] / math.sqrt(state['q'].shape[1])
    gk = gs.T @ state['q'] / math.sqrt(state['q'].shape[1])
    g['Wq'] = state['u'].T @ gq
    g['Wk'] = state['u'].T @ gk
    g['Wv'] = state['u'].T @ gv
    gu = gq @ weights['Wq'].T + gk @ weights['Wk'].T + gv @ weights['Wv'].T
    gx = gr + norm_backward(gu, state['x'])
    g['P'] = np.zeros_like(weights['P'])
    g['P'][:t] += gx
    g['E'] = np.zeros_like(weights['E'])
    np.add.at(g['E'], list(state['ids']), gx)
    return g


def finite_difference_check(weights, grads, tol=3e-6):
    """Check one entry of every tensor against independent central differences."""
    for name, value in weights.items():
        idx = (0,) * value.ndim
        if name == 'E':
            idx = (1, 0)  # token ID 0 is unused in this example
        h = 1e-5
        old = value[idx]
        value[idx] = old + h
        high = forward(weights)['loss']
        value[idx] = old - h
        low = forward(weights)['loss']
        value[idx] = old
        numerical = (high - low) / (2 * h)
        analytical = float(grads[name][idx])
        if abs(numerical - analytical) > tol:
            raise AssertionError(f'{name}{idx}: analytic={analytical}, numerical={numerical}')


def run_checks():
    w = parameters()
    assert abs(float(np.linalg.det(w['E'][[1, 3, 4]]))) > 1e-4
    st = forward(w)
    assert st['x'].shape == (3, 3) and st['a'].shape == (3, 3)
    assert st['h'].shape == (3, 3) and st['probs'].shape == (3, 5)
    assert np.allclose(np.triu(st['a'], 1), 0.)
    assert np.allclose(st['a'].sum(axis=1), 1.)
    assert st['probs'][1, 4] < st['probs'][1, 3], 'Middle position should initially err'
    # Replacing an earlier token while leaving the last token unchanged
    # must affect last-position logits (context sensitivity).
    counter = forward(w, ids=(4, 3, 4), targets=None)
    delta = float(np.max(np.abs(counter['logits'][-1] - st['logits'][-1])))
    assert delta > 1e-4, f'Counterfactual too weak: {delta}'
    # Independent ablations: location and Value path, with everything else fixed.
    wp = {key: val.copy() for key, val in w.items()}
    wp['P'][1, 0] += .2
    position_delta = float(np.max(np.abs(forward(wp)['logits'] - st['logits'])))
    assert position_delta > 1e-4
    wv = {key: val.copy() for key, val in w.items()}
    wv['Wv'][0, 0] += .25
    value_delta = float(np.max(np.abs(forward(wv)['logits'] - st['logits'])))
    assert value_delta > 1e-4
    grads = backward(w, st)
    finite_difference_check(w, grads)
    w1 = {key: val - LR * grads[key] for key, val in w.items()}
    st1 = forward(w1)
    assert st1['loss'] < st['loss'], 'Full-sequence optimization must improve mean loss'
    assert not np.allclose(st['probs'], st1['probs'])
    return w, st, grads, w1, st1, delta, position_delta, value_delta


def report():
    w, st, grads, _, st1, delta, position_delta, value_delta = run_checks()
    return {
        'exercise': 'single-head pre-norm 3D teaching decoder',
        'token_ids': list(IDS), 'targets': list(TARGETS), 'vocab': list(VOCAB),
        'learning_rate': LR, 'layernorm_epsilon': EPS,
        'shapes': {key: list(st[key].shape) for key in
                   ('x', 'q', 'k', 'v', 'a', 'r', 'b', 'hid', 'h', 'logits', 'probs')},
        'position_losses_before': [-float(np.log(st['probs'][i, y])) for i, y in enumerate(TARGETS)],
        'position_losses_after': [-float(np.log(st1['probs'][i, y])) for i, y in enumerate(TARGETS)],
        'mean_loss_before': st['loss'], 'mean_loss_after': st1['loss'],
        'true_probabilities_before': [float(st['probs'][i, y]) for i, y in enumerate(TARGETS)],
        'true_probabilities_after': [float(st1['probs'][i, y]) for i, y in enumerate(TARGETS)],
        'attention_weights_before': st['a'].tolist(),
        'logits_before': st['logits'].tolist(),
        'gradient_norms': {key: float(np.linalg.norm(val)) for key, val in grads.items()},
        'counterfactual_last_logit_max_delta': delta,
        'position_perturbation_logit_delta': position_delta,
        'value_projection_perturbation_logit_delta': value_delta,
        'embedding_det_1_3_4': float(np.linalg.det(w['E'][[1, 3, 4]])),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='machine-readable example values')
    args = parser.parse_args()
    result = report()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print('Toy Transformer numeric QA passed (including finite differences).')
        print(f"Three-position mean loss: {result['mean_loss_before']:.6f} → {result['mean_loss_after']:.6f}")
        print('True-token probabilities before:', np.round(result['true_probabilities_before'], 6))
        print('True-token probabilities after: ', np.round(result['true_probabilities_after'], 6))
        print('Counterfactual last-logit delta:', result['counterfactual_last_logit_max_delta'])
