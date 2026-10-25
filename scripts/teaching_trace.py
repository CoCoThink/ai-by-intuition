#!/usr/bin/env python3
"""Emit the canonical 0-to-20-step loss and greedy predictions; requires numpy."""
import argparse
import numpy as np
from teaching_reference import LR, backward, forward, parameters

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--attention",action="store_true")
args=parser.parse_args()
weights = parameters()
for step in range(21):
    state = forward(weights)
    predictions = (np.argmax(state["probs"], axis=1) + 1).tolist()
    print(f"{step:02d} {state['loss']:.6f} {predictions}")
    if args.attention and step in (0,20):
        print("attention",np.array2string(state["a"],precision=6))
    if step != 20:
        grads = backward(weights, state)
        for name in weights:
            weights[name] -= LR * grads[name]
