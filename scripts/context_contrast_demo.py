#!/usr/bin/env python3
"""Controlled context ablation: same token at same position, conflicting labels.

Only the shared binary output head is trained in both arms. The attention arm
uses fixed uniform causal attention (Q=K=0,V=input); no extra trained parameters.
This tests access to context, not a unique need for the Attention architecture.
"""
from __future__ import annotations
import numpy as np


def train(features, steps=2000, lr=1.):
    w = np.zeros((features.shape[1], 2))
    target = np.eye(2)
    for _ in range(steps):
        z = features @ w
        exp = np.exp(z - z.max(axis=1, keepdims=True))
        probs = exp / exp.sum(axis=1, keepdims=True)
        w -= lr * features.T @ (probs - target) / 2
    z = features @ w
    log_probs = z - z.max(axis=1, keepdims=True)
    log_probs -= np.log(np.exp(log_probs).sum(axis=1, keepdims=True))
    return float(-np.diag(log_probs).mean()), np.exp(log_probs)


def run_checks():
    # Coordinates: spring, winter, flower. Position 2 is identical in both rows.
    spring, winter, flower = np.eye(3)
    local = np.stack([np.r_[flower, np.zeros(3), 1.], np.r_[flower, np.zeros(3), 1.]])
    context = np.stack([np.r_[flower, (spring+flower)/2, 1.],
                        np.r_[flower, (winter+flower)/2, 1.]])
    local_loss, local_probs = train(local)
    context_loss, context_probs = train(context)
    # Any deterministic row-only network has the SAME output p at both positions.
    # -log(p(1-p))/2 >= log(2), with equality at p=1/2.
    assert local.shape == context.shape  # identical head width/parameter budget
    assert np.array_equal(local[0], local[1])
    assert np.allclose(local_probs, .5)
    assert abs(local_loss - np.log(2)) < 1e-12
    assert context_loss < .01 and np.all(context_probs.diagonal() > .99)
    print(f'row-only: loss={local_loss:.6f}, target probabilities={local_probs.diagonal()}')
    print(f'causal attention: loss={context_loss:.6f}, target probabilities={context_probs.diagonal()}')
    return local_loss, context_loss


if __name__ == '__main__':
    run_checks()
