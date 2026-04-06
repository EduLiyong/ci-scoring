"""精确汉字统计 - 仅计算汉字，去除所有标点符号"""
import json
import re

def count_chinese_chars(text):
    """只统计汉字数量，去除所有标点、空格、换行"""
    # 去除所有非汉字字符（标点、数字、英文、空格等）
    chinese_only = re.sub(r'[^\u4e00-\u9fff]', '', text)
    return len(chinese_only)

# 测试
tests = [
    ('明月几时有', '苏轼'),
    ('大江东去', '苏轼'),
    ('平林漠漠烟如织', '李白'),
]

print("=== 纯汉字计数测试 ===")
for title, author in tests:
    print("  《%s》%s: %d字" % (title, author, count_chinese_chars(title)))

print()

# 加载数据
with open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'r', encoding='utf-8') as f:
    rep = json.load(f)

import sys, importlib.util
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
spec = importlib.util.spec_from_file_location('cipai_data', 'd:/MyClaw/ci-scoring/backend/cipai_data.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
db = mod.CIPAI_DATABASE

cipai_chars = {}
for c in db:
    cid = c['id']
    if c.get('patterns') and len(c['patterns']) > 0:
        zhengti = c['patterns'][0]
        for p in c['patterns']:
            if '正体' in p.get('name', ''):
                zhengti = p
                break
        cipai_chars[cid] = zhengti.get('total_chars', 0)

cipai_names = {c['id']: c['name'] for c in db}

issues = []
for cid_str in sorted(rep.keys(), key=lambda x: int(x)):
    cid = int(cid_str)
    name = cipai_names.get(cid, '?')
    expected = cipai_chars.get(cid, 0)

    for work in rep[cid_str].get('main', []):
        text = work.get('text', '')
        title = work.get('title', '')
        author = work.get('author', '')
        actual = count_chinese_chars(text)
        if actual != expected:
            issues.append('ID %d [%s《%s》]: db=%d, 汉字=%d' % (cid, author, title, expected, actual))

    for variant in rep[cid_str].get('variants', []):
        vname = variant.get('name', '?')
        for work in variant.get('works', []):
            text = work.get('text', '')
            title = work.get('title', '')
            author = work.get('author', '')
            actual = count_chinese_chars(text)
            if actual != expected:
                issues.append('ID %s 变体[%s] [%s《%s》]: db=%d, 汉字=%d' % (
                    cid_str, vname, author, title, expected, actual))

print('总不匹配数: %d' % len(issues))
print()
for iss in issues:
    print(iss)

if not issues:
    print('[ALL OK] 所有词牌代表作汉字字数与数据库完全匹配！')
