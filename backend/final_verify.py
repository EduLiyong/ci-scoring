import sys
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')

print("=== 1. cipai_data.py 验证 ===")
try:
    exec(open('d:/MyClaw/ci-scoring/backend/cipai_data.py', encoding='utf-8').read())
    db = CIPAI_DATABASE
    print('总词牌数:', len(db))
    for c in db:
        if c.get('id') in [36, 50]:
            print('ID %d: %s (dynasty=%s)' % (c['id'], c['name'], c.get('dynasty')))
            for p in c.get('patterns', []):
                sc = sum(s.get('chars', 0) for s in p.get('sentences', []))
                print('  %s: %d句, total_chars=%d, 句子字数合计=%d' % (
                    p.get('name'), len(p.get('sentences', [])), p.get('total_chars'), sc))
except Exception as e:
    print('ERROR:', e)

print()
print("=== 2. representative_works.json 验证 ===")
import json
rep = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'r', encoding='utf-8'))
print('总代表作词牌数:', len(rep))
for k in ['36', '50']:
    v = rep.get(k, {})
    print('ID %s (%s): main=%d部, variant=%d组' % (k, v.get('name', '?'), len(v.get('main', [])), len(v.get('variant', []))))
    for w in v.get('main', []):
        t = str(w.get('text', ''))
        print('  [%s] %s | %s | %d字 | 首句: %s' % (
            w.get('dynasty', '?'), w.get('author', '?'), w.get('title', '?'), len(t), t[:30].replace('\n', ' ')))

print()
print("=== 3. 数据库一致性检查 ===")
db_ids = set(c.get('id') for c in CIPAI_DATABASE)
rep_ids = set(int(k) for k in rep.keys())
print('cipai_data IDs:', sorted(db_ids))
print('representative_works.json keys:', sorted(rep_ids))
print('一致:', db_ids == rep_ids)

print()
print("=== 4. 检查无其他重复词牌 ===")
names = {}
for c in CIPAI_DATABASE:
    n = c.get('name', '')
    names.setdefault(n, []).append(c.get('id'))
dups = {k: v for k, v in names.items() if len(v) > 1}
if dups:
    print('重复:', dups)
else:
    print('无重复词牌')

print()
print('=== 全部验证完成 ===')