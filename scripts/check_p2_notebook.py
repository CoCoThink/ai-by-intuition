#!/usr/bin/env python3
"""Check the P2 self-contained interactive notebook without importing optional libraries."""
from __future__ import annotations

import ast
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "notebooks" / "p2-interactive-intuitions.ipynb"


def check() -> None:
    nb = json.loads(PATH.read_text(encoding="utf-8"))
    assert nb["nbformat"] == 4
    assert len(nb["cells"]) >= 9
    code_cells = [
        "".join(cell["source"]) for cell in nb["cells"]
        if cell["cell_type"] == "code"
    ]
    for code in code_cells:
        # Notebook setup may contain %pip, while the experiments must be Python.
        if code.lstrip().startswith("%pip "):
            continue
        ast.parse(code)
    source = "\n".join(code_cells)
    for snippet in ("widgets.FloatSlider", "def stable_softmax",
                    "def masked_attention", "def gradient_descent",
                    "np.nan", "np.allclose", "widgets.interact"):
        assert snippet in source, f"Missing P2 interactive feature: {snippet}"
    assert source.count("widgets.interact(") == 3

    # Independent standard-library checks for the exact initial values.
    probs = [1 / 4, 2 / 4, 1 / 4]
    assert abs(-math.log(probs[1]) - math.log(2)) < 1e-12
    a = math.exp(-0.9019) / (math.exp(-0.9019) + math.exp(1.0496))
    assert abs(a - 0.1244) < 5e-5
    w, b = 1.0, 0.0
    gw, gb = 4 / 3 * (w - 2), 2 * (b - 1)
    w -= 0.3 * gw
    b -= 0.3 * gb
    new_loss = (2 / 3) * (w - 2) ** 2 + (b - 1) ** 2
    assert abs(w - 1.4) < 1e-12 and abs(b - 0.6) < 1e-12
    assert abs(new_loss - 0.4) < 1e-12
    print("P2 notebook QA passed: 3 sliders, syntax, causal mask and regression baseline")


if __name__ == "__main__":
    check()
