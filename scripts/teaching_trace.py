#!/usr/bin/env python3
"""Emit the canonical 0-to-20-step loss and greedy predictions; requires numpy.

Options:
  --attention          also print the 3x3 attention matrix at steps 0 and 20
  --freeze Wq,Wk       keep the listed tensors at their initial values
  --only Wq,Wk         train only the listed tensors (all others frozen)
  --generate           after training, greedily generate from prompt [2]
                       until the 3-row position table P is exhausted
  --lr 0.2             learning rate (default: the book's 0.04)
  --ids 2,5,4          train on other input IDs (exactly 3, vocabulary 1..5);
                       targets default to the next IDs followed by 3 ("。")
  --targets 5,4,3      explicit targets for --ids
"""
import argparse
import numpy as np
from teaching_reference import IDS, LR, TARGETS, VOCAB, backward, forward, parameters

NAMES = tuple(parameters())


def names(text):
    chosen = tuple(n for n in text.split(',') if n)
    unknown = set(chosen) - set(NAMES)
    if unknown:
        raise argparse.ArgumentTypeError(f'unknown tensors {sorted(unknown)}; choose from {NAMES}')
    return chosen


def id_list(text):
    try:
        chosen = tuple(int(n) for n in text.split(','))
    except ValueError:
        raise argparse.ArgumentTypeError('use comma-separated integers, e.g. 2,5,4')
    if len(chosen) != 3 or not all(1 <= n <= len(VOCAB) for n in chosen):
        raise argparse.ArgumentTypeError(f'need exactly 3 IDs in 1..{len(VOCAB)} (P has 3 rows)')
    return chosen


def train(steps=20, trainable=NAMES, on_step=None, lr=LR, ids=IDS, targets=TARGETS):
    """Full-batch SGD on the 3-position fixture; frozen tensors keep initial values."""
    weights = parameters()
    for step in range(steps + 1):
        state = forward(weights, ids=ids, targets=targets)
        if on_step:
            on_step(step, state)
        if step != steps:
            grads = backward(weights, state)
            for name in trainable:
                weights[name] -= lr * grads[name]
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
    parser.add_argument('--lr', type=float, default=LR)
    parser.add_argument('--ids', type=id_list, default=IDS)
    parser.add_argument('--targets', type=id_list, default=None)
    args = parser.parse_args()
    if args.targets is not None and args.ids == IDS:
        parser.error('--targets requires --ids')
    targets = args.targets or (TARGETS if args.ids == IDS else args.ids[1:] + (3,))
    if args.lr != LR or args.ids != IDS:
        print(f'lr={args.lr} ids={list(args.ids)} targets={list(targets)}')
    trainable = args.only if args.only is not None else tuple(n for n in NAMES if n not in args.freeze)
    if set(trainable) != set(NAMES):
        print('trainable:', ','.join(trainable))

    def show(step, state):
        predictions = (np.argmax(state['probs'], axis=1) + 1).tolist()
        print(f"{step:02d} {state['loss']:.6f} {predictions}")
        if args.attention and step in (0, 20):
            print('attention', np.array2string(state['a'], precision=6))

    weights = train(trainable=trainable, on_step=show, lr=args.lr, ids=args.ids, targets=targets)
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
