#!/usr/bin/env python3
"""Deterministic multimodal bridge: 4 image patch rows + 2 text rows -> 6 rows.

The "vision encoder" is identity here; this is a SHAPE illustration, not a
trained ViT or a claim about any deployed multimodal model.
"""
from __future__ import annotations


def multiply(a, b):
    assert all(len(row) == len(a[0]) for row in a)
    assert all(len(row) == len(b[0]) for row in b)
    assert len(a[0]) == len(b)
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def shape(rows):
    return (len(rows), len(rows[0]))


def main():
    patch_pixels = [
        [1, 1, 1, 0],
        [0, 0, 0, 1],
        [0, 1, 0, 0],
        [1, 1, 0, 1],
    ]
    patch_projection = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [0.5, 0.5, 0],
    ]
    vision_output = multiply(patch_pixels, patch_projection)
    assert shape(vision_output) == (4, 3)
    assert vision_output == [[1, 1, 1], [.5, .5, 0], [0, 1, 0], [1.5, 1.5, 0]]

    bridge = [
        [1, 0, 0, 1],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
    ]
    image_prefix = multiply(vision_output, bridge)
    assert shape(image_prefix) == (4, 4)
    assert image_prefix[0] == [1, 1, 1, 1]
    text_embedding = [[0, 0, 1, 1], [1, 0, 0, 0]]
    llm_inputs = image_prefix + text_embedding
    assert shape(llm_inputs) == (6, 4)

    # Last (text) query sees all preceding image prefix rows under causal mask.
    permitted_keys_for_last_query = list(range(len(llm_inputs)))
    assert permitted_keys_for_last_query == [0, 1, 2, 3, 4, 5]
    print("Patch pixels (4,4) -> vision features (4,3) "
          "-> projected image prefix (4,4)")
    print("Image prefix (4,4) + text embeddings (2,4) -> LLM input (6,4)")
    print("First projected image row:", image_prefix[0])
    print("Final text query can see positions:", permitted_keys_for_last_query)
    print("Vision bridge QA passed; no model weights or image generation used.")


if __name__ == "__main__":
    main()
