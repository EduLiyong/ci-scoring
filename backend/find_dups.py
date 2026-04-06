# -*- coding: utf-8 -*-
import re

with open('d:/MyClaw/ci-scoring/backend/cipai_data.backup.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到所有词牌的ID
entry_ids = []
for i, line in enumerate(lines):
    if "'id':" in line:
        m = re.search(r"'id': (\d+),", line)
        if m:
            cid = int(m.group(1))
            entry_ids.append(cid)

print(f'总ID出现次数: {len(entry_ids)}')
print(f'唯一ID数: {len(set(entry_ids))}')
print(f'ID范围: {min(entry_ids)} - {max(entry_ids)}')

# 检查大于60的ID
large_ids = [x for x in entry_ids if x > 60]
print(f'大于60的ID: {sorted(set(large_ids))}')

from collections import Counter
counter = Counter(entry_ids)
dups = {k: v for k, v in counter.items() if v > 1}
print(f'重复ID: {dups}')
