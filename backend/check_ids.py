import sys
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
from cipai_data import CIPAI_DATABASE

# 找到ID 36和50的位置和结构
for i, c in enumerate(CIPAI_DATABASE):
    if c.get('id') in [36, 50]:
        print(f'index={i}, id={c.get("id")}, name={c.get("name")}, total_chars={c.get("total_chars")}')
        print(f'  sentences count: {len(c.get("sentences", []))}')
        print(f'  keys: {list(c.keys())}')
        # 打印完整结构
        import json
        print(json.dumps(c, ensure_ascii=False, indent=2))
        print()