import sys
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
from cipai_data import CIPAI_DATABASE
import json

rep = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'r', encoding='utf-8'))

print("=== CIPAI_DATABASE ===")
for c in CIPAI_DATABASE:
    if c.get('id') in [36, 50]:
        print(f'ID {c.get("id")}: {c.get("name")}')
        for p in c.get('patterns', []):
            sc = sum(s.get('chars', 0) for s in p.get('sentences', []))
            print(f'  {p.get("name")}: {len(p.get("sentences", []))}句, 总字数={sc}')

print("\n=== 代表作 ===")
for k in ['36', '50']:
    v = rep.get(k, {})
    print(f'ID {k} ({v.get("name", "?")}): main={len(v.get("main", []))}, variant={len(v.get("variant", []))}')
    for w in v.get('main', []):
        t = str(w.get('text', ''))
        print(f'  {w.get("title", "?")} by {w.get("author", "?")} | {len(t)}chars | 首句: {t[:30]}')