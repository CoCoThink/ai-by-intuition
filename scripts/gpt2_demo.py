#!/usr/bin/env python3
"""Reproducible GPT-2 experiment.

Default smoke: standard-library-only mathematics; no network or model download.
--real: load pinned openai-community/gpt2 checkpoint and inspect true tokens,
next-token probabilities at two temperatures, and optional first-head attention.
Model revision is pinned; runtime package versions are printed for provenance.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

MODEL = "openai-community/gpt2"
REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"
VOCAB = 50257


def probabilities(logits: list[float], temperature: float) -> list[float]:
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    scaled = [v / temperature for v in logits]
    m = max(scaled)
    exps = [math.exp(v - m) for v in scaled]
    return [value / sum(exps) for value in exps]


def smoke() -> None:
    assert math.isclose(math.log(VOCAB), 10.824905119, abs_tol=1e-6)
    scores = [0.0, 1.0, 2.0]
    hot = probabilities(scores, 2.0)
    cold = probabilities(scores, 0.5)
    assert all(math.isclose(sum(x), 1.0, abs_tol=1e-12) for x in (hot, cold))
    assert cold[-1] > hot[-1]
    print(f"Offline smoke passed: ln({VOCAB})={math.log(VOCAB):.6f}; "
          f"highest-p(T=0.5)={cold[-1]:.4f}, highest-p(T=2)={hot[-1]:.4f}")


def run_real(prompt: str, heatmap: Path | None, local_files_only: bool) -> None:
    try:
        import torch
        import transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise SystemExit(
            "Install compatible torch and transformers before --real; "
            "the offline smoke does not need them."
        ) from exc

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL, revision=REVISION, local_files_only=local_files_only
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=REVISION, local_files_only=local_files_only,
        attn_implementation="eager"
    )
    model.eval()
    ids = tokenizer(prompt, return_tensors="pt")["input_ids"]
    if ids.shape[1] < 2:
        raise SystemExit("Use a prompt of at least two tokens.")
    with torch.no_grad():
        outputs = model(input_ids=ids, use_cache=False,
                        output_attentions=heatmap is not None)
    last = outputs.logits[0, -1, :]
    assert last.ndim == 1 and last.shape[0] == VOCAB
    print(f"Model={MODEL}@{REVISION}; torch={torch.__version__}; "
          f"transformers={transformers.__version__}")
    print("Token count:", ids.shape[1])
    print("Token IDs:", ids[0].tolist())
    print("Tokenizer pieces:", tokenizer.convert_ids_to_tokens(ids[0].tolist()))
    print("Next token logits shape:", tuple(outputs.logits.shape))
    good = torch.isfinite(last)
    finite_count = int(good.sum())
    print(f"Finite logits: {finite_count}/{VOCAB}")
    if finite_count:
        good_values = last[good]
        print(f"Finite logit range: "
              f"[{float(good_values.min()):.5g}, {float(good_values.max()):.5g}]")
    if finite_count != VOCAB:
        bad = (~good).nonzero().flatten()[:8].tolist()
        raise RuntimeError(f"Nonfinite GPT-2 logits at vocabulary indices {bad}")
    for temperature in (0.7, 1.0, 1.5):
        # Sum across a 50,257-way distribution in float64 to avoid float32
        # accumulation noise (observed 1.00001204 at T=0.7 on CPU).
        distribution = torch.softmax(last.double() / temperature, dim=-1)
        mass = float(distribution.sum())
        print(f"T={temperature}: probability sum={mass:.8f}")
        if not math.isfinite(mass) or abs(mass - 1.0) >= 1e-5:
            raise RuntimeError(f"Invalid softmax probability sum at T={temperature}: {mass}")
        values, indices = torch.topk(distribution, k=5)
        choices = [(int(i), repr(tokenizer.decode([int(i)])),
                    round(float(v), 5))
                   for v, i in zip(values.tolist(), indices.tolist())]
        print(f"T={temperature}: top-5 token/probabilities={choices}")
    if heatmap is not None:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise SystemExit("Install matplotlib to save --heatmap.") from exc
        attentions = outputs.attentions
        if not attentions or attentions[0] is None:
            raise RuntimeError("No attention weights; ensure eager attention backend.")
        weights = attentions[0][0, 0].detach().float().cpu().numpy()
        n = ids.shape[1]
        assert weights.shape == (n, n), weights.shape
        import numpy as np
        masked_future = np.triu(weights, k=1)
        max_future = float(np.max(np.abs(masked_future)))
        assert max_future < 1e-6, max_future
        assert np.allclose(weights.sum(axis=-1), 1.0, atol=1e-5)
        print(f"Causal attention first-head upper triangle max={max_future:.8g}")
        fig, ax = plt.subplots(figsize=(6, 5))
        picture = ax.imshow(weights, vmin=0, vmax=1, cmap="gray_r")
        fig.colorbar(picture, ax=ax, label="Attention weight")
        ax.set(xlabel="Key position", ylabel="Query position",
               title="GPT-2 first layer, head 0 (causal)")
        fig.tight_layout()
        heatmap.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(heatmap, dpi=160)
        plt.close(fig)
        print("Saved attention heatmap:", heatmap)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real", action="store_true",
                        help="explicitly load pinned public GPT-2 weights")
    parser.add_argument("--local-files-only", action="store_true",
                        help="require model/tokenizer already cached (with --real)")
    parser.add_argument("--prompt", default="The capital of France is",
                        help="English prompt for the historical English GPT-2")
    parser.add_argument("--heatmap", type=Path,
                        help="save first-layer head-0 heatmap, requires --real")
    args = parser.parse_args()
    smoke()
    if args.heatmap and not args.real:
        parser.error("--heatmap requires --real")
    if args.real:
        run_real(args.prompt, args.heatmap, args.local_files_only)


if __name__ == "__main__":
    main()
