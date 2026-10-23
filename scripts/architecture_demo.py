#!/usr/bin/env python3
"""Two separate architecture hand calculations: illustrative MLA cache and sliding window."""
from __future__ import annotations


def mask(n: int, window: int):
    assert 1 <= window <= n
    return [[int(j <= i and j >= max(0, i - window + 1))
             for j in range(n)] for i in range(n)]


def main():
    # Hypothetical cache accounting, one layer; not a specific published MLA.
    t, heads, kv_heads, width, latent, rope = 8, 4, 2, 2, 3, 2
    mha = 2 * t * heads * width   # K and V for every head.
    gqa = 2 * t * kv_heads * width
    mla_toy = t * (latent + rope)  # Shared latent plus positional cache.
    assert (mha, gqa, mla_toy) == (128, 64, 40)
    print(f"Toy cache elements per layer: MHA={mha}, GQA={gqa}, "
          f"MLA-like={mla_toy} (hypothetical)")

    m = mask(n=5, window=3)
    assert m == [
        [1, 0, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [1, 1, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 1, 1],
    ]
    allowed = sum(map(sum, m))
    assert allowed == 12
    print("5 x 5 causal sliding-window mask (window=3):")
    for row in m:
        print(" ".join(str(value) for value in row))
    print("Allowed pairs:", allowed, "vs full causal:", 5 * 6 // 2)
    print("Architecture arithmetic QA passed.")


if __name__ == "__main__":
    main()
