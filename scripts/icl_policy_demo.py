#!/usr/bin/env python3
"""Reproduce the book's two-record ICL read and frozen-advantage logit update."""
import numpy as np

def softmax(z):
    e=np.exp(z-np.max(z,axis=-1,keepdims=True));return e/e.sum(axis=-1,keepdims=True)

def icl_read(query=0, swap_values=False):
    # Keys carry the predecessor identity, already copied to each completed record.
    q=np.eye(2)[query]*np.sqrt(2)*np.log(9)
    k=np.eye(2);v=np.eye(2)[::-1] if swap_values else np.eye(2)
    weights=softmax(q@k.T/np.sqrt(2));context=weights@v
    return weights,context,softmax(context*5)

def policy_step():
    chosen=np.array([0,1,0,2]);advantages=np.array([1.,-1.,1.,-1.])
    z=np.zeros(3);p=softmax(z)
    gradients=advantages[:,None]*(p-np.eye(3)[chosen])
    gradient=gradients.mean(axis=0);updated=z-.2*gradient
    return gradient,updated,softmax(updated)

def run_checks():
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
