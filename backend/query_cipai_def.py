# -*- coding: utf-8 -*-
"""查询6个严重错误词牌的正确代表作"""
import json, importlib.util, sys

# 加载cipai_data
spec = importlib.util.spec_from_file_location("cipai_data", "cipai_data.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def get_entry(cid):
    return mod.get_cipai_by_id(cid)

# 查询6个词牌的定义
for cid in [17, 44, 91, 80, 76, 78]:
    entry = get_entry(cid)
    if not entry:
        print('id=%d not found' % cid)
        continue
    name = entry['name']
    patterns = entry.get('patterns', [])
    desc = entry.get('description', '')
    total = entry.get('total_chars', 0)
    print('=== id=%d %s (total_chars=%s) ===' % (cid, name, total))
    print('描述: %s' % desc[:80])
    for pi, p in enumerate(patterns[:2]):
        tone = p.get('tone', '')
        chars = p.get('chars', 0)
        print('  pattern[%d]: %s句 %s字' % (pi, len(tone.split('/')), chars))
        print('    格律: %s' % tone[:100])
    print()
