import json
d = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'r', encoding='utf-8'))
# 查找唐多令
for k, v in d.items():
    name = v.get('name', '')
    if '唐多令' in name:
        print(f"ID: {k}, name: {name}")
        for i, w in enumerate(v.get('main', [])):
            print(f"  [{i}] {w.get('title','?')} - {w.get('author','?')} ({w.get('dynasty','?')})")
            print(f"      词文: {w.get('text','?')[:50]}...")
        print()
        break
else:
    # 也搜索id
    for k, v in d.items():
        if v.get('cipai_id') == '唐多令' or v.get('name') == '唐多令':
            print(f"Found: {k}", v)
