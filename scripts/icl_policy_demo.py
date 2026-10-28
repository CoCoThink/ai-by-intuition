#!/usr/bin/env python3
"""Reproduce the book's two-record ICL read and frozen-advantage logit update."""
import numpy as np

def softmax(z):
    e=np.exp(z-np.max(z,axis=-1,keepdims=True));return e/e.sum(axis=-1,keepdims=True)

def icl_records(sequence):
    """Build records from tokens, copying only the previous position's first channel pair."""
    features = {token: np.eye(4)[i] for i, token in enumerate(('A', 'C', 'B', 'D'))}
    x = np.array([features[token] for token in sequence])
    # Each noninitial row has one visible predecessor: attention weight = 1.
    previous_mask = np.eye(len(x), k=-1)
    copied = previous_mask @ x[:, :2]
    records = x.copy()
    records[:, :2] += copied
    # Only completed B/D records take part in the second-stage read.
    indices = [i for i, token in enumerate(sequence[:-1]) if token in ('B', 'D')]
    completed = records[indices]
    return completed[:, :2], completed[:, 2:]


def icl_read(query=0, swap_values=False):
    last_token = ('A', 'C')[query]
    sequence = ('A', 'D', 'C', 'B', last_token) if swap_values else ('A', 'B', 'C', 'D', last_token)
    k, v = icl_records(sequence)
    q = np.eye(2)[query] * np.sqrt(2) * np.log(9)
    weights = softmax(q @ k.T / np.sqrt(2))
    context = weights @ v
    return weights, context, softmax(context * 5)

def policy_step():
    chosen=np.array([0,1,0,2]);advantages=np.array([1.,-1.,1.,-1.])
    z=np.zeros(3);p=softmax(z)
    gradients=advantages[:,None]*(p-np.eye(3)[chosen])
    gradient=gradients.mean(axis=0);updated=z-.2*gradient
    return gradient,updated,softmax(updated)

def run_checks():
    k, v = icl_records(('A', 'B', 'C', 'D', 'A'))
    swapped_k, swapped_v = icl_records(('A', 'D', 'C', 'B', 'A'))
    assert np.array_equal(k, np.eye(2)) and np.array_equal(v, np.eye(2))
    assert np.array_equal(k, swapped_k) and np.array_equal(swapped_v, v[::-1])
    a,c,p=icl_read();assert np.allclose(a,[.9,.1]) and np.allclose(c,[.9,.1])
    assert p.argmax()==0 and icl_read(1)[2].argmax()==1
    assert icl_read(swap_values=True)[2].argmax()==1
    assert np.allclose(softmax(np.zeros(2))@np.eye(2),[.5,.5])
    g,z,new=policy_step();assert np.allclose(g,[-.5,.25,.25]) and np.allclose(z,[.1,-.05,-.05])
    # Signed loss finite differences, with sampled actions and advantages fixed.
    acts=np.array([0,1,0,2]);adv=np.array([1.,-1.,1.,-1.])
    def loss(logits):return -np.mean(adv*np.log(softmax(logits)[acts]))
    for i in range(3):
        delta=np.eye(3)[i]*1e-6
        assert abs((loss(delta)-loss(-delta))/2e-6-g[i])<1e-9
    print(f'ICL record weights: {a.tolist()}; copied-token probability {p[0]:.6f}')
    print(f'Policy logit gradient: {g.tolist()}; logits {z.tolist()}; rewarded-token probability {new[0]:.6f}')
    return a,c,p,g,z,new
if __name__=='__main__':run_checks()
