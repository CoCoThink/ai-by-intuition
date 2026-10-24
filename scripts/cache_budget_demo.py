#!/usr/bin/env python3
"""Cache data bytes (not element counts), using pinned Qwen2.5 metadata."""
import json
from pathlib import Path


def kv_bytes(layers, heads, width, positions, bytes_per_element, batch=1):
    return 2 * layers * heads * width * positions * bytes_per_element * batch


def run_checks():
    configs=Path(__file__).with_name('model_configs')
    cfg=next(json.loads(p.read_text())['config'] for p in configs.glob('*.json')
             if json.loads(p.read_text())['config']['model_type']=='qwen2')
    width=cfg['hidden_size']//cfg['num_attention_heads']
    per_token=kv_bytes(cfg['num_hidden_layers'],cfg['num_key_value_heads'],width,1,2)
    full=per_token*32768
    mha=kv_bytes(cfg['num_hidden_layers'],cfg['num_attention_heads'],width,32768,2)
    assert width==64 and per_token==12288 and full==402653184
    assert mha==2818572288 and mha/full==7
    assert kv_bytes(2,2,8,10,2)==1280
    assert kv_bytes(2,2,8,10,1)==640  # the earlier erroneous byte answer was an element count
    assert kv_bytes(24,2,64,32768,2,batch=3)==3*full
    print(f'KV bytes: C4-41=1280; Qwen/token={per_token}; 32K={full}; MHA={mha} (7x)')
    return per_token,full,mha


if __name__=='__main__': run_checks()
