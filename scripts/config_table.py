#!/usr/bin/env python3
"""Offline comparison from versioned public config.json snapshots.

Default: reads verified field excerpts under scripts/model_configs/*.json, no network.
--verify-online: downloads config.json at pinned commits and checks stored fields.
This reads CONFIG METADATA, not model weights or benchmark results.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.request import urlopen

SNAPSHOTS = Path(__file__).resolve().parent / "model_configs"


def load_rows():
    rows = []
    for path in sorted(SNAPSHOTS.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        cfg = obj["config"]
        if cfg["model_type"] == "gpt2":
            row = ("GPT-2 small", cfg["n_embd"], cfg["n_layer"],
                   cfg["n_head"], cfg["n_head"], "learned abs. positions",
                   "LayerNorm", cfg["activation_function"],
                   "MHA", "not specified")
        elif cfg["model_type"] == "qwen2":
            assert cfg["num_attention_heads"] % cfg["num_key_value_heads"] == 0
            row = ("Qwen2.5-0.5B", cfg["hidden_size"], cfg["num_hidden_layers"],
                   cfg["num_attention_heads"], cfg["num_key_value_heads"],
                   "RoPE", "RMSNorm", cfg["hidden_act"] + " (gate in model)",
                   "GQA", "disabled" if not cfg["use_sliding_window"] else "enabled")
        else:
            raise ValueError(f"Unexpected model_type in {path}: {cfg['model_type']}")
        rows.append((obj, row))
    if len(rows) != 2:
        raise AssertionError("Exactly two checked source snapshots are expected")
    return rows


def verify_online(obj) -> None:
    model, revision = obj["model_id"], obj["revision"]
    url = f"https://huggingface.co/{model}/resolve/{revision}/config.json"
    with urlopen(url, timeout=20) as response:  # Explicit opt-in.
        cfg = json.load(response)
    for field, expected in obj["config"].items():
        actual = cfg.get(field)
        if actual != expected:
            raise AssertionError((model, field, expected, actual))
    print(f"Verified {model}@{revision[:12]} against public config.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-online", action="store_true",
                        help="check pinned public config files; requires network")
    args = parser.parse_args()
    rows = load_rows()
    print("model | d_model | layers | query_heads | kv_heads | position | norm | activation | attention | window")
    for obj, row in rows:
        print(" | ".join(str(x) for x in row))
        print("  source:", obj["source"])
        if args.verify_online:
            verify_online(obj)
    by_name = {row[0]: row for _, row in rows}
    assert by_name["GPT-2 small"][1:5] == (768, 12, 12, 12)
    assert by_name["Qwen2.5-0.5B"][1:5] == (896, 24, 14, 2)
    assert by_name["Qwen2.5-0.5B"][-1] == "disabled"
    print("Offline config comparison passed; no model weights downloaded.")


if __name__ == "__main__":
    main()
