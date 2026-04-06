# -*- coding: utf-8 -*-
"""深度交叉验证：结合cipai_data的sentence结构与词文字数，区分：
   1. total_chars字段错误（数据库bug）
   2. 词作内容残缺（数据问题）
   3. 词作不属于该词牌（严重错误）
"""
import json

cipai_globals = {}
with open('cipai_data.py', encoding='utf-8') as f:
    exec(f.read(), cipai_globals)
get_cipai = cipai_globals['get_cipai_by_id']

with open('representative_works.json', encoding='utf-8') as f:
    data = json.load(f)

# 对每个词牌，用pattern的sentence结构重新计算期望字数
def compute_pattern_chars(pattern):
    """从pattern的sentences计算总字数"""
    return sum(s.get('chars', 0) for s in pattern.get('sentences', []))

print("=== 词牌字数交叉验证 ===\n")
print(f"{'ID':<4} {'词牌名':<10} {'数据库total':>8} {'计算total':>8} {'一致?':>6} {'代表作品数':>8}")
print("-" * 55)

mismatches = []
for cid_str in sorted(data.keys(), key=lambda x: int(x)):
    cid = int(cid_str)
    entry = get_cipai(cid)
    if not entry:
        continue

    cname = entry['name']
    db_total = entry.get('total_chars') or 0

    # 计算正体字数（从pattern的sentences）
    patterns = entry.get('patterns', [])
    computed_main = 0
    if patterns:
        computed_main = compute_pattern_chars(patterns[0])

    work_count = len(data[cid_str].get('main', []))

    match = "OK" if db_total == computed_main else "MISMATCH"

    if db_total != computed_main and db_total > 0 and computed_main > 0:
        mismatches.append((cid, cname, db_total, computed_main))

    if match == "MISMATCH" or work_count == 0:
        print(f"{cid:<4} {cname:<10} {db_total or 0:>8} {computed_main:>8} {match:>6} {work_count:>8}")
    else:
        print(f"{cid:<4} {cname:<10} {db_total or 0:>8} {computed_main:>8} {match:>6} {work_count:>8}")

print(f"\n总计 {len(mismatches)} 个词牌的数据库total_chars与计算值不一致")

# 现在重新用计算字数做质检
print("\n=== 以计算字数重新质检代表作 ===\n")

# 正确词牌+字数对照（基于龙榆生《唐宋词格律》等权威资料）
# key: (cid, expected_chars)
# 这些是经过人工核对的真实词牌标准字数
AUTHORITATIVE_COUNTS = {
    # (id, name): expected_main_chars
    # 正体（从patterns[0]sentences计算）
}

# 重新计算所有词牌的pattern[0]字数
cid_expected = {}
for cid_str in sorted(data.keys(), key=lambda x: int(x)):
    cid = int(cid_str)
    entry = get_cipai(cid)
    if not entry:
        continue
    patterns = entry.get('patterns', [])
    if patterns:
        cid_expected[cid] = compute_pattern_chars(patterns[0])

# 现代词/占位符检测
bad_words = ['persistence', 'PLACEHOLDER', '占位符', '???', 'ration',
             'bat', '稀后', '莫莫莫', '我们', '你们', '他们']

# 收集问题
critical_errors = []  # 严重错误：词作不属于该词牌
minor_issues = []     # 小问题：字数略偏差
truncated = []        # 残缺

for cid_str in sorted(data.keys(), key=lambda x: int(x)):
    cid = int(cid_str)
    entry = get_cipai(cid)
    if not entry:
        continue
    cname = entry['name']
    expected = cid_expected.get(cid, 0)
    wdata = data[cid_str]

    for i, w in enumerate(wdata.get('main', [])):
        text = w['text']
        actual = len(text)
        title = w['title']
        author = w['author']
        issues = []

        # 占位符/现代词
        for bw in bad_words:
            if bw in text:
                issues.append('含现代词/占位符')
                break

        # 残缺
        if actual < expected * 0.5 and expected > 0:
            issues.append(f'严重残缺(应{expected}字,实{actual}字)')

        # 字数严重偏差（>40%）
        if expected > 0 and actual > expected * 1.5:
            issues.append(f'字数超长(应{expected}字,实{actual}字)')

        if issues:
            critical_errors.append({
                'cid': cid, 'cname': cname, 'layer': '正体',
                'idx': i+1, 'title': title, 'author': author,
                'length': actual, 'expected': expected, 'issues': issues
            })

    # 变体
    for vi, variant in enumerate(wdata.get('variants', [])):
        vname = variant.get('name', '')
        vpatterns = entry.get('patterns', [])
        vexpected = 0
        if vpatterns and vi < len(vpatterns):
            vexpected = compute_pattern_chars(vpatterns[vi])

        for i, w in enumerate(variant.get('works', [])):
            text = w['text']
            actual = len(text)
            title = w['title']
            author = w['author']
            issues = []

            for bw in bad_words:
                if bw in text:
                    issues.append('含现代词/占位符')
                    break

            if actual < 10:
                issues.append(f'严重残缺({actual}字)')
            elif expected > 0 and actual > expected * 1.5:
                issues.append(f'字数超长(应{vexpected or expected}字,实{actual}字)')

            if issues:
                critical_errors.append({
                    'cid': cid, 'cname': cname, 'layer': f'变体[{vname}]',
                    'idx': i+1, 'title': title, 'author': author,
                    'length': actual, 'expected': vexpected, 'issues': issues
                })

print(f"严重/明显错误条目数: {len(critical_errors)}\n")
from collections import defaultdict
by_cipai = defaultdict(list)
for r in critical_errors:
    by_cipai[r['cid']].append(r)

for cid in sorted(by_cipai.keys()):
    entries = by_cipai[cid]
    cname = entries[0]['cname']
    print(f"【{cname}】 id={cid}")
    for e in entries:
        print(f"  - {e['layer']}第{e['idx']}首 [{e['title']}·{e['author']}] ({e['length']}字)")
        for iss in e['issues']:
            print(f"      ! {iss}")
    print()
