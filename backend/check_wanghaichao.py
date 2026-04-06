# -*- coding: utf-8 -*-
import json

with open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 望海潮 id=36
key = '36'
if key in data:
    print(f"望海潮 (id=36) 数据:")
    print(json.dumps(data[key], ensure_ascii=False, indent=2))
else:
    print(f"id=36 不在数据中")
    # 搜索望海潮
    for k, v in data.items():
        name = v.get('name', '')
        if '望海潮' in name:
            print(f"找到: key={k}, name={name}")
