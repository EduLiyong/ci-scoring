# -*- coding: utf-8 -*-
"""重新生成 representative_works.json - 100个词牌"""
import json
import sys
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
from cipai_data import CIPAI_DATABASE

# 读取现有的代表作数据
try:
    with open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'r', encoding='utf-8') as f:
        existing_rep = json.load(f)
    print(f"现有代表作词牌数: {len(existing_rep)}")
except:
    existing_rep = {}
    print("没有现有代表作数据")

# 获取当前100个词牌的ID列表
current_ids = set(c['id'] for c in CIPAI_DATABASE)
print(f"当前词牌数: {len(current_ids)}")

# 过滤现有的代表作，只保留当前词牌有的
filtered_rep = {}
for cid_str, data in existing_rep.items():
    cid = int(cid_str)
    if cid in current_ids:
        filtered_rep[cid_str] = data

print(f"过滤后代表作词牌数: {len(filtered_rep)}")

# 如果有缺失的词牌，生成占位符
missing_ids = current_ids - set(int(k) for k in filtered_rep.keys())
print(f"缺失词牌数: {len(missing_ids)}")

for cid in missing_ids:
    # 找到词牌信息
    cipai = next((c for c in CIPAI_DATABASE if c['id'] == cid), None)
    if cipai:
        chars = cipai.get('chars', 0)
        desc = cipai.get('desc', '')
        filtered_rep[str(cid)] = {
            'main': [
                {
                    'author': '历代名家',
                    'title': f'{cipai["name"]}·经典',
                    'text': f'此词为{cipai["name"]}正体，{chars}字。{desc}。',
                    'dynasty': cipai.get('dynasty', '宋')
                }
            ],
            'variants': []
        }

print(f"最终代表作词牌数: {len(filtered_rep)}")

# 保存
with open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_rep, f, ensure_ascii=False, indent=2)

print("已保存 representative_works.json")
