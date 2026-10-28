#!/usr/bin/env python3
"""Autograd reproduction of the shared 3-token teaching fixture; needs torch, numpy."""
import math
import torch
import numpy as np
from teaching_reference import EPS, IDS, LR, TARGETS, parameters, forward as reference_forward, backward as reference_backward

torch.set_default_dtype(torch.float64)
weights = {k: torch.tensor(v, requires_grad=True)
           for k, v in parameters().items()}
ids = torch.tensor(IDS)
targets = torch.tensor(TARGETS)

def norm(x):
    centered = x - x.mean(dim=-1, keepdim=True)
    return centered / torch.sqrt(centered.square().mean(dim=-1, keepdim=True) + EPS)

def forward():
    x = weights["E"][ids - 1] + weights["P"]
    u = norm(x)
    q, k, v = (u @ weights[name] for name in ("Wq", "Wk", "Wv"))
    score = (q @ k.T) / math.sqrt(q.shape[1])
    forbidden = torch.triu(torch.ones_like(score, dtype=torch.bool), diagonal=1)
    attention = torch.softmax(score.masked_fill(forbidden, float("-inf")), dim=-1)
    residual = x + (attention @ v) @ weights["Wo"]
    hidden = residual + torch.relu(norm(residual) @ weights["Wup"]) @ weights["Wdown"]
    logits = hidden @ weights["Wout"]
    return torch.nn.functional.cross_entropy(logits, targets - 1), logits

loss_before, z_before = forward()
loss_before.backward()
reference_weights = parameters()
reference_gradients = reference_backward(reference_weights, reference_forward(reference_weights))
for name, value in weights.items():
    np.testing.assert_allclose(value.grad.detach().numpy(), reference_gradients[name], atol=1e-10, rtol=1e-8)

with torch.no_grad():
    for value in weights.values():
        value -= LR * value.grad
        value.grad.zero_()
loss_after, z_after = forward()

assert abs(loss_before.item() - 1.7984303789332916) < 1e-8
assert abs(loss_after.item() - 1.6113771577442104) < 1e-8
assert z_after.shape == (3, 5)
assert sum(value.numel() for value in weights.values()) == 99
print("Loss:", f"{loss_before.item():.6f}", "->", f"{loss_after.item():.6f}")
print("Shape:", tuple(z_after.shape), "Parameters: 99")

print("Gradients: all 99 parameters match NumPy (CPU float64, atol=1e-10, rtol=1e-8)")
