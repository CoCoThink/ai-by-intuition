#!/usr/bin/env python3
"""Emit the canonical 0-to-20-step loss and greedy predictions; requires numpy."""
import numpy as np
from teaching_reference import LR, backward, forward, parameters

weights = parameters()
for step in range(21):
    state = forward(weights)
    predictions = np.argmax(state["probs"], axis=1).tolist()
    print(f"{step:02d} {state['loss']:.6f} {predictions}")
    if step != 20:
        grads = backward(weights, state)
        for name in weights:
            weights[name] -= LR * grads[name]
