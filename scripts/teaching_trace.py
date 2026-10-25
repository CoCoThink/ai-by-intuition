#!/usr/bin/env python3
"""Emit the canonical 0-to-20-step loss and greedy predictions; requires numpy.

Options:
  --attention          also print the 3x3 attention matrix at steps 0 and 20
  --freeze Wq,Wk       keep the listed tensors at their initial values
  --only Wq,Wk         train only the listed tensors (all others frozen)
  --generate           after training, greedily generate from prompt [2]
                       until the 3-row position table P is exhausted
"""
import argparse
import numpy as np
from teaching_reference import LR, VOCAB, backward, forward, parameters

NAMES = tuple(parameters())


def names(text):
    chosen = tuple(n for n in text.split(',') if n)
    unknown = set(chosen) - set(NAMES)
    if unknown:
        raise argparse.ArgumentTypeError(f'unknown tensors {sorted(unknown)}; choose from {NAMES}')
    return chosen


def train(steps=20, trainable=NAMES, on_step=None):
    """Full-batch SGD on the 3-position fixture; frozen tensors keep initial values."""
    weights = parameters()
    for step in range(steps + 1):
        state = forward(weights)
        if on_step:
            on_step(step, state)
        if step != steps:
            grads = backward(weights, state)
            for name in trainable:
                weights[name] -= LR * grads[name]
    return weights


def greedy_generate(weights, prompt=(2,)):
    """Greedy decoding with a fixed model; stops when P_pos has no next row."""
    ids, trace = list(prompt), []
    while len(ids) <= weights['P'].shape[0]:
        state = forward(weights, ids=tuple(ids), targets=None)
        probs = state['probs'][-1]
        chosen = int(np.argmax(probs)) + 1
        trace.append(dict(context=tuple(ids), chosen=chosen, prob=float(probs[chosen - 1]),
                          probs=probs.copy(), attention=state['a'][-1].copy(),
                          k=state['k'].copy(), v=state['v'].copy()))
        ids.append(chosen)
    return ids, trace


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--attention', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--freeze', type=names, default=())
    group.add_argument('--only', type=names, default=None)
    parser.add_argument('--generate', action='store_true')
    args = parser.parse_args()
    trainable = args.only if args.only is not None else tuple(n for n in NAMES if n not in args.freeze)
    if set(trainable) != set(NAMES):
        print('trainable:', ','.join(trainable))

    def show(step, state):
        predictions = (np.argmax(state['probs'], axis=1) + 1).tolist()
        print(f"{step:02d} {state['loss']:.6f} {predictions}")
        if args.attention and step in (0, 20):
            print('attention', np.array2string(state['a'], precision=6))

    weights = train(trainable=trainable, on_step=show)
    if args.generate:
        ids, trace = greedy_generate(weights)
        for item in trace:
            t = len(item['context'])
            print(f"generate {list(item['context'])} -> {item['chosen']} "
                  f"{VOCAB[item['chosen'] - 1]} p={item['prob']:.4f} "
                  f"probs={np.array2string(item['probs'], precision=4)}")
            print(f"  last-query attention={np.array2string(item['attention'], precision=4)}"
                  f"  K row 1={np.array2string(item['k'][0], precision=4)}"
                  f"  new K row {t}={np.array2string(item['k'][-1], precision=4)}")
        print(f"stop: context {ids} has {len(ids)} tokens; P_pos has only "
              f"{weights['P'].shape[0]} rows")


if __name__ == '__main__':
    main()
