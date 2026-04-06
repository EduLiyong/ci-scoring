"""统计总作品数和每个词牌的作品数"""
import json
import re

def zh(text):
    if not text:
        return 0
    return len(re.findall(r'[\u4e00-\u9fff]', text))

rep = json.load(open(r'd:/MyClaw/ci-scoring/backend/representative_works.json', encoding='utf-8'))

total = 0
for cid in sorted(rep.keys(), key=int):
    entry = rep[cid]
    main = entry.get('main', [])
    variants = entry.get('variants', [])
    for v in variants:
        if isinstance(v, dict) and 'works' in v:
            main_v = v['works']
        else:
            main_v = []
    m_count = len(main)
    v_count = sum(len(v.get('works', [])) if isinstance(v, dict) else 0 for v in variants)
    total += m_count
    if m_count < 3 or v_count == 0:
        print(f"id={cid}: {m_count}首 main, {v_count}首 variants")

print(f"\n总作品数: {total}")
